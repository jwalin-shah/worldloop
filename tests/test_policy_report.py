import json
from pathlib import Path

from worldloop.benchmark import generate_benchmark
from worldloop.policy import evaluate_v0_v1


def test_committed_gate3_report_matches_recomputed_metrics():
    report_path = Path(__file__).resolve().parents[1] / "reports" / "EXP-008-gate3.json"
    committed = json.loads(report_path.read_text())
    recomputed = evaluate_v0_v1(generate_benchmark()).to_dict()

    assert committed["dataset_snapshot"] == recomputed["dataset_snapshot"]
    assert committed["primary_metric"] == recomputed["primary_metric"]
    assert committed["v0"] == recomputed["v0"]
    assert committed["v1"] == recomputed["v1"]
    assert committed["promotion_decision"] == recomputed["promotion_decision"]
    assert committed["policy"] == recomputed["policy"]
    assert committed["heldout_case_ids"] == recomputed["heldout_case_ids"]
