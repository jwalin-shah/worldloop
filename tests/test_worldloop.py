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


def test_temporal_case_repairs_staleness():
    result = WorldLoop(FIXTURES).run_case("case-current-cache")
    assert result.final_sufficient
    assert "temporal" in result.passes[-1].recipe


def test_unknown_question_fails_closed():
    result = WorldLoop(FIXTURES).run_case("case-insufficient")
    assert result.passes[-1].answer == "INSUFFICIENT_EVIDENCE"
