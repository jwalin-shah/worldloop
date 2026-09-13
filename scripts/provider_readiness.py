#!/usr/bin/env python3
"""Cheap provider-readiness preflight for WorldLoop.

This script proves the execution path only up to (but not including) a paid/provider
request. It never prints credential values. The first failing hop is emitted as JSON so
WorldLoop/LifeOps can route around unavailable capabilities without wasting calls.

Usage:
    uv run python scripts/provider_readiness.py typesafe

Exit codes:
    0  READY
    11 runtime executable missing
    12 sponsor SDK unavailable
    13 secret context unavailable
    14 required credential absent inside secret context
    64 unsupported provider
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Sequence


@dataclass(frozen=True)
class Readiness:
    capability: str
    status: str
    highest_proven_level: str
    blocking_stage: str | None = None
    reason: str | None = None
    cost: int = 0
    external_provider_calls: int = 0


def emit(result: Readiness, code: int) -> int:
    print(json.dumps(asdict(result), sort_keys=True))
    return code


def run_quiet(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )


def typesafe_readiness() -> int:
    capability = "typesafe"

    for binary in ("uv", "infisical"):
        if shutil.which(binary) is None:
            return emit(
                Readiness(
                    capability=capability,
                    status="BLOCKED",
                    highest_proven_level="HOST_REACHABLE",
                    blocking_stage="RUNTIME_EXECUTABLE",
                    reason=f"{binary.upper()}_MISSING",
                ),
                11,
            )

    sdk = run_quiet(("uv", "run", "python", "-c", "import typesafe_sdk"))
    if sdk.returncode != 0:
        return emit(
            Readiness(
                capability=capability,
                status="BLOCKED",
                highest_proven_level="RUNTIME_READY",
                blocking_stage="SPONSOR_SDK",
                reason="TYPESAFE_SDK_UNAVAILABLE",
            ),
            12,
        )

    env_name = os.getenv("WORLDLOOP_INFISICAL_ENV", "hackathon")
    secret_context = run_quiet(("infisical", "run", f"--env={env_name}", "--", "true"))
    if secret_context.returncode != 0:
        return emit(
            Readiness(
                capability=capability,
                status="BLOCKED",
                highest_proven_level="SDK_READY",
                blocking_stage="SECRET_CONTEXT",
                reason="INFISICAL_CONTEXT_UNAVAILABLE",
            ),
            13,
        )

    credential_presence = run_quiet(
        (
            "infisical",
            "run",
            f"--env={env_name}",
            "--",
            "uv",
            "run",
            "python",
            "-c",
            "import os,sys; sys.exit(0 if os.environ.get('TYPESAFE_API_KEY') else 1)",
        )
    )
    if credential_presence.returncode != 0:
        return emit(
            Readiness(
                capability=capability,
                status="BLOCKED",
                highest_proven_level="SECRET_CONTEXT_READY",
                blocking_stage="CREDENTIAL_PRESENCE",
                reason="TYPESAFE_API_KEY_ABSENT",
            ),
            14,
        )

    return emit(
        Readiness(
            capability=capability,
            status="READY",
            highest_proven_level="RUNTIME_READY",
        ),
        0,
    )


def main() -> int:
    provider = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    if provider == "typesafe":
        return typesafe_readiness()
    return emit(
        Readiness(
            capability=provider or "unknown",
            status="BLOCKED",
            highest_proven_level="NONE",
            blocking_stage="PROVIDER",
            reason="UNSUPPORTED_PROVIDER",
        ),
        64,
    )


if __name__ == "__main__":
    raise SystemExit(main())
