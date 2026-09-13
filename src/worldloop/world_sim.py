from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from .models import Evidence

Decision = Literal["APPROVE", "BLOCK", "ESCALATE", "ABSTAIN"]
RiskBand = Literal["low", "medium", "high", "critical"]


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class WorldGroundTruth:
    task_id: str
    target_entity: str
    as_of: str
    expected_decision: Decision
    risk_band: RiskBand
    has_active_blocker: bool
    dependency: str | None
    dependency_healthy: bool
    is_information_complete: bool
    minimal_evidence_ids: tuple[str, ...]
    stale_evidence_ids: tuple[str, ...]
    distractor_evidence_ids: tuple[str, ...]
    explanation: str


class OperationalWorld:
    """Simulates a causal, partially-observable operational world with evolving state.

    The world contains services, dependency topologies, risk tiers, and incident timelines.
    Events can be superseded (e.g. an incident resolution superseding an active alert).
    Distractor noise (unrelated alerts, stale maintenance notices) is injected to test
    retrieval selectivity.
    """

    def __init__(self, seed: int = 20260913):
        self.seed = seed
        self.rng = random.Random(seed)
        self.evidence_by_id: dict[str, Evidence] = {}
        self.all_evidence: list[Evidence] = []
        self.ground_truths: dict[str, WorldGroundTruth] = {}

    def _add_evidence(self, ev: Evidence) -> None:
        self.evidence_by_id[ev.evidence_id] = ev
        self.all_evidence.append(ev)

    def generate_universe(
        self,
        split: Literal["development", "heldout"],
        task_count: int = 60,
    ) -> list[dict[str, Any]]:
        """Generates a complete operational universe for the given split.

        Returns a list of task specifications (with zero oracle leaks).
        """
        prefix = "dev" if split == "development" else "heldout"
        stem = "Aurora" if split == "development" else "Orion"
        dep_stem = "Atlas" if split == "development" else "Lyra"
        base_time = (
            datetime(2026, 1, 10, 8, tzinfo=UTC)
            if split == "development"
            else datetime(2026, 8, 15, 8, tzinfo=UTC)
        )

        task_specs: list[dict[str, Any]] = []

        scenarios = [
            "clean_approve",
            "direct_block",
            "superseded_block",
            "dependency_degraded",
            "high_risk_escalate",
            "missing_info_abstain",
            "noisy_clean",
            "noisy_blocked",
        ]

        for idx in range(task_count):
            task_id = f"{prefix}-{idx:03d}"
            project = f"{stem}-{idx:03d}"
            dep_name = f"{dep_stem}-{idx:03d}" if idx % 2 == 0 else None
            scenario = scenarios[idx % len(scenarios)]

            task_time = base_time + timedelta(days=idx, hours=self.rng.randint(2, 14))
            as_of_dt = task_time + timedelta(hours=self.rng.randint(8, 16))
            as_of_str = _iso(as_of_dt)

            gt = self._materialize_scenario(
                task_id=task_id,
                project=project,
                dependency=dep_name,
                scenario=scenario,
                task_time=task_time,
                as_of_dt=as_of_dt,
                as_of_str=as_of_str,
                prefix=prefix,
                idx=idx,
            )
            self.ground_truths[task_id] = gt

            context_prose = self._synthesize_context_prose(
                project=project,
                dependency=dep_name,
                scenario=scenario,
                risk_band=gt.risk_band,
                as_of_str=as_of_str,
            )

            task_specs.append(
                {
                    "task_id": task_id,
                    "split": split,
                    "target_entity": project,
                    "as_of": as_of_str,
                    "question": f"Can {project} proceed with production release as of {as_of_str}?",
                    "context_brief": context_prose,
                    "risk_band": gt.risk_band,
                    "dependency": dep_name,
                }
            )

        return task_specs

    def _materialize_scenario(
        self,
        task_id: str,
        project: str,
        dependency: str | None,
        scenario: str,
        task_time: datetime,
        as_of_dt: datetime,
        as_of_str: str,
        prefix: str,
        idx: int,
    ) -> WorldGroundTruth:
        minimal_ids: list[str] = []
        stale_ids: list[str] = []
        distractor_ids: list[str] = []

        # 1. Base Policy
        policy_id = f"ev:{prefix}:{idx:03d}:policy"
        policy_ev = Evidence(
            evidence_id=policy_id,
            entity=project,
            text=(
                f"Governance Policy: Service {project} requires risk verification, blocker check, "
                f"and upstream dependency validation. Active blockers require BLOCK. "
                f"Critical risk or high risk under change requires ESCALATE. "
                f"Missing critical telemetry requires ABSTAIN. Otherwise APPROVE."
            ),
            event_time=_iso(task_time - timedelta(days=30)),
            observed_time=_iso(task_time - timedelta(days=30)),
            source="policy://release-governance/v2",
            tags=("policy", "governance"),
        )
        self._add_evidence(policy_ev)
        minimal_ids.append(policy_id)

        # 2. Risk Assessment
        risk_map: dict[str, RiskBand] = {
            "clean_approve": "low" if idx % 2 == 0 else "medium",
            "direct_block": "medium",
            "superseded_block": "low",
            "dependency_degraded": "medium",
            "high_risk_escalate": "high" if idx % 2 == 0 else "critical",
            "missing_info_abstain": "medium",
            "noisy_clean": "low",
            "noisy_blocked": "high",
        }
        risk = risk_map[scenario]

        if scenario != "missing_info_abstain" or idx % 2 != 0:
            risk_id = f"ev:{prefix}:{idx:03d}:risk"
            risk_ev = Evidence(
                evidence_id=risk_id,
                entity=project,
                text=f"Service Registry: {project} security & architectural risk tier classified as '{risk}'.",
                event_time=_iso(task_time - timedelta(days=2)),
                observed_time=_iso(task_time - timedelta(days=2)),
                source="registry://risk-tiers",
                tags=("risk", "registry", risk),
            )
            self._add_evidence(risk_ev)
            minimal_ids.append(risk_id)

        # 3. Status & Incidents
        has_blocker = False
        if scenario in {"direct_block", "noisy_blocked"}:
            inc_id = f"ev:{prefix}:{idx:03d}:incident:active"
            inc_ev = Evidence(
                evidence_id=inc_id,
                entity=project,
                text=f"Alert Incident: Critical regression detected on {project}. Status: ACTIVE BLOCKER.",
                event_time=_iso(task_time + timedelta(hours=2)),
                observed_time=_iso(task_time + timedelta(hours=2, minutes=3)),
                source="alert://datadog-incidents",
                tags=("incident", "blocker", "active"),
            )
            self._add_evidence(inc_ev)
            minimal_ids.append(inc_id)
            has_blocker = True

        elif scenario == "superseded_block":
            old_inc_id = f"ev:{prefix}:{idx:03d}:incident:morning"
            old_inc_ev = Evidence(
                evidence_id=old_inc_id,
                entity=project,
                text=f"Alert Incident: Memory leak alert triggered on {project}. Status: BLOCKER.",
                event_time=_iso(task_time + timedelta(hours=1)),
                observed_time=_iso(task_time + timedelta(hours=1, minutes=2)),
                source="alert://datadog-incidents",
                tags=("incident", "blocker", "stale"),
            )
            self._add_evidence(old_inc_ev)
            stale_ids.append(old_inc_id)

            patch_id = f"ev:{prefix}:{idx:03d}:incident:patch-resolved"
            patch_ev = Evidence(
                evidence_id=patch_id,
                entity=project,
                text=(
                    f"Remediation Log: Hotfix deployed for {project}. Memory leak mitigated. "
                    f"Supersedes previous alert {old_inc_id}. All diagnostic health checks clear."
                ),
                event_time=_iso(task_time + timedelta(hours=5)),
                observed_time=_iso(task_time + timedelta(hours=5, minutes=5)),
                source="incident://remediation-timeline",
                links=(old_inc_id,),
                tags=("remediation", "resolved", "clear"),
            )
            self._add_evidence(patch_ev)
            minimal_ids.append(patch_id)
            has_blocker = False

        elif scenario in {"clean_approve", "high_risk_escalate", "noisy_clean"}:
            status_id = f"ev:{prefix}:{idx:03d}:status:green"
            status_ev = Evidence(
                evidence_id=status_id,
                entity=project,
                text=f"Diagnostic Audit: {project} passed all integration and boundary tests. No active incidents.",
                event_time=_iso(task_time + timedelta(hours=3)),
                observed_time=_iso(task_time + timedelta(hours=3, minutes=2)),
                source="audit://ci-cd-verifier",
                tags=("status", "clean", "passed"),
            )
            self._add_evidence(status_ev)
            minimal_ids.append(status_id)
            has_blocker = False

        # 4. Dependencies
        dep_healthy = True
        if dependency:
            link_id = f"ev:{prefix}:{idx:03d}:dep-link"
            link_ev = Evidence(
                evidence_id=link_id,
                entity=project,
                text=f"Architecture Graph: {project} has runtime dependency on upstream service {dependency}.",
                event_time=_iso(task_time - timedelta(days=5)),
                observed_time=_iso(task_time - timedelta(days=5)),
                source="topology://service-graph",
                links=(dependency,),
                tags=("topology", "dependency"),
            )
            self._add_evidence(link_ev)
            minimal_ids.append(link_id)

            if scenario == "dependency_degraded":
                dep_health_id = f"ev:{prefix}:{idx:03d}:dep-health:failed"
                dep_health_ev = Evidence(
                    evidence_id=dep_health_id,
                    entity=dependency,
                    text=(
                        f"Component Telemetry: Upstream dependency {dependency} reporting 503 error rates "
                        f"exceeding SLA threshold (8.4%). Cluster DEGRADED."
                    ),
                    event_time=_iso(task_time + timedelta(hours=4)),
                    observed_time=_iso(task_time + timedelta(hours=4, minutes=4)),
                    source="telemetry://cluster-health",
                    tags=("dependency", "telemetry", "degraded"),
                )
                self._add_evidence(dep_health_ev)
                minimal_ids.append(dep_health_id)
                dep_healthy = False
            elif scenario != "missing_info_abstain" or idx % 2 == 0:
                dep_health_id = f"ev:{prefix}:{idx:03d}:dep-health:ok"
                dep_health_ev = Evidence(
                    evidence_id=dep_health_id,
                    entity=dependency,
                    text=f"Component Telemetry: {dependency} cluster operating nominally. Latency p99 < 15ms. HEALTHY.",
                    event_time=_iso(task_time + timedelta(hours=4)),
                    observed_time=_iso(task_time + timedelta(hours=4, minutes=2)),
                    source="telemetry://cluster-health",
                    tags=("dependency", "telemetry", "healthy"),
                )
                self._add_evidence(dep_health_ev)
                minimal_ids.append(dep_health_id)
                dep_healthy = True
            else:
                dep_healthy = False

        # 5. Distractor Noise Injection
        if scenario in {"noisy_clean", "noisy_blocked", "superseded_block"}:
            for noise_i in range(self.rng.randint(2, 4)):
                dist_id = f"ev:{prefix}:{idx:03d}:noise:{noise_i}"
                dist_entity = f"Peripheral-{idx:03d}-{noise_i}"
                dist_ev = Evidence(
                    evidence_id=dist_id,
                    entity=dist_entity,
                    text=(
                        f"Routine log notice for {dist_entity}: routine log rotation completed. "
                        f"Unrelated background daemon heartbeat at standard interval."
                    ),
                    event_time=_iso(task_time - timedelta(hours=noise_i * 3)),
                    observed_time=_iso(task_time - timedelta(hours=noise_i * 3)),
                    source="system://cron-heartbeat",
                    tags=("distractor", "noise"),
                )
                self._add_evidence(dist_ev)
                distractor_ids.append(dist_id)

        # 6. Compute Ground Truth Decision
        info_complete = scenario != "missing_info_abstain"

        if not info_complete:
            decision: Decision = "ABSTAIN"
            explanation = "Critical telemetry or risk classification is missing from the world."
        elif has_blocker or not dep_healthy:
            decision = "BLOCK"
            explanation = "Active blocker or degraded upstream dependency prohibits release."
        elif risk in {"high", "critical"}:
            decision = "ESCALATE"
            explanation = f"Risk band is '{risk}', which mandates escalation under governance policy."
        else:
            decision = "APPROVE"
            explanation = f"All pre-conditions clear, no active blockers, risk is '{risk}'."

        return WorldGroundTruth(
            task_id=task_id,
            target_entity=project,
            as_of=as_of_str,
            expected_decision=decision,
            risk_band=risk,
            has_active_blocker=has_blocker,
            dependency=dependency,
            dependency_healthy=dep_healthy,
            is_information_complete=info_complete,
            minimal_evidence_ids=tuple(minimal_ids),
            stale_evidence_ids=tuple(stale_ids),
            distractor_evidence_ids=tuple(distractor_ids),
            explanation=explanation,
        )

    @staticmethod
    def _synthesize_context_prose(
        project: str,
        dependency: str | None,
        scenario: str,
        risk_band: RiskBand,
        as_of_str: str,
    ) -> str:
        """Synthesizes natural, human-written operational context without formulaic keywords."""
        lines = [f"Deployment request for {project} (target timestamp {as_of_str})."]
        if dependency:
            lines.append(f"Service architecture indicates integration with {dependency}.")

        if scenario == "superseded_block":
            lines.append(
                "An earlier automated monitor raised a flag regarding thread contention. "
                "Engineering logged a follow-up intervention prior to release window. "
                "Current state must be verified from the latest timeline event."
            )
        elif scenario == "dependency_degraded":
            lines.append(
                f"Release requires verifying both local component state and the stability SLA "
                f"of external upstream component {dependency}."
            )
        elif scenario == "high_risk_escalate":
            lines.append(
                "Service is categorized under sensitive risk requirements. "
                "Governance rules dictate specific handling according to classification."
            )
        elif scenario == "missing_info_abstain":
            lines.append(
                "Telemetry collection for this cluster is experiencing partial reporting gaps. "
                "Verify whether evidence is sufficient to certify deployment readiness."
            )
        elif scenario in {"direct_block", "noisy_blocked"}:
            lines.append(
                "Routine release pipeline triggered following weekly sprint cut. "
                "Standard pre-flight verification across alerting and health registries applies."
            )
        else:
            lines.append(
                "Routine operational rollout requested. Verify risk rating and registry records."
            )

        return " ".join(lines)
