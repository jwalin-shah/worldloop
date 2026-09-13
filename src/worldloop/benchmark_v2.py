from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from .models import Evidence
from .world_sim import OperationalWorld

BENCHMARK_V2_VERSION = "worldloop.benchmark-v2.falsification.v1"
DEFAULT_SEED = 20260913
DEV_COUNT = 60
HELDOUT_COUNT = 60


@dataclass(frozen=True)
class BenchmarkCaseV2:
    """Benchmark V2 task presented to routers and solvers.

    ZERO ORACLE INVARIANT: This object strictly omits:
    - expected_answer / expected_decision
    - failure_class / repair_recipe / initial_recipe
    - required_evidence
    - formulaic boolean feature flags
    """

    task_id: str
    split: Literal["development", "heldout"]
    target_entity: str
    as_of: str
    question: str
    context_brief: str
    risk_band: str
    dependency: str | None
    task_family: str = "change-aware-rollout"

    @property
    def case_id(self) -> str:
        return self.task_id

    @property
    def context_prose(self) -> str:
        return self.context_brief

    @property
    def adversarial_context_prose(self) -> str:
        return self.context_brief

    def pre_action_features(self, mode: str = "adversarial") -> dict[str, Any]:
        return {
            "case_id": self.task_id,
            "task_family": self.task_family,
            "question": self.question,
            "risk_band": self.risk_band,
            "context_prose": self.context_brief,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkDatasetV2:
    version: str
    seed: int
    development: tuple[BenchmarkCaseV2, ...]
    heldout: tuple[BenchmarkCaseV2, ...]
    evidence: tuple[Evidence, ...]

    @property
    def snapshot_id(self) -> str:
        payload = {
            "version": self.version,
            "seed": self.seed,
            "development": [c.to_dict() for c in self.development],
            "heldout": [c.to_dict() for c in self.heldout],
            "evidence_count": len(self.evidence),
        }
        digest = sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
        return f"{self.version}:{digest}"

    def save_fixtures(self, fixture_dir: Path) -> None:
        fixture_dir.mkdir(parents=True, exist_ok=True)
        cases_payload = {
            "version": self.version,
            "seed": self.seed,
            "snapshot_id": self.snapshot_id,
            "development": [c.to_dict() for c in self.development],
            "heldout": [c.to_dict() for c in self.heldout],
        }
        (fixture_dir / "cases.json").write_text(json.dumps(cases_payload, indent=2))

        evidence_payload = [
            {
                "evidence_id": e.evidence_id,
                "entity": e.entity,
                "text": e.text,
                "event_time": e.event_time,
                "observed_time": e.observed_time,
                "source": e.source,
                "links": list(e.links),
                "tags": list(e.tags),
            }
            for e in self.evidence
        ]
        (fixture_dir / "evidence.json").write_text(json.dumps(evidence_payload, indent=2))


def generate_benchmark_v2(
    seed: int = DEFAULT_SEED,
    dev_count: int = DEV_COUNT,
    heldout_count: int = HELDOUT_COUNT,
) -> tuple[BenchmarkDatasetV2, OperationalWorld]:
    """Generates the Benchmark V2 dataset and the underlying causal world simulator."""
    world = OperationalWorld(seed=seed)
    dev_specs = world.generate_universe(split="development", task_count=dev_count)
    heldout_specs = world.generate_universe(split="heldout", task_count=heldout_count)

    dev_cases = tuple(
        BenchmarkCaseV2(
            task_id=s["task_id"],
            split="development",
            target_entity=s["target_entity"],
            as_of=s["as_of"],
            question=s["question"],
            context_brief=s["context_brief"],
            risk_band=s["risk_band"],
            dependency=s["dependency"],
        )
        for s in dev_specs
    )

    heldout_cases = tuple(
        BenchmarkCaseV2(
            task_id=s["task_id"],
            split="heldout",
            target_entity=s["target_entity"],
            as_of=s["as_of"],
            question=s["question"],
            context_brief=s["context_brief"],
            risk_band=s["risk_band"],
            dependency=s["dependency"],
        )
        for s in heldout_specs
    )

    dataset = BenchmarkDatasetV2(
        version=BENCHMARK_V2_VERSION,
        seed=seed,
        development=dev_cases,
        heldout=heldout_cases,
        evidence=tuple(world.all_evidence),
    )

    return dataset, world
