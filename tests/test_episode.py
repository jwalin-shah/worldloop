from dataclasses import dataclass
from types import SimpleNamespace

from worldloop.episode import RunIdentity, run_episode


@dataclass
class FakeItem:
    evidence_id: str


class FakeLoop:
    def __init__(self):
        self.cases = {
            "case": SimpleNamespace(
                case_id="case",
                question="Should Aurora roll out?",
                initial_recipe=("vector",),
                repair_recipe=("vector", "graph"),
                expected_abstain=False,
            )
        }

    def retrieve(self, case, recipe):
        if "graph" in recipe:
            return [FakeItem("project"), FakeItem("dependency")]
        return [FakeItem("project")]

    def evaluate(self, case, items, pass_number, recipe):
        sufficient = "graph" in recipe
        return SimpleNamespace(
            answer="APPROVE" if sufficient else "INSUFFICIENT_EVIDENCE",
            sufficient=sufficient,
            score=1.0 if sufficient else 0.5,
            failure_class=None if sufficient else "cross_entity_join",
            diagnosis=None if sufficient else "missing dependency",
            transition_check=SimpleNamespace(
                to_dict=lambda: {
                    "pass_number": pass_number,
                    "next_state": "DONE" if sufficient else "REPAIR",
                }
            ),
        )

    def repair(self, case, recipe):
        return ["vector", "graph"]


def identity():
    return RunIdentity.create(
        experiment_id="EXP-008",
        run_id="run-fixed",
        code_revision="abc123",
        dataset_snapshot="dataset:v1",
        evidence_snapshot="evidence:v1",
    )


def test_episode_records_real_failure_repair_and_verification_order():
    trace = run_episode(FakeLoop(), "case", identity())
    event_types = [event.event_type for event in trace.events]
    assert event_types == [
        "program_selected",
        "retrieval_completed",
        "semantic_node_completed",
        "critic_scored",
        "program_delta_proposed",
        "retry_started",
        "retrieval_completed",
        "semantic_node_completed",
        "critic_scored",
        "verification_completed",
    ]
    assert trace.improved is True
    assert trace.final_sufficient is True
    assert trace.final_score == 1.0


def test_identity_binds_required_run_metadata_before_execution():
    run = identity()
    payload = run.to_dict()
    for key in (
        "experiment_id",
        "run_id",
        "code_revision",
        "dataset_snapshot",
        "evidence_snapshot",
        "workflow_version",
        "policy_version",
        "provider",
        "model",
        "scorer_version",
    ):
        assert payload[key]
