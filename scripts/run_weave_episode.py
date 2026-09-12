from __future__ import annotations

import argparse
import os
import subprocess
from hashlib import sha256
from pathlib import Path

from worldloop.engine import WorldLoop
from worldloop.episode import RunIdentity, run_episode, write_episode_trace
from worldloop.runtime import FIXTURES
from worldloop.weave_integration import publish_episode, weave_status


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


def fixture_snapshot() -> str:
    digest = sha256()
    for name in ("cases.json", "evidence.json"):
        digest.update((FIXTURES / name).read_bytes())
    return f"fixtures:{digest.hexdigest()[:16]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one inspectable WorldLoop Weave episode")
    parser.add_argument("--case", default="case-cross-entity")
    parser.add_argument("--experiment", default="EXP-008-live")
    parser.add_argument("--output-dir", default="reports/weave")
    parser.add_argument("--provider", default="deterministic")
    parser.add_argument("--model", default="none")
    args = parser.parse_args()

    snapshot = fixture_snapshot()
    identity = RunIdentity.create(
        experiment_id=args.experiment,
        code_revision=git_revision(),
        dataset_snapshot=snapshot,
        evidence_snapshot=snapshot,
        provider=args.provider,
        model=args.model,
    )
    loop = WorldLoop(FIXTURES)
    trace = run_episode(loop, args.case, identity)
    output = Path(args.output_dir) / f"{identity.run_id}.json"
    write_episode_trace(str(output), trace)
    receipt = publish_episode(trace)
    print(f"local_trace={output}")
    print(f"weave={weave_status()}")
    print(f"publish_receipt={receipt}")


if __name__ == "__main__":
    main()
