from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from .benchmark import GeneratedCase

Route = Literal[
    "MODEL_ONLY",
    "EXACT",
    "LEXICAL",
    "VECTOR",
    "TEMPORAL",
    "GRAPH",
    "DEEP_RETRIEVAL",
    "ABSTAIN",
]

ROUTE_CRITERIA: dict[str, str] = {
    "MODEL_ONLY": (
        "No external retrieval is needed because the current supplied state is already complete "
        "for the next semantic judgment."
    ),
    "EXACT": (
        "Use a direct exact lookup when the needed source is known and neither freshness-aware "
        "selection nor a cross-entity join is required."
    ),
    "LEXICAL": (
        "Use keyword or lexical retrieval when terminology is the main access problem and no "
        "temporal or graph relation is required."
    ),
    "VECTOR": (
        "Use semantic/vector retrieval when evidence is described conceptually and a single-entity "
        "semantic search is sufficient."
    ),
    "TEMPORAL": (
        "Use freshness-aware temporal retrieval when current truth may supersede an older matching "
        "fact or status."
    ),
    "GRAPH": (
        "Use graph/dependency retrieval when the answer depends on another linked entity or a "
        "relationship that must be traversed."
    ),
    "DEEP_RETRIEVAL": (
        "Use a broader retrieval plan when more than one specialized retrieval operator is needed "
        "and the task cannot be satisfied by one bounded route."
    ),
    "ABSTAIN": (
        "Do not select a retrieval route when the supplied state is too incomplete or contradictory "
        "to choose one responsibly."
    ),
}

ROUTE_TO_RECIPE: dict[str, tuple[str, ...]] = {
    "MODEL_ONLY": (),
    "EXACT": ("exact",),
    "LEXICAL": ("lexical",),
    "VECTOR": ("vector",),
    "TEMPORAL": ("vector", "temporal"),
    "GRAPH": ("vector", "graph"),
    "DEEP_RETRIEVAL": ("vector", "temporal", "graph"),
    "ABSTAIN": (),
}


@dataclass(frozen=True)
class SemanticRouteResult:
    route: Route
    confidence: float | None
    probabilities: dict[str, float]
    provider: str
    model: str

    @property
    def recipe(self) -> tuple[str, ...]:
        return ROUTE_TO_RECIPE[self.route]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["recipe"] = list(self.recipe)
        return payload


def routing_state(case: GeneratedCase) -> dict[str, Any]:
    """Construct legitimate pre-action state shared by every router arm.

    Ground-truth decision, failure label, repair recipe, and held-out outcome are intentionally
    excluded. The state only contains information declared before retrieval begins.
    """
    features = case.pre_action_features()
    return {
        "task_family": case.task_family,
        "question": case.question,
        "risk_band": case.risk_band,
        "has_dependency": features["has_dependency"],
        "freshness_sensitive": features["freshness_sensitive"],
        "cross_entity": features["cross_entity"],
        "available_route_budget": 3,
    }


def heuristic_route(case: GeneratedCase) -> SemanticRouteResult:
    """Deterministic baseline over the exact same pre-action state."""
    state = routing_state(case)
    if state["cross_entity"] or state["has_dependency"]:
        route: Route = "GRAPH"
    elif state["freshness_sensitive"]:
        route = "TEMPORAL"
    else:
        route = "EXACT"
    return SemanticRouteResult(
        route=route,
        confidence=None,
        probabilities={},
        provider="deterministic",
        model="heuristic-v1",
    )


def _coerce_route(value: str) -> Route:
    if value not in ROUTE_CRITERIA:
        raise ValueError(f"TypeSafe returned unsupported route: {value!r}")
    return value  # type: ignore[return-value]


def parse_typesafe_choice(answer: Any) -> SemanticRouteResult:
    """Normalize the official ChoiceAnswer without granting it control-flow authority."""
    route = _coerce_route(str(answer.choice))
    probabilities = {str(key): float(value) for key, value in answer.probabilities.items()}
    return SemanticRouteResult(
        route=route,
        confidence=float(answer.confidence),
        probabilities=probabilities,
        provider="typesafe",
        model="jev-latest",
    )


def typesafe_route(case: GeneratedCase) -> SemanticRouteResult:
    """Run one bounded TypeSafe Choice judgment.

    `typesafe-sdk` and `TYPESAFE_API_KEY` are runtime-only sponsor dependencies. TypeSafe returns
    a typed judgment; WorldLoop still owns route-to-recipe mapping, transition checks, authority,
    execution, and verification.
    """
    try:
        from typesafe_sdk import Choice, TypeSafeClient
    except ImportError as exc:  # pragma: no cover - optional sponsor dependency
        raise RuntimeError(
            "TypeSafe SDK is not installed; install the sponsors extra or `uv add typesafe-sdk`"
        ) from exc

    state = routing_state(case)
    question = Choice(
        instructions=(
            "Choose the smallest retrieval route WorldLoop should use before deciding the rollout "
            "question. Choose a retrieval strategy only; do not decide APPROVE/BLOCK/ESCALATE and "
            "do not invent facts that are absent from state."
        ),
        criteria=ROUTE_CRITERIA,
    )
    with TypeSafeClient() as client:
        response = client.system_one(state=state, questions={"route": question})
    return parse_typesafe_choice(response.choices["route"])
