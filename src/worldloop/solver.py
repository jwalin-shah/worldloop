from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Literal

import httpx

from .benchmark_v2 import BenchmarkCaseV2
from .models import Evidence

Decision = Literal["APPROVE", "BLOCK", "ESCALATE", "ABSTAIN"]


@dataclass(frozen=True)
class SolverDecision:
    task_id: str
    decision: Decision
    confidence: float
    rationale: str
    cited_evidence_ids: tuple[str, ...]
    retrieval_steps: tuple[str, ...]
    retrieved_count: int
    solver_type: str
    latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DeterministicSolver:
    """Typed deterministic operational reasoner.

    Analyzes retrieved evidence to determine release readiness.
    Operates strictly on retrieved items — no oracle access to the world state.
    """

    @classmethod
    def solve(
        cls,
        case: BenchmarkCaseV2,
        retrieved_evidence: list[Evidence],
        retrieval_steps: tuple[str, ...] = (),
    ) -> SolverDecision:
        t0 = time.perf_counter()
        target = case.target_entity
        as_of = case.as_of

        # Filter evidence to items valid up to as_of
        valid_items = [e for e in retrieved_evidence if e.event_time <= as_of]

        # 1. Identify Risk Band
        risk_ev = None
        for e in valid_items:
            if ("registry" in e.source or "risk" in e.tags) and (target in e.entity or target in e.text):
                risk_ev = e
                break

        risk_val = "medium"
        if risk_ev:
            for r in ("critical", "high", "medium", "low"):
                if f"'{r}'" in risk_ev.text or f"classified as '{r}'" in risk_ev.text or r in risk_ev.tags:
                    risk_val = r
                    break

        # 2. Identify Incidents & Mitigations (Temporal Resolution)
        incidents: list[Evidence] = []
        mitigations: list[Evidence] = []
        for e in valid_items:
            if target in e.entity:
                if ("alert://" in e.source or "incident" in e.tags) and "policy" not in e.tags and "policy" not in e.source and ("blocker" in e.text.lower() or "active blocker" in e.text.lower()):
                    incidents.append(e)
                if "remediation" in e.source or "resolved" in e.tags or "supersedes" in e.text.lower():
                    mitigations.append(e)

        # Check which incidents are superseded by a mitigation
        superseded_ids: set[str] = set()
        for m in mitigations:
            for link in m.links:
                superseded_ids.add(link)
            # regex match "supersedes ... ev:..."
            matches = re.findall(r"ev:[a-zA-Z0-9_\-:]+", m.text)
            for match in matches:
                superseded_ids.add(match)

        active_blockers = [
            inc for inc in incidents
            if inc.evidence_id not in superseded_ids and "active blocker" in inc.text.lower()
        ]

        # 3. Check Dependencies (Graph Resolution)
        dep_name = case.dependency
        dep_telemetry: list[Evidence] = []
        if dep_name:
            for e in valid_items:
                if (dep_name in e.entity or dep_name in e.text) and ("telemetry" in e.source or "dependency" in e.tags or "healthy" in e.tags or "degraded" in e.tags):
                    dep_telemetry.append(e)

        cited_ids: list[str] = []

        # Decision Logic:
        # A. Unresolved Active Blocker on target
        if active_blockers:
            blocker = active_blockers[0]
            cited_ids.append(blocker.evidence_id)
            if risk_ev:
                cited_ids.append(risk_ev.evidence_id)
            decision: Decision = "BLOCK"
            rationale = f"Active blocker detected on {target} ({blocker.evidence_id}). Release prohibited."
            conf = 0.95

        # B. Dependency degraded
        elif dep_name and any("degraded" in e.text.lower() or "503" in e.text for e in dep_telemetry):
            bad_dep = next(e for e in dep_telemetry if "degraded" in e.text.lower() or "503" in e.text)
            cited_ids.append(bad_dep.evidence_id)
            if risk_ev:
                cited_ids.append(risk_ev.evidence_id)
            decision = "BLOCK"
            rationale = f"Upstream dependency {dep_name} is degraded ({bad_dep.evidence_id}). Release blocked."
            conf = 0.90

        # C. Missing critical evidence
        elif not valid_items or (not risk_ev and not incidents and not mitigations):
            decision = "ABSTAIN"
            rationale = f"Insufficient evidence retrieved for {target} to certify readiness."
            conf = 0.80

        # D. High or Critical Risk
        elif risk_val in ("high", "critical"):
            if risk_ev:
                cited_ids.append(risk_ev.evidence_id)
            for m in mitigations:
                cited_ids.append(m.evidence_id)
            decision = "ESCALATE"
            rationale = f"Target {target} is classified as '{risk_val}' risk. Escalation required by policy."
            conf = 0.90

        # E. Clean / Mitigated
        else:
            if risk_ev:
                cited_ids.append(risk_ev.evidence_id)
            for m in mitigations:
                cited_ids.append(m.evidence_id)
            for d in dep_telemetry:
                if "healthy" in d.text.lower() or "healthy" in d.tags:
                    cited_ids.append(d.evidence_id)
            for e in valid_items:
                if "clean" in e.tags or "passed" in e.tags:
                    cited_ids.append(e.evidence_id)

            decision = "APPROVE"
            rationale = f"All pre-conditions satisfied for {target} (risk: {risk_val}). Zero active blockers."
            conf = 0.95

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return SolverDecision(
            task_id=case.task_id,
            decision=decision,
            confidence=conf,
            rationale=rationale,
            cited_evidence_ids=tuple(dict.fromkeys(cited_ids)),
            retrieval_steps=retrieval_steps,
            retrieved_count=len(retrieved_evidence),
            solver_type="deterministic_typed",
            latency_ms=latency_ms,
        )


