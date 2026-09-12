from __future__ import annotations

import argparse
import json
from pathlib import Path

from worldloop.benchmark import generate_benchmark
from worldloop.policy import evaluate_v0_v1


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate derived WorldLoop policy v1")
    parser.add_argument("--output", default="reports/EXP-008-gate3.json")
    args = parser.parse_args()

    dataset = generate_benchmark()
    report = evaluate_v0_v1(dataset)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n")
    print(
        f"{report.promotion_decision}: "
        f"v0={report.v0.first_pass_verified_success:.3f} "
        f"v1={report.v1.first_pass_verified_success:.3f} "
        f"snapshot={report.dataset_snapshot}"
    )


if __name__ == "__main__":
    main()
