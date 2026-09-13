from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_gate3_report(root: Path) -> dict[str, Any]:
    return json.loads((root / "reports" / "EXP-008-gate3.json").read_text())


def live_program_view(loop: Any, case_id: str) -> dict[str, Any]:
    case = loop.cases[case_id]
    result = loop.run_case(case_id)

    pass_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    for item in result.passes:
        check = item.transition_check
        pass_rows.append(
            {
                "pass": item.pass_number,
                "recipe": " -> ".join(item.recipe),
                "score": item.score,
                "sufficient": item.sufficient,
                "failure_class": item.failure_class or "",
                "evidence": ", ".join(item.evidence_ids),
            }
        )
        if check is not None:
            missing = [name for name, passed in check.obligation_results.items() if not passed]
            transition_rows.append(
                {
                    "pass": check.pass_number,
                    "node": check.node_id,
                    "preconditions": check.preconditions_passed,
                    "postcondition": check.postcondition_passed,
                    "next_state": check.next_state,
                    "failure_class": check.failure_class or "",
                    "missing_obligations": ", ".join(missing),
                }
            )

    before = list(case.initial_recipe)
    after = list(result.passes[-1].recipe)
    added = [step for step in after if step not in before]
    return {
        "case_id": case.case_id,
        "question": case.question,
        "required_evidence": list(case.required_evidence),
        "pass_rows": pass_rows,
        "transition_rows": transition_rows,
        "program_before": before,
        "program_after": after,
        "program_delta": added,
        "failure_class": result.passes[0].failure_class or "none",
        "improved": result.improved,
        "final_sufficient": result.final_sufficient,
    }


def heldout_comparison_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    v0 = report["v0"]
    v1 = report["v1"]
    return [
        {
            "metric": "First-pass verified success",
            "v0": v0["first_pass_verified_success"],
            "v1": v1["first_pass_verified_success"],
            "delta": round(v1["first_pass_verified_success"] - v0["first_pass_verified_success"], 6),
        },
        {
            "metric": "Final verified success",
            "v0": v0["final_verified_success"],
            "v1": v1["final_verified_success"],
            "delta": round(v1["final_verified_success"] - v0["final_verified_success"], 6),
        },
        {
            "metric": "Mean retrieval steps",
            "v0": v0["mean_retrieval_steps"],
            "v1": v1["mean_retrieval_steps"],
            "delta": round(v1["mean_retrieval_steps"] - v0["mean_retrieval_steps"], 6),
        },
    ]


def program_comparison_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rule in report["policy"]["rules"]:
        if rule["cross_entity"]:
            condition = "cross-entity dependency"
            v0 = "vector"
        elif rule["freshness_sensitive"]:
            condition = "freshness-sensitive"
            v0 = "vector"
        else:
            condition = "exact/control"
            v0 = "exact"
        v1 = " -> ".join(rule["recipe"])
        rows.append(
            {
                "task shape": condition,
                "program v0": v0,
                "learned program v1": v1,
                "added operation": "none" if v0 == v1 else v1.removeprefix(f"{v0} -> "),
            }
        )
    return rows


def lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset_snapshot": report["dataset_snapshot"],
        "heldout_cases": report["v1"]["case_count"],
        "v0_first_pass": report["v0"]["first_pass_verified_success"],
        "v1_first_pass": report["v1"]["first_pass_verified_success"],
        "final_verified": report["v1"]["final_verified_success"],
        "promotion_decision": report["promotion_decision"],
    }


def load_three_arm_report(root: Path, filename: str = "three-arm-eval.json") -> dict[str, Any] | None:
    target = root / "reports" / filename
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def load_adversarial_report(root: Path) -> dict[str, Any] | None:
    return load_three_arm_report(root, filename="three-arm-eval-adversarial.json")


def three_arm_summary_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary", {})
    labels = {
        "deterministic": "Deterministic Heuristic",
        "typesafe": "TypeSafe Multi-Primitive (Jev)",
        "wandb_inference": "W&B Hosted LLM (Llama-3.3-70B)",
    }
    rows: list[dict[str, Any]] = []
    for key, arm in summary.items():
        rows.append(
            {
                "Arm": labels.get(key, key),
                "Accuracy": f"{arm.get('verified_success_rate', 0.0) * 100:.1f}%",
                "Under-Allocation": f"{arm.get('under_allocation_rate', 0.0) * 100:.1f}%",
                "Unnecessary Retrieval": f"{arm.get('unnecessary_retrieval_rate', 0.0) * 100:.1f}%",
                "Mean Latency": f"{arm.get('mean_latency_ms', 0.0):.1f} ms",
                "Mean Confidence": f"{arm.get('mean_confidence', 0.0):.2f}",
            }
        )
    return rows


def three_arm_case_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    cases = report.get("cases", [])
    rows: list[dict[str, Any]] = []
    for item in cases:
        arms = item.get("arms", {})
        det = arms.get("deterministic", {})
        ts = arms.get("typesafe", {})
        wb = arms.get("wandb_inference", {})
        rows.append(
            {
                "Case": item.get("case_id"),
                "Target Recipe": " -> ".join(item.get("target_recipe", [])),
                "Deterministic": f"{det.get('route', '-')} ({'✓' if det.get('verified') else '✗'})",
                "TypeSafe Jev": f"{ts.get('route', '-')} ({'✓' if ts.get('verified') else '✗'}) [p={ts.get('confidence', 0):.2f}]",
                "W&B Llama 3.3": f"{wb.get('route', '-')} ({'✓' if wb.get('verified') else '✗'}) [{wb.get('latency_ms', 0):.0f}ms]",
            }
        )
    return rows


def load_benchmark_v2_report(root: Path) -> dict[str, Any] | None:
    p = root / "reports" / "benchmark-v2-four-arm-eval.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def benchmark_v2_summary_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary", {})
    labels = {
        "fixed_simple": "Fixed Baseline (Exact + Lexical)",
        "deterministic_worldloop": "Deterministic WorldLoop Router",
        "typesafe_router": "TypeSafe Specialized Router",
        "wandb_llama_70b": "W&B Hosted Llama 3.3 70B",
    }
    rows: list[dict[str, Any]] = []
    for key, arm in summary.items():
        rows.append(
            {
                "Arm": labels.get(key, key),
                "End-Task Accuracy": f"{arm.get('accuracy', 0.0) * 100:.1f}%",
                "Citation Precision": f"{arm.get('citation_precision', 0.0) * 100:.1f}%",
                "Citation Recall": f"{arm.get('citation_recall', 0.0) * 100:.1f}%",
                "Stale Citation Rate": f"{arm.get('stale_citation_rate', 0.0) * 100:.1f}%",
                "Mean Retrieval Waste": f"{arm.get('mean_retrieval_waste', 0.0):.1f} items",
                "Mean Latency": f"{arm.get('mean_latency_ms', 0.0):.1f} ms",
            }
        )
    return rows