class LLMSolver:
    """W&B Hosted Llama 3.3 70B task solver.

    Prompts the LLM to read the retrieved evidence snippets and produce a structured
    decision with exact citations.
    """

    WANDB_URL = "https://api.inference.wandb.ai/v1/chat/completions"
    MODEL = "meta-llama/Llama-3.3-70B-Instruct"

    @classmethod
    def solve(
        cls,
        case: BenchmarkCaseV2,
        retrieved_evidence: list[Evidence],
        retrieval_steps: tuple[str, ...] = (),
        api_key: str | None = None,
        client: httpx.Client | None = None,
    ) -> SolverDecision:
        token = api_key or os.getenv("WANDB_API_KEY")
        if not token:
            # Fallback to deterministic solver if API key not available
            dec = DeterministicSolver.solve(case, retrieved_evidence, retrieval_steps)
            return SolverDecision(
                task_id=dec.task_id,
                decision=dec.decision,
                confidence=dec.confidence,
                rationale=f"[Fallback: WANDB_API_KEY unset] {dec.rationale}",
                cited_evidence_ids=dec.cited_evidence_ids,
                retrieval_steps=retrieval_steps,
                retrieved_count=len(retrieved_evidence),
                solver_type="llm_fallback_deterministic",
                latency_ms=dec.latency_ms,
            )

        t0 = time.perf_counter()
        snippets = []
        for e in retrieved_evidence:
            snippets.append(
                f"- ID: {e.evidence_id}\n  Entity: {e.entity}\n  EventTime: {e.event_time}\n  Source: {e.source}\n  Text: {e.text}"
            )
        evidence_block = "\n\n".join(snippets) if snippets else "None retrieved."

        system_prompt = (
            "You are an autonomous Release Verification Gatekeeper.\n"
            "You must evaluate whether the target service can proceed with deployment based ONLY "
            "on the provided evidence valid up to the target timestamp.\n\n"
            "Operational Governance Rules:\n"
            "1. If an active, un-mitigated blocker exists on the target service or its upstream dependency: emit BLOCK.\n"
            "2. If an earlier alert was superseded/mitigated by a subsequent patch log: the blocker is cleared.\n"
            "3. If risk classification is 'high' or 'critical' and no blockers exist: emit ESCALATE.\n"
            "4. If all checks pass, dependency is healthy, and risk is low/medium: emit APPROVE.\n"
            "5. If evidence is missing, conflicting, or insufficient to verify readiness: emit ABSTAIN.\n\n"
            "Output JSON matching this exact schema:\n"
            "{\n"
            '  "decision": "APPROVE" | "BLOCK" | "ESCALATE" | "ABSTAIN",\n'
            '  "confidence": <float 0.0 to 1.0>,\n'
            '  "rationale": "<concise justification>",\n'
            '  "cited_evidence_ids": ["<exact evidence ID from evidence list>"]\n'
            "}"
        )

        user_prompt = (
            f"Task ID: {case.task_id}\n"
            f"Target Service: {case.target_entity}\n"
            f"Target Timestamp (as_of): {case.as_of}\n"
            f"Context Brief: {case.context_brief}\n\n"
            f"Retrieved Evidence:\n{evidence_block}"
        )

        payload = {
            "model": cls.MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "worldloop-benchmark-v2/1.0",
        }

        try:
            if client:
                resp = client.post(cls.WANDB_URL, headers=headers, json=payload, timeout=30.0)
            else:
                with httpx.Client(timeout=30.0) as default_client:
                    resp = default_client.post(cls.WANDB_URL, headers=headers, json=payload)

            if resp.status_code != 200:
                raise RuntimeError(f"W&B API error {resp.status_code}: {resp.text}")

            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"].strip()

            # Parse JSON block
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
            parsed = json.loads(match.group(1)) if match else json.loads(raw_content)

            dec_str = str(parsed.get("decision", "ABSTAIN")).strip().upper()
            if dec_str not in {"APPROVE", "BLOCK", "ESCALATE", "ABSTAIN"}:
                dec_str = "ABSTAIN"

            cited = tuple(str(x) for x in parsed.get("cited_evidence_ids", []))
            conf = float(parsed.get("confidence", 0.9))
            rationale = str(parsed.get("rationale", ""))
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)

            return SolverDecision(
                task_id=case.task_id,
                decision=dec_str,  # type: ignore
                confidence=conf,
                rationale=rationale,
                cited_evidence_ids=cited,
                retrieval_steps=retrieval_steps,
                retrieved_count=len(retrieved_evidence),
                solver_type="wandb_llama_70b",
                latency_ms=latency_ms,
            )
        except (RuntimeError, httpx.HTTPError, json.JSONDecodeError, KeyError, ValueError) as exc:
            # Fallback on network/API failure
            dec = DeterministicSolver.solve(case, retrieved_evidence, retrieval_steps)
            return SolverDecision(
                task_id=dec.task_id,
                decision=dec.decision,
                confidence=dec.confidence,
                rationale=f"[LLM error fallback: {exc}] {dec.rationale}",
                cited_evidence_ids=dec.cited_evidence_ids,
                retrieval_steps=retrieval_steps,
                retrieved_count=len(retrieved_evidence),
                solver_type="llm_error_fallback",
                latency_ms=dec.latency_ms,
            )
