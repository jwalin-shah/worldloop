from __future__ import annotations

from dataclasses import asdict

from worldloop.benchmark_v2 import generate_benchmark_v2
from worldloop.evaluator import IndependentEvaluator
from worldloop.solver import DeterministicSolver, SolverDecision
from worldloop.store import EvidenceStore
from worldloop.world_sim import OperationalWorld


def test_zero_oracle_leakage_on_task_surface():
    """CRITICAL INVARIANT: The task surface presented to router/solver must have zero oracle labels."""
    dataset, _world = generate_benchmark_v2(seed=42, dev_count=10, heldout_count=10)

    forbidden_fields = {
        "expected_answer",
        "expected_decision",
        "failure_class",
        "initial_recipe",
        "repair_recipe",
        "required_evidence",
        "has_dependency",
        "freshness_sensitive",
        "cross_entity",
    }

    for case in list(dataset.development) + list(dataset.heldout):
        case_dict = asdict(case)
        for field_name in forbidden_fields:
            assert field_name not in case_dict, f"Oracle leak! {field_name} present on case {case.task_id}"

        # Context brief must not contain formulaic template tags
        assert "has_dependency" not in case.context_brief
        assert "failure_class" not in case.context_brief


def test_disjoint_namespaces_and_time_clusters():
    dataset, _world = generate_benchmark_v2(seed=42, dev_count=15, heldout_count=15)

    dev_entities = {c.target_entity for c in dataset.development}
    heldout_entities = {c.target_entity for c in dataset.heldout}
    assert dev_entities.isdisjoint(heldout_entities), "Entities must be strictly disjoint across splits"

    dev_times = [c.as_of for c in dataset.development]
    heldout_times = [c.as_of for c in dataset.heldout]
    # Heldout is months after dev
    assert min(heldout_times) > max(dev_times), "Held-out split must be strictly in the future relative to dev"


def test_evaluator_catches_stale_citation():
    """Falsification: A solver that relies on an earlier superseded incident must be flagged for stale citation."""
    world = OperationalWorld(seed=99)
    # Generate 10 cases to get a superseded_block scenario (pattern index 2)
    cases = world.generate_universe(split="development", task_count=10)
    superseded_task = next(
        s for s in cases
        if "superseded" in world.ground_truths[s["task_id"]].explanation or world.ground_truths[s["task_id"]].stale_evidence_ids
    )
    task_id = superseded_task["task_id"]
    gt = world.ground_truths[task_id]

    evaluator = IndependentEvaluator(world)

    # Simulate a buggy solver that cites the old morning alert
    stale_id = gt.stale_evidence_ids[0]
    bad_decision = SolverDecision(
        task_id=task_id,
        decision="BLOCK",
        confidence=0.9,
        rationale="Old alert observed",
        cited_evidence_ids=(stale_id,),
        retrieval_steps=("exact",),
        retrieved_count=2,
        solver_type="buggy_solver",
        latency_ms=5.0,
    )

    res = evaluator.evaluate_task(bad_decision)
    assert not res.correct, "Ground truth for mitigated incident is APPROVE, not BLOCK"
    assert stale_id in res.stale_evidence_cited, "Evaluator must flag citation of superseded evidence"
    assert res.citation_precision == 0.0, "Citation precision must be 0 when citing only stale evidence"


def test_missing_telemetry_mandates_abstention():
    """Falsification: When critical facts are missing, the evaluator mandates ABSTAIN."""
    world = OperationalWorld(seed=99)
    cases = world.generate_universe(split="development", task_count=16)
    abstain_tasks = [s for s in cases if world.ground_truths[s["task_id"]].expected_decision == "ABSTAIN"]
    assert abstain_tasks, "World must generate cases with incomplete information"

    task = abstain_tasks[0]
    task_id = task["task_id"]
    evaluator = IndependentEvaluator(world)

    # 1. Honest solver abstains
    honest_decision = SolverDecision(
        task_id=task_id,
        decision="ABSTAIN",
        confidence=0.8,
        rationale="Missing telemetry",
        cited_evidence_ids=(),
        retrieval_steps=("exact",),
        retrieved_count=1,
        solver_type="honest_solver",
        latency_ms=2.0,
    )
    res_honest = evaluator.evaluate_task(honest_decision)
    assert res_honest.correct is True
    assert res_honest.correct_abstention is True
    assert res_honest.false_abstention is False

    # 2. Overconfident solver guesses APPROVE
    guess_decision = SolverDecision(
        task_id=task_id,
        decision="APPROVE",
        confidence=0.8,
        rationale="Guessed without evidence",
        cited_evidence_ids=(),
        retrieval_steps=("exact",),
        retrieved_count=1,
        solver_type="guessing_solver",
        latency_ms=2.0,
    )
    res_guess = evaluator.evaluate_task(guess_decision)
    assert res_guess.correct is False


def test_deterministic_solver_end_to_end():
    dataset, world = generate_benchmark_v2(seed=123, dev_count=8, heldout_count=8)
    store = EvidenceStore(list(world.all_evidence))

    case = dataset.development[0]
    # Retrieve using exact + lexical
    items = store.exact(case.target_entity) + store.lexical(f"{case.target_entity} {case.context_brief}")
    decision = DeterministicSolver.solve(case, items, retrieval_steps=("exact", "lexical"))

    assert decision.task_id == case.task_id
    assert decision.decision in {"APPROVE", "BLOCK", "ESCALATE", "ABSTAIN"}
    assert decision.confidence > 0.0
    assert isinstance(decision.cited_evidence_ids, tuple)
