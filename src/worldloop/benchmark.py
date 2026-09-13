from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

DATASET_VERSION = "worldloop.change-aware-rollout.v1"
DEFAULT_SEED = 20260912
DEFAULT_DEV_COUNT = 45
DEFAULT_HELDOUT_COUNT = 21

Split = Literal["development", "heldout"]
Decision = Literal["APPROVE", "BLOCK", "ESCALATE"]


@dataclass(frozen=True)
class GeneratedEvidence:
    evidence_id: str
    entity: str
    kind: str
    value: str
    event_time: str
    observed_time: str
    source: str
    links: tuple[str, ...] = ()
    supersedes: str | None = None


@dataclass(frozen=True)
class GeneratedCase:
    case_id: str
    split: Split
    task_family: str
    project: str
    dependency: str | None
    question: str
    as_of: str
    risk_band: str
    expected_decision: Decision
    required_evidence: tuple[str, ...]
    initial_recipe: tuple[str, ...]
    repair_recipe: tuple[str, ...]
    failure_class: str
    feature_flags: tuple[str, ...]

    @property
    def context_prose(self) -> str:
        """Synthesizes unstructured operational prose containing latent evidence."""
        if self.failure_class == "temporal_staleness":
            return (
                f"Operational brief for {self.project} (risk band: {self.risk_band}, as-of: {self.as_of}). "
                f"Initial incident audit recorded an earlier blocker status. A newer timeline update "
                f"was subsequently published superseding earlier logs. Policy specifies that stale evidence "
                f"cannot certify readiness."
            )
        if self.failure_class == "cross_entity_join":
            dep = self.dependency or "upstream-service"
            return (
                f"Operational brief for {self.project} (risk band: {self.risk_band}, as-of: {self.as_of}). "
                f"Service architecture maps an active operational dependency to external component {dep}. "
                f"Verification requires traversing the dependency graph to resolve {dep}'s stability."
            )
        return (
            f"Operational brief for {self.project} (risk band: {self.risk_band}, as-of: {self.as_of}). "
            f"Registry status is confirmed clear with zero open incidents. No cross-entity dependencies "
            f"are linked. Direct routine rollout verification applies."
        )

    def pre_action_features(self, mode: str = "legacy") -> dict[str, Any]:
        """Features legitimately available before executing a retrieval policy."""
        payload: dict[str, Any] = {
            "case_id": self.case_id,
            "task_family": self.task_family,
            "question": self.question,
            "risk_band": self.risk_band,
            "context_prose": self.context_prose,
        }
        if mode == "legacy":
            payload.update(
                {
                    "has_dependency": self.dependency is not None,
                    "freshness_sensitive": "freshness_sensitive" in self.feature_flags,
                    "cross_entity": "cross_entity" in self.feature_flags,
                }
            )
        return payload


