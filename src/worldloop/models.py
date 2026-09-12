from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .ir import TransitionCheck


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    entity: str
    text: str
    event_time: str
    observed_time: str
    source: str
    links: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    question: str
    expected_answer: str
    required_evidence: tuple[str, ...]
    initial_recipe: tuple[str, ...]
    repair_recipe: tuple[str, ...]
    failure_class: str
    as_of: str | None = None
    expected_abstain: bool = False


@dataclass
class PassResult:
    pass_number: int
    recipe: list[str]
    evidence_ids: list[str]
    score: float
    sufficient: bool
    answer: str
    failure_class: str | None = None
    diagnosis: str | None = None
    provenance: list[dict[str, str]] = field(default_factory=list)
    transition_check: TransitionCheck | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LoopResult:
    case_id: str
    question: str
    passes: list[PassResult]
    improved: bool
    final_sufficient: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "question": self.question,
            "passes": [item.to_dict() for item in self.passes],
            "improved": self.improved,
            "final_sufficient": self.final_sufficient,
        }
