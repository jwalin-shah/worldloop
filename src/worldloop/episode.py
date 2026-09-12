from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class RunIdentity:
    experiment_id: str
    run_id: str
    code_revision: str
    dataset_snapshot: str
    evidence_snapshot: str
    workflow_version: str
    policy_version: str
    provider: str
    model: str
    scorer_version: str

    @classmethod
    def create(
        cls,
        *,
        experiment_id: str,
        code_revision: str,
        dataset_snapshot: str,
        evidence_snapshot: str,
        workflow_version: str = "workflow-v0",
        policy_version: str = "policy-v0",
        provider: str = "deterministic",
        model: str = "none",
        scorer_version: str = "transition-check-v1",
        run_id: str | None = None,
    ) -> "RunIdentity":
        return cls(
            experiment_id=experiment_id,
            run_id=run_id or f"run-{uuid4().hex[:12]}",
            code_revision=code_revision,
            dataset_snapshot=dataset_snapshot,
            evidence_snapshot=evidence_snapshot,
            workflow_version=workflow_version,
            policy_version=policy_version,
            provider=provider,
            model=model,
            scorer_version=scorer_version,
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class EpisodeEvent:
    event_type: str
    stage: str
    payload: dict[str, Any]
    observed_at: str

    @classmethod
    def make(cls, event_type: str, stage: str, payload: dict[str, Any]) -> "EpisodeEvent":
        observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return cls(event_type=event_type, stage=stage, payload=payload, observed_at=observed_at)


@dataclass
class EpisodeTrace:
    identity: RunIdentity
    case_id: str
    question: str
    events: list[EpisodeEvent] = field(default_factory=list)
    final_sufficient: bool = False
    improved: bool = False
    final_score: float = 0.0
    final_answer: str = "INSUFFICIENT_EVIDENCE"

    def add(self, event_type: str, stage: str, **payload: Any) -> None:
        self.events.append(EpisodeEvent.make(event_type, stage, payload))

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "case_id": self.case_id,
            "question": self.question,
            "events": [asdict(event) for event in self.events],
            "final_sufficient": self.final_sufficient,
            "improved": self.improved,
            "final_score": self.final_score,
            "final_answer": self.final_answer,
        }


def _transition_payload(result: Any) -> dict[str, Any] | None:
    check = getattr(result, "transition_check", None)
    if check is None:
        return None
    if hasattr(check, "to_dict"):
        return check.to_dict()
    if hasattr(check, "__dict__"):
        return dict(check.__dict__)
    return None


def run_episode(loop: Any, case_id: str, identity: RunIdentity) -> EpisodeTrace:
    """Execute one real WorldLoop failure/repair episode while emitting typed local events.

    This intentionally mirrors the runtime steps instead of wrapping `run_case()` after the fact,
    so the event log records the actual recipe, retrieved evidence, Critic result, repair delta,
    retry, and verification result in execution order.
    """
    case = loop.cases[case_id]
    trace = EpisodeTrace(identity=identity, case_id=case.case_id, question=case.question)

    first_recipe = list(case.initial_recipe)
    trace.add(
        "program_selected",
        "compiler",
        workflow_version=identity.workflow_version,
        policy_version=identity.policy_version,
        recipe=first_recipe,
    )

    first_items = loop.retrieve(case, first_recipe)
    trace.add(
        "retrieval_completed",
        "retrieval",
        pass_number=1,
        recipe=first_recipe,
        evidence_ids=[item.evidence_id for item in first_items],
    )
    first = loop.evaluate(case, first_items, 1, first_recipe)
    trace.add(
        "semantic_node_completed",
        "worker",
        pass_number=1,
        answer=first.answer,
        sufficient=first.sufficient,
        transition_check=_transition_payload(first),
    )
    trace.add(
        "critic_scored",
        "critic",
        pass_number=1,
        score=first.score,
        failure_class=first.failure_class,
        diagnosis=first.diagnosis,
    )

    final = first
    if not first.sufficient and not case.expected_abstain:
        repaired_recipe = loop.repair(case, first_recipe)
        delta = [step for step in repaired_recipe if step not in first_recipe]
        trace.add(
            "program_delta_proposed",
            "loop_doctor",
            failure_class=first.failure_class,
            from_recipe=first_recipe,
            to_recipe=repaired_recipe,
            added_steps=delta,
        )
        trace.add(
            "retry_started",
            "runtime",
            pass_number=2,
            recipe=repaired_recipe,
        )
        second_items = loop.retrieve(case, repaired_recipe)
        trace.add(
            "retrieval_completed",
            "retrieval",
            pass_number=2,
            recipe=repaired_recipe,
            evidence_ids=[item.evidence_id for item in second_items],
        )
        second = loop.evaluate(case, second_items, 2, repaired_recipe)
        trace.add(
            "semantic_node_completed",
            "worker",
            pass_number=2,
            answer=second.answer,
            sufficient=second.sufficient,
            transition_check=_transition_payload(second),
        )
        trace.add(
            "critic_scored",
            "critic",
            pass_number=2,
            score=second.score,
            failure_class=second.failure_class,
            diagnosis=second.diagnosis,
        )
        final = second
        trace.improved = second.score > first.score

    trace.final_sufficient = final.sufficient
    trace.final_score = final.score
    trace.final_answer = final.answer
    trace.add(
        "verification_completed",
        "verifier",
        sufficient=final.sufficient,
        score=final.score,
        answer=final.answer,
        improved=trace.improved,
    )
    return trace


def write_episode_trace(path: str, trace: EpisodeTrace) -> None:
    import json
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(trace.to_dict(), indent=2, sort_keys=True) + "\n")
