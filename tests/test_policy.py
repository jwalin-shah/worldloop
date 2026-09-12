from worldloop.benchmark import generate_benchmark
from worldloop.policy import DerivedRulePolicy, evaluate_v0_v1


def test_policy_fit_uses_development_cases_only():
    dataset = generate_benchmark()
    policy = DerivedRulePolicy.fit(dataset)
    heldout_ids = {case.case_id for case in dataset.heldout}

    assert set(policy.development_case_ids) == {case.case_id for case in dataset.development}
    assert set(policy.development_case_ids).isdisjoint(heldout_ids)


def test_policy_is_derived_from_three_repeated_structural_patterns():
    dataset = generate_benchmark()
    policy = DerivedRulePolicy.fit(dataset)

    assert policy.rules[(False, True, False)] == ("vector", "temporal")
    assert policy.rules[(True, False, True)] == ("vector", "graph")
    assert policy.rules[(False, False, False)] == ("exact",)


def test_v1_improves_first_pass_on_frozen_heldout_without_final_regression():
    report = evaluate_v0_v1(generate_benchmark())

    assert report.primary_metric == "first_pass_verified_success"
    assert report.v0.case_count == 21
    assert report.v0.first_pass_verified_count == 7
    assert report.v0.first_pass_verified_success == 0.333333
    assert report.v1.first_pass_verified_count == 21
    assert report.v1.first_pass_verified_success == 1.0
    assert report.v0.final_verified_success == 1.0
    assert report.v1.final_verified_success == 1.0
    assert report.promotion_decision == "PROMOTED"


def test_v1_generalizes_across_disjoint_entity_namespaces():
    dataset = generate_benchmark()
    report = evaluate_v0_v1(dataset)

    assert all(case.project.startswith("Orion-") for case in dataset.heldout)
    assert all(case_id.startswith("heldout-") for case_id in report.heldout_case_ids)
    assert report.v1.first_pass_verified_success == 1.0
