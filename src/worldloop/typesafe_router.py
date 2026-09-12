from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Callable, Literal

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


@dataclass(frozen=True)
class RouterMetrics:
    provider: str
    model: str
    case_count: int
    verified_count: int
    verified_success: float
    under_allocation_count: int
    unnecessary_retrieval_count: int
    abstain_count: int
    mean_confidence: float | None
    route_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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


def typesafe_question() -> Any:
    """Build the official SDK Choice object lazily so core/offline imports stay optional."""
    try:
        from typesafe_sdk import Choice
    except ImportError as exc:  # pragma: no cover - optional sponsor dependency
        raise RuntimeError(
            "TypeSafe SDK is not installed; install the sponsors extra or `uv add typesafe-sdk`"
        ) from exc
    return Choice(
        instructions=(
            "Choose the smallest retrieval route WorldLoop should use before deciding the rollout "
            "question. Choose a retrieval strategy only; do not decide APPROVE/BLOCK/ESCALATE and "
            "do not invent facts that are absent from state."
        ),
        criteria=ROUTE_CRITERIA,
    )


def typesafe_route(case: GeneratedCase) -> SemanticRouteResult:
    """Run one bounded TypeSafe Choice judgment.

    `typesafe-sdk` and `TYPESAFE_API_KEY` are runtime-only sponsor dependencies. TypeSafe returns
    a typed judgment; WorldLoop still owns route-to-recipe mapping, transition checks, authority,
    execution, and verification.
    """
    try:
        from typesafe_sdk import TypeSafeClient
    except ImportError as exc:  # pragma: no cover - optional sponsor dependency
        raise RuntimeError(
            "TypeSafe SDK is not installed; install the sponsors extra or `uv add typesafe-sdk`"
        ) from exc

    with TypeSafeClient() as client:
        response = client.system_one(
            state=routing_state(case),
            questions={"route": typesafe_question()},
        )
    return parse_typesafe_choice(response.choices["route"])


def route_is_verified(case: GeneratedCase, result: SemanticRouteResult) -> bool:
    return set(case.repair_recipe).issubset(result.recipe)


def evaluate_router(
    cases: tuple[GeneratedCase, ...],
    router: Callable[[GeneratedCase], SemanticRouteResult],
) -> tuple[RouterMetrics, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    confidences: list[float] = []
    route_counts: Counter[str] = Counter()
    verified_count = 0
    under_allocation_count = 0
    unnecessary_retrieval_count = 0
    abstain_count = 0
    provider = "unknown"
    model = "unknown"

    for case in cases:
        result = router(case)
        provider = result.provider
        model = result.model
        verified = route_is_verified(case, result)
        verified_count += int(verified)
        under_allocation_count += int(not verified and result.route != "ABSTAIN")
        abstain_count += int(result.route == "ABSTAIN")
        unnecessary = verified and not set(result.recipe).issubset(set(case.repair_recipe))
        unnecessary_retrieval_count += int(unnecessary)
        if result.confidence is not None:
            confidences.append(result.confidence)
        route_counts[result.route] += 1
        rows.append(
            {
                "case_id": case.case_id,
                "route": result.route,
                "recipe": list(result.recipe),
                "verified": verified,
                "confidence": result.confidence,
                "probabilities": result.probabilities,
            }
        )

    count = len(cases)
    metrics = RouterMetrics(
        provider=provider,
        model=model,
        case_count=count,
        verified_count=verified_count,
        verified_success=round(verified_count / count, 6) if count else 0.0,
        under_allocation_count=under_allocation_count,
        unnecessary_retrieval_count=unnecessary_retrieval_count,
        abstain_count=abstain_count,
        mean_confidence=(round(sum(confidences) / len(confidences), 6) if confidences else None),
        route_counts=dict(sorted(route_counts.items())),
    )
    return metrics, rows
