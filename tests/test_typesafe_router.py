from types import SimpleNamespace

import pytest

from worldloop.benchmark import generate_benchmark
from worldloop.typesafe_router import (
    ROUTE_CRITERIA,
    ROUTE_TO_RECIPE,
    evaluate_router,
    heuristic_route,
    parse_typesafe_choice,
    routing_state,
    typesafe_question,
)


def test_routing_state_excludes_oracle_fields():
    case = generate_benchmark().heldout[0]
    state = routing_state(case)

    assert "expected_decision" not in state
    assert "failure_class" not in state
    assert "repair_recipe" not in state
    assert state["task_family"] == "change_aware_rollout"


def test_route_contract_is_closed_and_maps_to_explicit_recipes():
    assert set(ROUTE_CRITERIA) == set(ROUTE_TO_RECIPE)
    assert ROUTE_TO_RECIPE["TEMPORAL"] == ("vector", "temporal")
    assert ROUTE_TO_RECIPE["GRAPH"] == ("vector", "graph")
    assert ROUTE_TO_RECIPE["ABSTAIN"] == ()


def test_official_choice_object_uses_all_declared_routes():
    question = typesafe_question()
    assert dict(question.criteria) == ROUTE_CRITERIA
    assert "do not decide APPROVE/BLOCK/ESCALATE" in question.instructions


def test_typesafe_choice_is_normalized_without_owning_control_flow():
    answer = SimpleNamespace(
        choice="GRAPH",
        confidence=0.91,
        probabilities={"GRAPH": 0.91, "VECTOR": 0.09},
    )
    result = parse_typesafe_choice(answer)

    assert result.route == "GRAPH"
    assert result.recipe == ("vector", "graph")
    assert result.confidence == 0.91
    assert result.provider == "typesafe"


def test_deterministic_baseline_is_perfect_on_current_frozen_task_family():
    dataset = generate_benchmark()
    metrics, rows = evaluate_router(dataset.heldout, heuristic_route)

    assert metrics.case_count == 21
    assert metrics.verified_success == 1.0
    assert metrics.under_allocation_count == 0
    assert metrics.unnecessary_retrieval_count == 0
    assert metrics.route_counts == {"EXACT": 7, "GRAPH": 7, "TEMPORAL": 7}
    assert all(row["verified"] for row in rows)


def test_latent_routing_state_provides_context_prose_and_no_booleans():
    case = generate_benchmark().heldout[0]
    legacy_state = routing_state(case, mode="legacy")
    latent_state = routing_state(case, mode="latent")

    assert "has_dependency" in legacy_state
    assert "has_dependency" not in latent_state
    assert "cross_entity" not in latent_state
    assert "freshness_sensitive" not in latent_state
    assert "context_brief" in latent_state
    assert len(latent_state["context_brief"]) > 20


def test_multi_primitive_questions_structure():
    from worldloop.typesafe_router import typesafe_multi_questions

    questions = typesafe_multi_questions()
    assert "is_evidence_stale" in questions
    assert "has_cross_entity_dependency" in questions
    assert "is_receipt_attached" in questions
    assert "missing_evidence_class" in questions
    assert "candidate_route" in questions


def test_compose_typesafe_policy_prioritizes_dependency_and_staleness():
    from worldloop.typesafe_router import compose_typesafe_policy

    cand_mock = SimpleNamespace(
        choice="EXACT",
        confidence=0.5,
        probabilities={"EXACT": 0.5, "GRAPH": 0.5},
    )

    # 1. High dependency signal -> GRAPH
    res_dep = compose_typesafe_policy(
        nouls={"has_cross_entity_dependency": 0.88, "is_evidence_stale": 0.05},
        choices={"candidate_route": cand_mock},
    )
    assert res_dep.route == "GRAPH"
    assert res_dep.confidence == 0.88

    # 2. High staleness signal -> TEMPORAL
    res_stale = compose_typesafe_policy(
        nouls={"has_cross_entity_dependency": 0.10, "is_evidence_stale": 0.85},
        choices={"candidate_route": cand_mock},
    )
    assert res_stale.route == "TEMPORAL"
    assert res_stale.confidence == 0.85

    # 3. Model only with receipt obligation is bounded to EXACT
    cand_model_only = SimpleNamespace(
        choice="MODEL_ONLY",
        confidence=0.75,
        probabilities={"MODEL_ONLY": 0.75, "EXACT": 0.25},
    )
    res_bounded = compose_typesafe_policy(
        nouls={"has_cross_entity_dependency": 0.05, "is_evidence_stale": 0.05, "is_receipt_attached": 0.1},
        choices={"candidate_route": cand_model_only},
        obligation="independent_receipt_required",
    )
    assert res_bounded.route == "EXACT"
    assert res_bounded.confidence == 0.75


def test_heuristic_collapses_on_adversarial_prose():
    from worldloop.typesafe_router import evaluate_router, heuristic_route

    dataset = generate_benchmark()
    metrics, _ = evaluate_router(dataset.heldout, lambda c: heuristic_route(c, mode="adversarial"))
    # Keyword-matching fails on natural operational prose, dropping to 33.3%
    assert metrics.verified_success == pytest.approx(1 / 3, abs=0.01)
    assert metrics.under_allocation_count == 14
    assert metrics.route_counts == {"EXACT": 21}



