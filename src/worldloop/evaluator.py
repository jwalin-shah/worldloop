from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .solver import SolverDecision
from .world_sim import OperationalWorld, WorldGroundTruth


@dataclass(frozen=True)
class TaskEvaluationResult:
    task_id: str
    target_entity: str
    solver_decision: str
    ground_truth_decision: str
    correct: bool
    cited_evidence_ids: tuple[str, ...]
    minimal_evidence_ids: tuple[str, ...]
    stale_evidence_cited: tuple[str, ...]
    citation_precision: float
    citation_recall: float
    correct_abstention: bool
    false_abstention: bool
    retrieved_count: int
    retrieval_waste: int
    latency_ms: float
    solver_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArmSummaryMetrics:
    arm_name: str
    case_count: int
    accuracy: float
    citation_precision: float
    citation_recall: float
    stale_citation_rate: float
    correct_abstention_rate: float
    false_abstention_rate: float
    mean_retrieval_count: float
    mean_retrieval_waste: float
    mean_latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class IndependentEvaluator:
    """Independent ground-truth evaluator for Benchmark V2.

    Evaluates solver decisions against hidden world state without oracle leakage.
    Scores end-task correctness, citation validity, freshness, and retrieval waste.
    """

    def __init__(self, world: OperationalWorld):
        self.world = world

    def evaluate_task(self, decision: SolverDecision) -> TaskEvaluationResult:
        gt: WorldGroundTruth = self.world.ground_truths[decision.task_id]

        correct = decision.decision == gt.expected_decision
        cited_set = set(decision.cited_evidence_ids)
        minimal_set = set(gt.minimal_evidence_ids)
        stale_set = set(gt.stale_evidence_ids)

        # Check for stale citations (relying on superseded evidence)
        stale_cited = tuple(cited_set.intersection(stale_set))

        # Citation precision and recall
        if cited_set:
            prec = len(cited_set.intersection(minimal_set)) / len(cited_set)
        else:
            prec = 1.0 if gt.expected_decision == "ABSTAIN" else 0.0

        if minimal_set:
            rec = len(cited_set.intersection(minimal_set)) / len(minimal_set)
        else:
            rec = 1.0

        is_gt_abstain = gt.expected_decision == "ABSTAIN"
        is_solver_abstain = decision.decision == "ABSTAIN"
        correct_abstain = is_gt_abstain and is_solver_abstain
        false_abstain = (not is_gt_abstain) and is_solver_abstain

        # Retrieval waste: items retrieved that were not in minimal set
        waste = max(0, decision.retrieved_count - len(minimal_set))

        return TaskEvaluationResult(
            task_id=decision.task_id,
            target_entity=gt.target_entity,
            solver_decision=decision.decision,
            ground_truth_decision=gt.expected_decision,
            correct=correct,
            cited_evidence_ids=decision.cited_evidence_ids,
            minimal_evidence_ids=gt.minimal_evidence_ids,
            stale_evidence_cited=stale_cited,
            citation_precision=round(prec, 4),
            citation_recall=round(rec, 4),
            correct_abstention=correct_abstain,
            false_abstention=false_abstain,
            retrieved_count=decision.retrieved_count,
            retrieval_waste=waste,
            latency_ms=decision.latency_ms,
            solver_type=decision.solver_type,
        )

    @staticmethod
    def aggregate_arm_metrics(
        arm_name: str,
        results: list[TaskEvaluationResult],
    ) -> ArmSummaryMetrics:
        n = len(results)
        if n == 0:
            return ArmSummaryMetrics(
                arm_name=arm_name,
                case_count=0,
                accuracy=0.0,
                citation_precision=0.0,
                citation_recall=0.0,
                stale_citation_rate=0.0,
                correct_abstention_rate=0.0,
                false_abstention_rate=0.0,
                mean_retrieval_count=0.0,
                mean_retrieval_waste=0.0,
                mean_latency_ms=0.0,
            )

        acc = sum(r.correct for r in results) / n
        prec = sum(r.citation_precision for r in results) / n
        rec = sum(r.citation_recall for r in results) / n
        stale_rate = sum(bool(r.stale_evidence_cited) for r in results) / n
        cor_abst = sum(r.correct_abstention for r in results) / n
        fal_abst = sum(r.false_abstention for r in results) / n
        mean_ret = sum(r.retrieved_count for r in results) / n
        mean_waste = sum(r.retrieval_waste for r in results) / n
        mean_lat = sum(r.latency_ms for r in results) / n

        return ArmSummaryMetrics(
            arm_name=arm_name,
            case_count=n,
            accuracy=round(acc, 4),
            citation_precision=round(prec, 4),
            citation_recall=round(rec, 4),
            stale_citation_rate=round(stale_rate, 4),
            correct_abstention_rate=round(cor_abst, 4),
            false_abstention_rate=round(fal_abst, 4),
            mean_retrieval_count=round(mean_ret, 2),
            mean_retrieval_waste=round(mean_waste, 2),
            mean_latency_ms=round(mean_lat, 2),
        )
