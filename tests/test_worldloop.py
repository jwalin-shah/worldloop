from pathlib import Path

from worldloop.engine import WorldLoop

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_benchmark_has_required_coverage():
    loop = WorldLoop(FIXTURES)
    report = loop.benchmark()
    assert report["case_count"] >= 10
    assert report["seeded_failure_count"] >= 3
    assert report["improved_seeded_cases"] >= 3


def test_cross_entity_case_repairs_retrieval():
    result = WorldLoop(FIXTURES).run_case("case-cross-entity")
    assert len(result.passes) == 2
    assert result.passes[0].score < result.passes[1].score
    assert "graph" in result.passes[1].recipe
    assert result.final_sufficient


def test_cross_entity_case_emits_transition_checks():
    result = WorldLoop(FIXTURES).run_case("case-cross-entity")
    first = result.passes[0].transition_check
    second = result.passes[1].transition_check

    assert first is not None
    assert first.node_id == "retrieve-and-verify"
    assert first.obligation_results["retrieval_method:graph"] is False
    assert first.postcondition_passed is False
    assert first.next_state == "REPAIR"

    assert second is not None
    assert second.obligation_results["retrieval_method:graph"] is True
    assert second.postcondition_passed is True
    assert second.next_state == "DONE"


def test_transition_check_serializes_with_loop_result():
    result = WorldLoop(FIXTURES).run_case("case-cross-entity").to_dict()
    first_check = result["passes"][0]["transition_check"]
    assert first_check["node_version"] == "v1"
    assert first_check["next_state"] == "REPAIR"


def test_temporal_case_repairs_staleness():
    result = WorldLoop(FIXTURES).run_case("case-current-cache")
    assert result.final_sufficient
    assert "temporal" in result.passes[-1].recipe
    check = result.passes[-1].transition_check
    assert check is not None
    assert check.obligation_results["retrieval_method:temporal"] is True


def test_unknown_question_fails_closed():
    result = WorldLoop(FIXTURES).run_case("case-insufficient")
    assert result.passes[-1].answer == "INSUFFICIENT_EVIDENCE"
    check = result.passes[-1].transition_check
    assert check is not None
    assert check.postcondition_passed is True
    assert check.next_state == "DONE"
