from __future__ import annotations

import argparse
import json
from pathlib import Path

from worldloop.benchmark import generate_benchmark
from worldloop.typesafe_router import evaluate_router, heuristic_route, typesafe_route


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate TypeSafe routing on frozen WorldLoop cases")
    parser.add_argument("--split", choices=("development", "heldout"), default="heldout")
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Number of cases to call TypeSafe on; use 1 for a harmless canary, 0 for all",
    )
    parser.add_argument("--output", default="reports/typesafe-router-live.json")
    args = parser.parse_args()

    dataset = generate_benchmark()
    source_cases = dataset.development if args.split == "development" else dataset.heldout
    cases = source_cases if args.limit == 0 else source_cases[: args.limit]
    if not cases:
        raise SystemExit("no cases selected")

    heuristic_metrics, heuristic_rows = evaluate_router(cases, heuristic_route)
    typesafe_metrics, typesafe_rows = evaluate_router(cases, typesafe_route)
    payload = {
        "dataset_snapshot": dataset.snapshot_id,
        "split": args.split,
        "case_ids": [case.case_id for case in cases],
        "heuristic": {"metrics": heuristic_metrics.to_dict(), "rows": heuristic_rows},
        "typesafe": {"metrics": typesafe_metrics.to_dict(), "rows": typesafe_rows},
        "interpretation_rule": (
            "TypeSafe confidence is model-reported distribution concentration. It is not authority "
            "or proof of correctness; evaluate thresholds empirically on frozen outcomes."
        ),
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["typesafe"]["metrics"], sort_keys=True))
    print(f"report={target}")


if __name__ == "__main__":
    main()
