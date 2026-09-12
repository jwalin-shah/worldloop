import json
from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "status",
    "question",
    "hypothesis",
    "independent_variable",
    "baseline",
    "treatment",
    "metrics",
    "dataset_or_cases",
    "stop_rule",
    "artifact",
}


def test_experiment_registry_is_structured_and_unique():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "experiments" / "registry.json").read_text())
    experiments = registry["experiments"]
    assert len(experiments) >= 7
    ids = [item["id"] for item in experiments]
    assert len(ids) == len(set(ids))
    assert all(item_id.startswith("EXP-") for item_id in ids)
    for item in experiments:
        assert REQUIRED_FIELDS <= item.keys()
        assert item["metrics"]
        assert item["question"].strip()
        assert item["stop_rule"].strip()
