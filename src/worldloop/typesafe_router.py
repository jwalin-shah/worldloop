from __future__ import annotations

from collections import Counter
from collections.abc import Callable
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


def routing_state(case: GeneratedCase, mode: str = "legacy") -> dict[str, Any]:
    """Construct legitimate pre-action state shared by every router arm.

    Ground-truth decision, failure label, repair recipe, and held-out outcome are intentionally
    excluded. The state only contains information declared before retrieval begins.
    In 'legacy' mode, pre-extracted boolean flags are provided.
    In 'latent' mode, unstructured operational prose (context_brief) is provided.
    In 'adversarial' mode, naturalistic operational prose without keyword giveaways is provided.
    """
    features = case.pre_action_features(mode=mode)
    payload: dict[str, Any] = {
        "task_family": case.task_family,
        "question": case.question,
        "risk_band": case.risk_band,
        "available_route_budget": 3,
        "evidence_obligation": "independent_receipt_required",
    }
    if mode == "legacy":
        payload.update(
            {
                "has_dependency": features.get("has_dependency", False),
                "freshness_sensitive": features.get("freshness_sensitive", False),
                "cross_entity": features.get("cross_entity", False),
            }
        )
    elif mode == "adversarial":
        payload["context_brief"] = case.adversarial_context_prose
    else:
        payload["context_brief"] = case.context_prose
    return payload


