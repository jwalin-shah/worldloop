from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from worldloop.benchmark import generate_benchmark
from worldloop.typesafe_router import (
    heuristic_route,
    route_is_verified,
    typesafe_multi_route,
)
from worldloop.wandb_inference import wandb_inference_route
from worldloop.weave_integration import weave_status

try:
    import weave  # type: ignore
except ImportError:
    weave = None


def git_revision() -> str:
    explicit = os.getenv("WORLDLOOP_CODE_REVISION")
    if explicit:
        return explicit
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def evaluate_arm(case: Any, arm_name: str, mode: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    if arm_name == "deterministic":
        res = heuristic_route(case, mode=mode)
    elif arm_name == "typesafe":
        res = typesafe_multi_route(case, mode=mode)
    elif arm_name == "wandb_inference":
        res = wandb_inference_route(case, mode=mode)
    else:
        raise ValueError(f"Unknown arm: {arm_name}")
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    verified = route_is_verified(case, res)
    under_allocated = not verified and res.route != "ABSTAIN"
    unnecessary = verified and not set(res.recipe).issubset(set(case.repair_recipe))

    return {
        "arm": arm_name,
        "provider": res.provider,
        "model": res.model,
        "route": res.route,
        "recipe": list(res.recipe),
        "confidence": res.confidence,
        "probabilities": res.probabilities,
        "verified": verified,
        "under_allocated": under_allocated,
        "unnecessary": unnecessary,
        "latency_ms": latency_ms,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Three-Arm Latent Routing Evaluation (Deterministic vs. TypeSafe vs. W&B LLM)")
    parser.add_argument("--limit", type=int, default=None, help="Number of held-out cases to evaluate")
    parser.add_argument("--mode", default="latent", choices=["latent", "adversarial", "legacy"], help="Evaluation mode")
    parser.add_argument("--output", default="reports/three-arm-eval.json", help="Path for JSON output")
    parser.add_argument("--experiment", default="EXP-010-receipt-aware-frontier", help="Experiment identifier")
    args = parser.parse_args()

    dataset = generate_benchmark()
    cases = list(dataset.heldout)
    if args.limit is not None:
        cases = cases[: args.limit]

    print(f"=== WorldLoop Three-Arm Cognitive Frontier Evaluation ===")
    print(f"Dataset Snapshot: {dataset.snapshot_id}")
    print(f"Mode: {args.mode}")
    print(f"Cases Count: {len(cases)}")
    print(f"Experiment: {args.experiment}\n")

    # Check Weave status
    status = weave_status()
    weave_active = status["remote_tracing_ready"]
    if weave_active:
        assert weave is not None
        weave.init(
            status["project"],
            settings={"implicitly_patch_integrations": False},
            attributes={
                "experiment_id": args.experiment,
                "snapshot_id": dataset.snapshot_id,
                "mode": args.mode,
                "revision": git_revision(),
            },
        )
        print(f"Weave initialized: {status['project']}")
    else:
        print("Weave not active (offline mode or WANDB_API_KEY unset).")

    arms = ["deterministic", "typesafe", "wandb_inference"]
    case_results: list[dict[str, Any]] = []

    # Trace helper op if weave is active
    def trace_comparison(row_data: dict[str, Any]) -> dict[str, Any]:
        return row_data

    if weave_active and weave is not None:
        trace_comparison = weave.op()(trace_comparison)

    for case in cases:
        print(f"Evaluating Case {case.case_id}...")
        context_prose = (
            case.adversarial_context_prose
            if args.mode == "adversarial"
            else (case.context_prose if args.mode == "latent" else "")
        )
        row: dict[str, Any] = {
            "case_id": case.case_id,
            "question": case.question,
            "target_recipe": list(case.repair_recipe),
            "context_prose": context_prose,
            "arms": {},
        }
        for arm in arms:
            try:
                arm_res = evaluate_arm(case, arm, mode=args.mode)
            except Exception as exc:
                print(f"  [ERROR] Arm {arm} failed: {exc}")
                arm_res = {
                    "arm": arm,
                    "provider": arm,
                    "model": "error",
                    "route": "ERROR",
                    "recipe": [],
                    "confidence": 0.0,
                    "probabilities": {},
                    "verified": False,
                    "under_allocated": True,
                    "unnecessary": False,
                    "latency_ms": 0.0,
                    "error": str(exc),
                }
            row["arms"][arm] = arm_res
            print(f"  [{arm:15}] Route: {arm_res['route']:10} | Verified: {str(arm_res['verified']):5} | Latency: {arm_res['latency_ms']}ms | Conf: {arm_res['confidence']}")

        case_results.append(row)
        if weave_active:
            trace_comparison(row)
        print()

    # Aggregate metrics
    summary: dict[str, Any] = {}
    for arm in arms:
        arm_rows = [c["arms"][arm] for c in case_results]
        verified_count = sum(1 for r in arm_rows if r["verified"])
        under_count = sum(1 for r in arm_rows if r["under_allocated"])
        unnec_count = sum(1 for r in arm_rows if r["unnecessary"])
        latencies = [r["latency_ms"] for r in arm_rows if r["latency_ms"] > 0]
        confidences = [r["confidence"] for r in arm_rows if r["confidence"] is not None]

        total = len(arm_rows)
        summary[arm] = {
            "verified_count": verified_count,
            "total_cases": total,
            "verified_success_rate": round(verified_count / total, 4) if total else 0.0,
            "under_allocation_rate": round(under_count / total, 4) if total else 0.0,
            "unnecessary_retrieval_rate": round(unnec_count / total, 4) if total else 0.0,
            "mean_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
            "mean_confidence": round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
        }

    # Log to Weave EvaluationLogger if active
    if weave_active and weave is not None:
        logger_cls = getattr(weave, "EvaluationLogger", None)
        if logger_cls:
            for arm in arms:
                arm_summary = summary[arm]
                arm_model = case_results[0]["arms"][arm]["model"] if case_results else arm
                evaluator = logger_cls(
                    name=f"worldloop-{args.experiment}-{arm}",
                    model={
                        "name": arm_model,
                        "metadata": {"provider": arm, "mode": args.mode},
                    },
                    dataset=dataset.snapshot_id,
                    scorers=["verified", "under_allocated", "latency_ms"],
                    eval_attributes={
                        "experiment_id": args.experiment,
                        "arm": arm,
                        "mode": args.mode,
                    },
                )
                for case_res in case_results:
                    arm_eval = case_res["arms"][arm]
                    evaluator.log_example(
                        inputs={"case_id": case_res["case_id"], "question": case_res["question"]},
                        output={"route": arm_eval["route"], "recipe": arm_eval["recipe"]},
                        scores={
                            "verified": arm_eval["verified"],
                            "under_allocated": arm_eval["under_allocated"],
                            "latency_ms": arm_eval["latency_ms"],
                        },
                    )
                evaluator.log_summary(
                    {
                        "verified_success_rate": arm_summary["verified_success_rate"],
                        "under_allocation_rate": arm_summary["under_allocation_rate"],
                        "mean_latency_ms": arm_summary["mean_latency_ms"],
                    }
                )

    report = {
        "experiment_id": args.experiment,
        "snapshot_id": dataset.snapshot_id,
        "mode": args.mode,
        "code_revision": git_revision(),
        "summary": summary,
        "cases": case_results,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to: {out_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print(f"{'ARM':<18} | {'ACCURACY':<10} | {'UNDER-ALLOC':<12} | {'UNNECESSARY':<12} | {'AVG LATENCY':<12} | {'CONF'}")
    print("-" * 80)
    for arm, stats in summary.items():
        print(f"{arm:<18} | {stats['verified_success_rate']*100:>8.1f}% | {stats['under_allocation_rate']*100:>10.1f}% | {stats['unnecessary_retrieval_rate']*100:>10.1f}% | {stats['mean_latency_ms']:>10.1f}ms | {stats['mean_confidence']:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
