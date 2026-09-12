from types import SimpleNamespace

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
