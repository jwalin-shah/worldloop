import json
from pathlib import Path

from worldloop.benchmark import (
    DATASET_VERSION,
    DEFAULT_DEV_COUNT,
    DEFAULT_HELDOUT_COUNT,
    generate_benchmark,
    write_snapshot,
)


def test_benchmark_is_deterministic_and_sized():
    first = generate_benchmark()
    second = generate_benchmark()
    assert first == second
    assert first.snapshot_id == second.snapshot_id
    assert len(first.development) == DEFAULT_DEV_COUNT
    assert len(first.heldout) == DEFAULT_HELDOUT_COUNT
    assert first.version == DATASET_VERSION


def test_split_is_entity_and_time_disjoint():
    dataset = generate_benchmark()
    dev_projects = {case.project for case in dataset.development}
    heldout_projects = {case.project for case in dataset.heldout}
    dev_dependencies = {case.dependency for case in dataset.development if case.dependency}
    heldout_dependencies = {case.dependency for case in dataset.heldout if case.dependency}

    assert dev_projects.isdisjoint(heldout_projects)
    assert dev_dependencies.isdisjoint(heldout_dependencies)
    assert all(case.as_of.startswith("2026-0") for case in dataset.development)
    assert all(case.as_of >= "2026-07" for case in dataset.heldout)


def test_required_failure_classes_and_evidence_exist():
    dataset = generate_benchmark()
    evidence_ids = {item.evidence_id for item in dataset.evidence}
    classes = {case.failure_class for case in (*dataset.development, *dataset.heldout)}
    assert {"temporal_staleness", "cross_entity_join"}.issubset(classes)
    for case in (*dataset.development, *dataset.heldout):
        assert set(case.required_evidence).issubset(evidence_ids)
        assert case.expected_decision in {"APPROVE", "BLOCK", "ESCALATE"}


def test_training_records_cannot_consume_heldout_labels():
    dataset = generate_benchmark()
    training = dataset.training_records()
    training_ids = {row["case_id"] for row in training}
    heldout_ids = {case.case_id for case in dataset.heldout}

    assert training_ids == {case.case_id for case in dataset.development}
    assert training_ids.isdisjoint(heldout_ids)
    assert all("expected_decision" not in row["features"] for row in training)
    assert all("failure_class" not in row["features"] for row in training)


def test_snapshot_writer_records_version_and_digest(tmp_path: Path):
    dataset = generate_benchmark()
    target = write_snapshot(tmp_path / "benchmark.json", dataset)
    payload = json.loads(target.read_text())
    assert payload["version"] == DATASET_VERSION
    assert payload["snapshot_id"] == dataset.snapshot_id
    assert payload["development_count"] == DEFAULT_DEV_COUNT
    assert payload["heldout_count"] == DEFAULT_HELDOUT_COUNT


def test_committed_manifest_locks_default_snapshot():
    manifest_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "generated"
        / "change_aware_rollout_v1.manifest.json"
    )
    manifest = json.loads(manifest_path.read_text())
    dataset = generate_benchmark()
    assert manifest["version"] == dataset.version
    assert manifest["snapshot_id"] == dataset.snapshot_id
    assert manifest["seed"] == dataset.seed
    assert manifest["development_count"] == len(dataset.development)
    assert manifest["heldout_count"] == len(dataset.heldout)


def test_adversarial_context_prose_eliminates_keyword_giveaways():
    dataset = generate_benchmark()
    for case in dataset.heldout:
        adv = case.adversarial_context_prose.lower()
        assert "dependency" not in adv
        assert "superseding" not in adv
        features = case.pre_action_features(mode="adversarial")
        assert features["context_prose"] == case.adversarial_context_prose

