from __future__ import annotations

import argparse

from worldloop.benchmark import generate_benchmark, write_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the frozen WorldLoop hackathon benchmark")
    parser.add_argument(
        "--output",
        default="fixtures/generated/change_aware_rollout_v1.json",
        help="Output JSON path",
    )
    args = parser.parse_args()
    dataset = generate_benchmark()
    path = write_snapshot(args.output, dataset)
    print(f"wrote {path} ({dataset.snapshot_id})")


if __name__ == "__main__":
    main()
