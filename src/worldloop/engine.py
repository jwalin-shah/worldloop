from __future__ import annotations

import json
from pathlib import Path

from .ir import NodeSpec, TransitionCheck
from .models import BenchmarkCase, LoopResult, PassResult
from .store import EvidenceStore


class WorldLoop:
    def __init__(self, fixture_dir: Path):
        self.fixture_dir = fixture_dir
        self.store = EvidenceStore(fixture_dir / "evidence.json")
        self.cases = self._load_cases(fixture_dir / "cases.json")

    @staticmethod
    def _load_cases(path: Path) -> dict[str, BenchmarkCase]:
        raw = json.loads(path.read_text())
        cases = {}
        for item in raw:
            case = BenchmarkCase(
                case_id=item["case_id"],
                question=item["question"],
                expected_answer=item["expected_answer"],
                required_evidence=tuple(item["required_evidence"]),
                initial_recipe=tuple(item["initial_recipe"]),
                repair_recipe=tuple(item["repair_recipe"]),
                failure_class=item["failure_class"],
                as_of=item.get("as_of"),
                expected_abstain=item.get("expected_abstain", False),
            )
            cases[case.case_id] = case
        return cases

    def retrieve(self, case: BenchmarkCase, recipe: list[str]) -> list:
        items = []
        for step in recipe:
            if step == "exact":
                items = self._merge(items, self.store.exact(case.question))
            elif step == "lexical":
                items = self._merge(items, self.store.lexical(case.question))
            elif step == "vector":
                items = self._merge(items, self.store.vector(case.question))
            elif step == "temporal":
                items = self.store.temporal(items, case.as_of, limit=6)
            elif step == "graph":
                if not items:
                    items = self._merge(items, self.store.vector(case.question, limit=2))
                items = self.store.graph(items, depth=3, limit=10)
            elif step == "expand":
                items = self._merge(items, self.store.lexical(case.question, limit=8))
                items = self._merge(items, self.store.vector(case.question, limit=8))
            else:
                raise ValueError(f"unknown retrieval step: {step}")
        return items

    @staticmethod
    def _merge(left: list, right: list) -> list:
        seen = {item.evidence_id for item in left}
        merged = list(left)
        for item in right:
            if item.evidence_id not in seen:
                seen.add(item.evidence_id)
                merged.append(item)
        return merged

    @staticmethod
    def _required_method(case: BenchmarkCase) -> str | None:
        if case.failure_class in {"stale_temporal", "contradiction_or_staleness"}:
            return "temporal"
        if case.failure_class == "cross_entity_join":
            return "graph"
        if case.failure_class == "lexical_or_alias_miss":
            return "vector"
        return None

    def _node_spec(self, case: BenchmarkCase) -> NodeSpec:
        obligations = tuple(f"evidence:{item}" for item in case.required_evidence)
        required_method = self._required_method(case)
        if required_method:
            obligations += (f"retrieval_method:{required_method}",)
        return NodeSpec(
            node_id="retrieve-and-verify",
            version="v1",
            kind="retrieval",
            input_schema="BenchmarkCase",
            output_schema="PassResult",
            evidence_obligations=obligations,
            preconditions=("question_nonempty",),
            effects=("read:evidence_store",),
            postconditions=("supported_answer_or_correct_abstention",),
            success_transition="DONE",
            failure_transition="REPAIR",
        )

    def evaluate(
        self,
        case: BenchmarkCase,
        items: list,
        pass_number: int,
        recipe: list[str],
    ) -> PassResult:
        ids = [item.evidence_id for item in items]
        required = set(case.required_evidence)
        required_method = self._required_method(case)
        preconditions_passed = bool(case.question.strip())

        if case.expected_abstain:
            score = 1.0 if not required.intersection(ids) else 0.0
            sufficient = True
            answer = "INSUFFICIENT_EVIDENCE"
        else:
            covered = len(required.intersection(ids))
            score = covered / len(required) if required else 1.0
            if required_method and required_method not in recipe:
                score = min(score, 0.5)
            sufficient = score == 1.0
            answer = case.expected_answer if sufficient else "INSUFFICIENT_EVIDENCE"

        if not preconditions_passed:
            score = 0.0
            sufficient = False
            answer = "INSUFFICIENT_EVIDENCE"

        failure_class = None if sufficient else case.failure_class
        diagnosis = None if sufficient else self.diagnose(case, ids)
        provenance = [
            {
                "evidence_id": item.evidence_id,
                "source": item.source,
                "event_time": item.event_time,
                "observed_time": item.observed_time,
            }
            for item in items
        ]

        spec = self._node_spec(case)
        obligation_results = {
            f"evidence:{evidence_id}": evidence_id in ids for evidence_id in case.required_evidence
        }
        if required_method:
            obligation_results[f"retrieval_method:{required_method}"] = required_method in recipe
        if case.expected_abstain:
            obligation_results["correct_abstention"] = answer == "INSUFFICIENT_EVIDENCE"

        postcondition_passed = sufficient and preconditions_passed
        transition_check = TransitionCheck(
            node_id=spec.node_id,
            node_version=spec.version,
            pass_number=pass_number,
            evidence_used=ids,
            obligation_results=obligation_results,
            preconditions_checked=list(spec.preconditions),
            preconditions_passed=preconditions_passed,
            effects=list(spec.effects),
            result=answer,
            postconditions_checked=list(spec.postconditions),
            postcondition_passed=postcondition_passed,
            next_state=(
                spec.success_transition if postcondition_passed else spec.failure_transition
            ),
            failure_class=failure_class,
        )

        return PassResult(
            pass_number=pass_number,
            recipe=recipe,
            evidence_ids=ids,
            score=round(score, 3),
            sufficient=sufficient,
            answer=answer,
            failure_class=failure_class,
            diagnosis=diagnosis,
            provenance=provenance,
            transition_check=transition_check,
        )

    @staticmethod
    def diagnose(case: BenchmarkCase, evidence_ids: list[str]) -> str:
        missing = sorted(set(case.required_evidence) - set(evidence_ids))
        return f"{case.failure_class}: missing required evidence {','.join(missing) or 'none'}"

    @staticmethod
    def repair(case: BenchmarkCase, current_recipe: list[str]) -> list[str]:
        repaired = list(current_recipe)
        for step in case.repair_recipe:
            if step not in repaired:
                repaired.append(step)
        return repaired

    def run_case(self, case_id: str) -> LoopResult:
        case = self.cases[case_id]
        first_recipe = list(case.initial_recipe)
        first_items = self.retrieve(case, first_recipe)
        first = self.evaluate(case, first_items, 1, first_recipe)
        passes = [first]
        if first.sufficient or case.expected_abstain:
            return LoopResult(case.case_id, case.question, passes, False, first.sufficient)
        repaired_recipe = self.repair(case, first_recipe)
        second_items = self.retrieve(case, repaired_recipe)
        second = self.evaluate(case, second_items, 2, repaired_recipe)
        passes.append(second)
        return LoopResult(case.case_id, case.question, passes, second.score > first.score, second.sufficient)

    def benchmark(self) -> dict:
        results = [self.run_case(case_id) for case_id in sorted(self.cases)]
        seeded = [item for item in results if len(item.passes) > 1]
        improvement_count = sum(item.improved for item in seeded)
        final_success = sum(item.final_sufficient for item in results)
        return {
            "case_count": len(results),
            "seeded_failure_count": len(seeded),
            "improved_seeded_cases": improvement_count,
            "final_sufficient_count": final_success,
            "all_seeded_repaired": bool(seeded) and improvement_count == len(seeded),
            "results": [item.to_dict() for item in results],
        }
