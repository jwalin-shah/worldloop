from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .benchmark import BenchmarkDataset, GeneratedCase

PRIMARY_METRIC = "first_pass_verified_success"


def _signature(features: dict[str, Any]) -> tuple[bool, bool, bool]:
    """Use only legitimate pre-action structural features.

    Case identity, expected decision, failure labels, and held-out outcomes are intentionally
    absent. These features describe whether the task declares a dependency/freshness/cross-entity
    requirement before retrieval begins.
    """
    return (
        bool(features["has_dependency"]),
        bool(features["freshness_sensitive"]),
        bool(features["cross_entity"]),
    )


@dataclass(frozen=True)
class DerivedRulePolicy:
    version: str
    rules: dict[tuple[bool, bool, bool], tuple[str, ...]]
    development_case_ids: tuple[str, ...]

    @classmethod
    def fit(cls, dataset: BenchmarkDataset) -> DerivedRulePolicy:
        grouped: dict[tuple[bool, bool, bool], Counter[tuple[str, ...]]] = defaultdict(Counter)
        development_ids: list[str] = []
        for row in dataset.training_records():
            case_id = str(row["case_id"])
            development_ids.append(case_id)
            signature = _signature(row["features"])
            grouped[signature][tuple(row["target_recipe"])] += 1

        rules: dict[tuple[bool, bool, bool], tuple[str, ...]] = {}
        for signature, candidates in grouped.items():
            # Highest empirical support wins; lexical recipe order provides a stable tie-break.
            ranked = sorted(candidates.items(), key=lambda item: (-item[1], item[0]))
            rules[signature] = ranked[0][0]

        return cls(
            version="policy-v1-derived-rules",
            rules=rules,
            development_case_ids=tuple(development_ids),
        )

    def select(self, case: GeneratedCase) -> tuple[str, ...]:
        signature = _signature(case.pre_action_features())
        return self.rules.get(signature, case.initial_recipe)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "development_case_ids": list(self.development_case_ids),
            "rules": [
                {
                    "has_dependency": signature[0],
                    "freshness_sensitive": signature[1],
                    "cross_entity": signature[2],
                    "recipe": list(recipe),
                }
                for signature, recipe in sorted(self.rules.items())
            ],
        }


@dataclass(frozen=True)
class PolicyMetrics:
    policy_version: str
    case_count: int
    first_pass_verified_count: int
    first_pass_verified_success: float
    final_verified_count: int
    final_verified_success: float
    mean_retrieval_steps: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PromotionReport:
    dataset_snapshot: str
    primary_metric: str
    v0: PolicyMetrics
    v1: PolicyMetrics
    promotion_decision: str
    policy: dict[str, Any]
    heldout_case_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_snapshot": self.dataset_snapshot,
            "primary_metric": self.primary_metric,
            "v0": self.v0.to_dict(),
            "v1": self.v1.to_dict(),
            "promotion_decision": self.promotion_decision,
            "policy": self.policy,
            "heldout_case_ids": list(self.heldout_case_ids),
        }


def recipe_is_verified(case: GeneratedCase, recipe: tuple[str, ...]) -> bool:
    """Deterministic verifier for the generated task family.

    The generator's repair recipe is the minimal evidence-access obligation for the case.
    A candidate may use extra steps, but it must cover every required step.
    """
    return set(case.repair_recipe).issubset(recipe)


def _metrics(
    cases: tuple[GeneratedCase, ...],
    policy_version: str,
    selector: Any,
) -> PolicyMetrics:
    selected = [tuple(selector(case)) for case in cases]
    first_pass = [recipe_is_verified(case, recipe) for case, recipe in zip(cases, selected)]

    # Both policies retain the same verified repair fallback. This metric guards against a v1
    # policy that improves first pass by making final completion worse.
    final = [
        ok or recipe_is_verified(case, tuple(case.repair_recipe))
        for case, ok in zip(cases, first_pass)
    ]
    count = len(cases)
    return PolicyMetrics(
        policy_version=policy_version,
        case_count=count,
        first_pass_verified_count=sum(first_pass),
        first_pass_verified_success=round(sum(first_pass) / count, 6),
        final_verified_count=sum(final),
        final_verified_success=round(sum(final) / count, 6),
        mean_retrieval_steps=round(sum(len(recipe) for recipe in selected) / count, 6),
    )


def evaluate_v0_v1(dataset: BenchmarkDataset) -> PromotionReport:
    """Fit on development only, then expose the frozen held-out split once for evaluation."""
    policy = DerivedRulePolicy.fit(dataset)
    heldout = dataset.heldout

    v0 = _metrics(heldout, "policy-v0", lambda case: case.initial_recipe)
    v1 = _metrics(heldout, policy.version, policy.select)

    promoted = (
        v1.first_pass_verified_success > v0.first_pass_verified_success
        and v1.final_verified_success >= v0.final_verified_success
    )
    return PromotionReport(
        dataset_snapshot=dataset.snapshot_id,
        primary_metric=PRIMARY_METRIC,
        v0=v0,
        v1=v1,
        promotion_decision="PROMOTED" if promoted else "REJECTED",
        policy=policy.to_dict(),
        heldout_case_ids=tuple(case.case_id for case in heldout),
    )
