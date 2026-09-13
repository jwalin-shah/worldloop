import importlib.util
from pathlib import Path

from worldloop.engine import WorldLoop
from worldloop.lab import (
    heldout_comparison_rows,
    lab_summary,
    lifeops_pilot_rows,
    live_program_view,
    load_gate3_report,
    load_lifeops_pilot,
    program_comparison_rows,
)
from worldloop.runtime import FIXTURES

ROOT = Path(__file__).resolve().parents[1]


def test_lab_summary_and_heldout_view_use_committed_gate3_report():
    report = load_gate3_report(ROOT)
    summary = lab_summary(report)
    comparison = heldout_comparison_rows(report)

    assert summary["promotion_decision"] == "PROMOTED"
    assert summary["heldout_cases"] == 21
    assert comparison[0] == {
        "metric": "First-pass verified success",
        "v0": 0.333333,
        "v1": 1.0,
        "delta": 0.666667,
    }


def test_live_program_view_exposes_localized_transition_and_repair():
    view = live_program_view(WorldLoop(FIXTURES), "case-cross-entity")

    assert view["program_before"] == ["vector"]
    assert view["program_after"] == ["vector", "graph"]
    assert view["program_delta"] == ["graph"]
    assert view["transition_rows"][0]["next_state"] == "REPAIR"
    assert view["transition_rows"][-1]["next_state"] == "DONE"
    assert view["final_sufficient"] is True


def test_program_comparison_is_an_inspectable_v0_v1_diff():
    rows = program_comparison_rows(load_gate3_report(ROOT))
    by_shape = {row["task shape"]: row for row in rows}

    assert by_shape["freshness-sensitive"]["added operation"] == "temporal"
    assert by_shape["cross-entity dependency"]["added operation"] == "graph"
    assert by_shape["exact/control"]["added operation"] == "none"


def test_lifeops_pilot_exposes_real_world_abstention_route():
    report = load_lifeops_pilot(ROOT)
    assert report is not None
    assert report["claim_scope"].startswith("single real-world routing snapshot")
    assert report["baseline_policy_v0"]["selected_route"] == "cursor-agent"
    assert report["candidate_policy_v1"]["selected_route"] == "ABSTAIN_REPAIR_CONTROL_PLANE"
    rows = lifeops_pilot_rows(report)
    assert rows[-1]["baseline / observed"] == "FAIL"
    assert rows[-1]["proof-aware route"] == "PASS"


def test_marimo_source_registers_as_python_without_starting_server():
    notebook_path = ROOT / "notebooks" / "worldloop_lab.py"
    spec = importlib.util.spec_from_file_location("worldloop_lab_gate4", notebook_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.app is not None
