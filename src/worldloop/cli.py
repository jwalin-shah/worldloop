from __future__ import annotations

import argparse
import json

from .engine import WorldLoop
from .runtime import FIXTURES
from .weave_integration import init_weave_if_configured, weave_status


def main() -> None:
    parser = argparse.ArgumentParser(prog="worldloop")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--case", default="case-cross-entity")
    demo.add_argument("--json", action="store_true")
    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("--json", action="store_true")
    sub.add_parser("health")
    args = parser.parse_args()

    init_weave_if_configured()
    loop = WorldLoop(FIXTURES)
    if args.command == "demo":
        payload = loop.run_case(args.case).to_dict()
    elif args.command == "benchmark":
        payload = loop.benchmark()
    else:
        payload = {"ok": True, "cases": len(loop.cases), "weave": weave_status()}

    if getattr(args, "json", False) or args.command == "health":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)


if __name__ == "__main__":
    main()