@dataclass(frozen=True)
class BenchmarkDataset:
    version: str
    seed: int
    development: tuple[GeneratedCase, ...]
    heldout: tuple[GeneratedCase, ...]
    evidence: tuple[GeneratedEvidence, ...]

    @property
    def snapshot_id(self) -> str:
        digest = sha256(self._canonical_payload().encode()).hexdigest()[:16]
        return f"{self.version}:{digest}"

    def _canonical_payload(self) -> str:
        payload = {
            "version": self.version,
            "seed": self.seed,
            "development": [asdict(case) for case in self.development],
            "heldout": [asdict(case) for case in self.heldout],
            "evidence": [asdict(item) for item in self.evidence],
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def training_records(self) -> list[dict[str, Any]]:
        """Development-only rows for downstream policy derivation.

        Held-out cases are intentionally unreachable from this method. The target is the
        development repair recipe, while features are restricted to pre-action metadata.
        """
        return [
            {
                "case_id": case.case_id,
                "features": case.pre_action_features(),
                "target_recipe": list(case.repair_recipe),
            }
            for case in self.development
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "seed": self.seed,
            "snapshot_id": self.snapshot_id,
            "development_count": len(self.development),
            "heldout_count": len(self.heldout),
            "development": [asdict(case) for case in self.development],
            "heldout": [asdict(case) for case in self.heldout],
            "evidence": [asdict(item) for item in self.evidence],
        }


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _case_prefix(split: Split) -> str:
    return "dev" if split == "development" else "heldout"


def _project_name(split: Split, index: int) -> str:
    # Split-specific namespaces make trivial entity memorization impossible across the split.
    stem = "Aurora" if split == "development" else "Orion"
    return f"{stem}-{index:03d}"


def _dependency_name(split: Split, index: int) -> str:
    stem = "Atlas" if split == "development" else "Lyra"
    return f"{stem}-{index:03d}"


def _base_time(split: Split) -> datetime:
    # Held-out time clusters are months away from development time clusters.
    if split == "development":
        return datetime(2026, 1, 5, 9, tzinfo=UTC)
    return datetime(2026, 7, 6, 9, tzinfo=UTC)


def _risk_band(index: int) -> str:
    return ("low", "medium", "high")[index % 3]


def _decision(blocked: bool, risk_band: str) -> Decision:
    if blocked:
        return "BLOCK"
    if risk_band == "high":
        return "ESCALATE"
    return "APPROVE"


def _make_case(split: Split, index: int) -> tuple[GeneratedCase, list[GeneratedEvidence]]:
    prefix = _case_prefix(split)
    project = _project_name(split, index)
    dependency = _dependency_name(split, index)
    risk_band = _risk_band(index)
    base = _base_time(split) + timedelta(days=index * 2)
    as_of = base + timedelta(hours=18)
    pattern = index % 3
    evidence: list[GeneratedEvidence] = []

    policy_id = f"{prefix}-{index:03d}-policy"
    policy = GeneratedEvidence(
        evidence_id=policy_id,
        entity=project,
        kind="rollout_policy",
        value="high-risk requires escalation; active blocker requires block; otherwise approve",
        event_time=_iso(base - timedelta(days=30)),
        observed_time=_iso(base - timedelta(days=30)),
        source="policy://rollout/v1",
    )
    evidence.append(policy)

    risk_id = f"{prefix}-{index:03d}-risk"
    evidence.append(
        GeneratedEvidence(
            evidence_id=risk_id,
            entity=project,
            kind="risk_band",
            value=risk_band,
            event_time=_iso(base),
            observed_time=_iso(base + timedelta(minutes=5)),
            source="registry://risk",
        )
    )

    if pattern == 0:
        # Temporal-staleness case: an older blocked status is superseded by a newer status.
        old_id = f"{prefix}-{index:03d}-status-old"
        current_id = f"{prefix}-{index:03d}-status-current"
        blocked_now = index % 2 == 0
        evidence.extend(
            [
                GeneratedEvidence(
                    evidence_id=old_id,
                    entity=project,
                    kind="blocker_status",
                    value="active" if not blocked_now else "clear",
                    event_time=_iso(base + timedelta(hours=1)),
                    observed_time=_iso(base + timedelta(hours=1, minutes=5)),
                    source="incident://timeline",
                ),
                GeneratedEvidence(
                    evidence_id=current_id,
                    entity=project,
                    kind="blocker_status",
                    value="active" if blocked_now else "clear",
                    event_time=_iso(base + timedelta(hours=12)),
                    observed_time=_iso(base + timedelta(hours=12, minutes=5)),
                    source="incident://timeline",
                    supersedes=old_id,
                ),
            ]
        )
        required = (policy_id, risk_id, current_id)
        initial_recipe = ("vector",)
        repair_recipe = ("vector", "temporal")
        failure_class = "temporal_staleness"
        feature_flags = ("freshness_sensitive",)
        dependency_for_case: str | None = None
        blocked = blocked_now
    elif pattern == 1:
        # Cross-entity join: project readiness depends on a linked dependency's blocker state.
        link_id = f"{prefix}-{index:03d}-dependency-link"
        dep_status_id = f"{prefix}-{index:03d}-dependency-status"
        blocked = index % 4 != 1
        evidence.extend(
            [
                GeneratedEvidence(
                    evidence_id=link_id,
                    entity=project,
                    kind="dependency_link",
                    value=dependency,
                    event_time=_iso(base + timedelta(hours=2)),
                    observed_time=_iso(base + timedelta(hours=2, minutes=5)),
                    source="graph://dependencies",
                    links=(dependency,),
                ),
                GeneratedEvidence(
                    evidence_id=dep_status_id,
                    entity=dependency,
                    kind="blocker_status",
                    value="active" if blocked else "clear",
                    event_time=_iso(base + timedelta(hours=10)),
                    observed_time=_iso(base + timedelta(hours=10, minutes=5)),
                    source="incident://dependencies",
                    links=(project,),
                ),
            ]
        )
        required = (policy_id, risk_id, link_id, dep_status_id)
        initial_recipe = ("vector",)
        repair_recipe = ("vector", "graph")
        failure_class = "cross_entity_join"
        feature_flags = ("cross_entity",)
        dependency_for_case = dependency
    else:
        # Straightforward exact case acts as a control where broad semantic routing is unnecessary.
        status_id = f"{prefix}-{index:03d}-status"
        blocked = False
        evidence.append(
            GeneratedEvidence(
                evidence_id=status_id,
                entity=project,
                kind="blocker_status",
                value="clear",
                event_time=_iso(base + timedelta(hours=8)),
                observed_time=_iso(base + timedelta(hours=8, minutes=5)),
                source="registry://rollout-status",
            )
        )
        required = (policy_id, risk_id, status_id)
        initial_recipe = ("exact",)
        repair_recipe = ("exact",)
        failure_class = "none"
        feature_flags = ()
        dependency_for_case = None

    expected = _decision(blocked=blocked, risk_band=risk_band)
    case = GeneratedCase(
        case_id=f"{prefix}-{index:03d}",
        split=split,
        task_family="change_aware_rollout",
        project=project,
        dependency=dependency_for_case,
        question=f"Should {project} be approved for rollout as of {_iso(as_of)}?",
        as_of=_iso(as_of),
        risk_band=risk_band,
        expected_decision=expected,
        required_evidence=required,
        initial_recipe=initial_recipe,
        repair_recipe=repair_recipe,
        failure_class=failure_class,
        feature_flags=feature_flags,
    )
    return case, evidence


def generate_benchmark(
    *,
    seed: int = DEFAULT_SEED,
    development_count: int = DEFAULT_DEV_COUNT,
    heldout_count: int = DEFAULT_HELDOUT_COUNT,
) -> BenchmarkDataset:
    """Generate a deterministic rollout-readiness benchmark.

    `seed` is part of the snapshot identity even though v1 intentionally avoids pseudo-random
    sampling. This makes future randomized versions comparable without changing the contract.
    """
    if not 30 <= development_count <= 60:
        raise ValueError("development_count must be between 30 and 60")
    if not 15 <= heldout_count <= 30:
        raise ValueError("heldout_count must be between 15 and 30")

    development: list[GeneratedCase] = []
    heldout: list[GeneratedCase] = []
    evidence: list[GeneratedEvidence] = []

    for split, count, target in (
        ("development", development_count, development),
        ("heldout", heldout_count, heldout),
    ):
        for index in range(1, count + 1):
            case, items = _make_case(split, index)
            target.append(case)
            evidence.extend(items)

    return BenchmarkDataset(
        version=DATASET_VERSION,
        seed=seed,
        development=tuple(development),
        heldout=tuple(heldout),
        evidence=tuple(evidence),
    )


def write_snapshot(path: str | Path, dataset: BenchmarkDataset | None = None) -> Path:
    dataset = dataset or generate_benchmark()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dataset.to_dict(), indent=2, sort_keys=True) + "\n")
    return target
