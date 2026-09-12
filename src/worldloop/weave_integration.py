from __future__ import annotations

import os
from typing import Any, Callable

try:
    import weave  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    weave = None


def weave_status() -> dict[str, Any]:
    key_present = bool(os.getenv("WANDB_API_KEY"))
    project = os.getenv("WORLDLOOP_WEAVE_PROJECT", "worldloop-coreweave-2026")
    return {
        "sdk_installed": weave is not None,
        "api_key_present": key_present,
        "project": project,
        "remote_tracing_ready": weave is not None and key_present,
    }


def init_weave_if_configured() -> bool:
    status = weave_status()
    if not status["remote_tracing_ready"]:
        return False
    assert weave is not None
    weave.init(status["project"])
    return True


def traced(fn: Callable[..., Any]) -> Callable[..., Any]:
    if weave is None:
        return fn
    return weave.op(fn)


def build_evaluation(dataset: list[dict[str, Any]], scorers: list[Callable[..., Any]]) -> Any:
    """Build a Weave Evaluation only when the optional SDK is installed."""
    if weave is None:
        raise RuntimeError("Weave SDK is not installed; run bootstrap with WORLDLOOP_INSTALL_WEAVE=1")
    return weave.Evaluation(dataset=dataset, scorers=scorers)
