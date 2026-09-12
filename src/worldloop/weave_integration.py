from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .episode import EpisodeTrace

try:
    import weave  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    weave = None

DEFAULT_WEAVE_PROJECT = "jwalinshah13-personal/worldloop"


def weave_status() -> dict[str, Any]:
    key_present = bool(os.getenv("WANDB_API_KEY"))
    project = os.getenv("WORLDLOOP_WEAVE_PROJECT", DEFAULT_WEAVE_PROJECT)
    return {
        "sdk_installed": weave is not None,
        "api_key_present": key_present,
        "project": project,
        "remote_tracing_ready": weave is not None and key_present,
    }


def init_weave_if_configured(global_attributes: dict[str, Any] | None = None) -> bool:
    status = weave_status()
    if not status["remote_tracing_ready"]:
        return False
    assert weave is not None
    weave.init(
        status["project"],
        settings={"implicitly_patch_integrations": False},
        global_attributes=global_attributes or {},
    )
    return True


def traced(fn: Callable[..., Any]) -> Callable[..., Any]:
    if weave is None:
        return fn
    return weave.op(fn)


@traced
def _trace_event(event: dict[str, Any]) -> dict[str, Any]:
    return event


@traced
def _trace_episode(payload: dict[str, Any]) -> dict[str, Any]:
    for event in payload["events"]:
        _trace_event(event)
    return payload


def publish_episode(trace: EpisodeTrace) -> dict[str, Any]:
    """Publish one completed episode to Weave, or return an offline receipt.

    The local `EpisodeTrace` is always the source artifact. Remote publishing is additive,
    so missing credentials never erase the inspectable trajectory.
    """
    payload = trace.to_dict()
    status = weave_status()
    if not status["remote_tracing_ready"]:
        return {
            "remote_logged": False,
            "evaluation_logged": False,
            "reason": "weave_not_configured",
            "project": status["project"],
            "run_id": trace.identity.run_id,
        }

    attributes = trace.identity.to_dict()
    init_weave_if_configured(attributes)
    assert weave is not None
    with weave.attributes(attributes):
        _trace_episode(payload)

        logger_cls = getattr(weave, "EvaluationLogger", None)
        if logger_cls is None:
            return {
                "remote_logged": True,
                "evaluation_logged": False,
                "reason": "evaluation_logger_unavailable",
                "project": status["project"],
                "run_id": trace.identity.run_id,
            }

        evaluator = logger_cls(
            name=f"worldloop-{trace.identity.experiment_id}",
            model={
                "name": trace.identity.model,
                "metadata": {
                    "provider": trace.identity.provider,
                    "workflow_version": trace.identity.workflow_version,
                    "policy_version": trace.identity.policy_version,
                },
            },
            dataset=trace.identity.dataset_snapshot,
            scorers=["verified_success", "improved", "final_score"],
            attributes=attributes,
        )
        evaluator.log_example(
            inputs={"case_id": trace.case_id, "question": trace.question},
            output={
                "answer": trace.final_answer,
                "final_sufficient": trace.final_sufficient,
                "events": len(trace.events),
            },
            scores={
                "verified_success": trace.final_sufficient,
                "improved": trace.improved,
                "final_score": trace.final_score,
            },
        )
        evaluator.log_summary(
            {
                "verified_success": float(trace.final_sufficient),
                "improved": float(trace.improved),
                "final_score": trace.final_score,
            }
        )

    return {
        "remote_logged": True,
        "evaluation_logged": True,
        "project": status["project"],
        "run_id": trace.identity.run_id,
    }


def build_evaluation(dataset: list[dict[str, Any]], scorers: list[Callable[..., Any]]) -> Any:
    """Build a Weave Evaluation only when the optional SDK is installed."""
    if weave is None:
        raise RuntimeError("Weave SDK is not installed; run bootstrap with WORLDLOOP_INSTALL_WEAVE=1")
    return weave.Evaluation(dataset=dataset, scorers=scorers)
