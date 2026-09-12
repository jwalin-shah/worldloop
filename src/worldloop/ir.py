from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class NodeSpec:
    """Minimal executable contract for a WorldLoop node.

    The hackathon MVP intentionally keeps this smaller than the long-term IR. It is
    enough to bind the node's interface, evidence obligations, explicit checks, and
    success/failure transitions without pretending semantic computation is formally
    proved.
    """

    node_id: str
    version: str
    kind: str
    input_schema: str
    output_schema: str
    evidence_obligations: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    postconditions: tuple[str, ...] = ()
    success_transition: str = "DONE"
    failure_transition: str = "REPAIR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TransitionCheck:
    """Observed evidence that one node transition was or was not admissible."""

    node_id: str
    node_version: str
    pass_number: int
    evidence_used: list[str]
    obligation_results: dict[str, bool]
    preconditions_checked: list[str]
    preconditions_passed: bool
    effects: list[str]
    result: str
    postconditions_checked: list[str]
    postcondition_passed: bool
    next_state: str
    failure_class: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