def heuristic_route(case: GeneratedCase, mode: str = "legacy") -> SemanticRouteResult:
    """Deterministic baseline over pre-action state."""
    state = routing_state(case, mode=mode)
    if mode == "legacy":
        if state.get("cross_entity") or state.get("has_dependency"):
            route: Route = "GRAPH"
        elif state.get("freshness_sensitive"):
            route = "TEMPORAL"
        else:
            route = "EXACT"
    else:
        # In latent mode without pre-extracted booleans, deterministic heuristics struggle with
        # semantic nuance (negations, superseding timeline entries vs current status).
        brief = str(state.get("context_brief", ""))
        if "dependency" in brief and "no cross-entity" not in brief.lower():
            route = "GRAPH"
        elif "superseding" in brief and "policy" in brief.lower():
            route = "TEMPORAL"
        else:
            route = "EXACT"

    return SemanticRouteResult(
        route=route,
        confidence=None,
        probabilities={},
        provider="deterministic",
        model=f"heuristic-{mode}",
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


def typesafe_multi_questions() -> dict[str, Any]:
    """Build the official SDK multi-primitive question dictionary:
    3 Nouls + 2 Choices evaluated in parallel in a single call.
    """
    try:
        from typesafe_sdk import Choice, Noul
    except ImportError as exc:  # pragma: no cover - optional sponsor dependency
        raise RuntimeError(
            "TypeSafe SDK is not installed; install the sponsors extra or `uv add typesafe-sdk`"
        ) from exc

    return {
        "is_evidence_stale": Noul(
            instructions=(
                "Does the provided context contain superseded, expired, or chronologically "
                "invalidated evidence where a later update or override supersedes an earlier claim?"
            ),
            criteria={
                "true": "A later timeline event, newer update, or remedial override alters the earlier claim.",
                "false": "The record reflects current uncontradicted status with no superseding updates.",
            },
        ),
        "has_cross_entity_dependency": Noul(
            instructions=(
                "Does evaluating this release request require resolving an external upstream "
                "system, coupled component, or cross-entity dependency?"
            ),
            criteria={
                "true": "Verification requires checking a linked external dependency, coupled service, or upstream component.",
                "false": "The release can be verified solely within the primary component without external systems.",
            },
        ),
        "is_receipt_attached": Noul(
            instructions=(
                "Does the supplied state already contain an independently verified execution receipt, "
                "cryptographic signature, or raw verification proof from the target system?"
            ),
            criteria={
                "true": "An independent verifiable execution receipt or raw proof artifact is already attached in state.",
                "false": "Only unverified prose assertions, notes, or tickets are provided without raw execution receipts.",
            },
        ),
        "missing_evidence_class": Choice(
            instructions="If independent verification is missing, what category of retrieval receipt is required?",
            criteria={
                "none": "Independently verified receipt is already attached in state.",
                "temporal_recency": "Missing current unexpired status or latest timeline update.",
                "cross_entity_dependency": "Missing linked upstream dependency health status.",
                "authorization_proof": "Missing sign-off or required approval record.",
                "registry_clearance": "Missing general registry status verification.",
            },
        ),
        "candidate_route": Choice(
            instructions=(
                "What is the minimal external retrieval route WorldLoop should execute to acquire an "
                "independent verification receipt for this rollout claim? Prose assertions in state do NOT "
                "satisfy verification obligations."
            ),
            criteria=ROUTE_CRITERIA,
        ),
    }


def compose_typesafe_policy(
    nouls: dict[str, float],
    choices: dict[str, Any],
    obligation: str = "independent_receipt_required",
) -> SemanticRouteResult:
    """Deterministic policy matrix combining parallel TypeSafe primitives.

    WorldLoop owns the composition logic and verification boundary.
    Under an independent_receipt_required contract (Machine Constitution:
    'Observation is not completion'), prose assertions in state do not
    permit MODEL_ONLY; the minimal bounded receipt acquisition is EXACT.
    """
    p_stale = float(nouls.get("is_evidence_stale", 0.0))
    p_dep = float(nouls.get("has_cross_entity_dependency", 0.0))
    p_receipt = float(nouls.get("is_receipt_attached", 0.0))

    cand_choice = choices.get("candidate_route")
    route_candidate: Route = "EXACT"
    cand_conf: float = 0.5
    cand_probs: dict[str, float] = {}
    if cand_choice is not None:
        raw_choice = getattr(cand_choice, "choice", str(cand_choice))
        route_candidate = _coerce_route(str(raw_choice))
        cand_conf = float(getattr(cand_choice, "confidence", 0.5))
        probs = getattr(cand_choice, "probabilities", {})
        cand_probs = {str(k): float(v) for k, v in probs.items()}

    # Contract enforcement: If an independent receipt is required and not attached,
    # MODEL_ONLY is legally disallowed and bounded to minimal exact receipt retrieval.
    if (
        obligation == "independent_receipt_required"
        and p_receipt < 0.70
        and route_candidate == "MODEL_ONLY"
    ):
        route_candidate = "EXACT"

    # Multi-primitive decision hierarchy:
    # 1. Dependency signal elevated
    if p_dep >= 0.60 or route_candidate == "GRAPH":
        final_route: Route = "GRAPH"
        confidence = max(p_dep, cand_conf)
    # 2. Staleness/temporal signal elevated
    elif p_stale >= 0.60 or route_candidate == "TEMPORAL":
        final_route = "TEMPORAL"
        confidence = max(p_stale, cand_conf)
    else:
        final_route = route_candidate
        confidence = cand_conf

    return SemanticRouteResult(
        route=final_route,
        confidence=round(confidence, 4),
        probabilities=cand_probs,
        provider="typesafe",
        model="jev-multi-primitive",
    )


def typesafe_multi_route(case: GeneratedCase, mode: str = "latent") -> SemanticRouteResult:
    """Run parallel multi-primitive TypeSafe evaluation over latent context.

    Asks independent Nouls and Choices concurrently in one request, preserving
    probability distributions, while WorldLoop owns the deterministic composition.
    """
    try:
        from typesafe_sdk import TypeSafeClient
    except ImportError as exc:  # pragma: no cover - optional sponsor dependency
        raise RuntimeError(
            "TypeSafe SDK is not installed; install the sponsors extra or `uv add typesafe-sdk`"
        ) from exc

    state = routing_state(case, mode=mode)
    with TypeSafeClient() as client:
        response = client.system_one(
            state=state,
            questions=typesafe_multi_questions(),
        )

    nouls = {k: float(getattr(v, "noul", v)) for k, v in getattr(response, "nouls", {}).items()}
    choices = getattr(response, "choices", {})
    return compose_typesafe_policy(
        nouls,
        choices,
        obligation=state.get("evidence_obligation", "independent_receipt_required"),
    )


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
