import pytest

from industrial_energy_lab.explainability.glossary import GLOSSARY
from industrial_energy_lab.learning import (
    CASTELLON_WALKTHROUGH, COMMON_TRAPS, GUIDED_EXPERIMENTS, LEARNING_PATH, QUESTIONS,
    TERM_DIFFICULTY,
    battery_duration_hours, co2_from_grid_energy_tco2, crf_learning_example,
    energy_balance_residual_kwh, energy_from_power, explain_dispatch_hour,
    modified_parameters, three_hour_battery_lab,
)
from industrial_energy_lab.learning.experiments import compare_prediction, result_comparison
from industrial_energy_lab.optimization.model import OptimizationResult


def result(**overrides):
    values = dict(
        status="optimal", solver_message="ok", objective_annualized_cost_eur=100.0,
        pv_capacity_kw=100.0, battery_energy_capacity_kwh=0.0, battery_power_capacity_kw=0.0,
        load_mwh=10.0, pv_generation_mwh=5.0, pv_self_consumption_mwh=5.0, pv_export_mwh=0.0,
        battery_charge_mwh=0.0, battery_discharge_mwh=0.0, battery_losses_mwh=0.0,
        grid_import_mwh=5.0, grid_export_mwh=0.0, self_consumption_ratio=1.0,
        self_sufficiency_ratio=0.5, annualized_pv_cost_eur=10.0, annualized_battery_cost_eur=0.0,
        annual_pv_opex_eur=1.0, annual_battery_opex_eur=0.0, grid_purchase_cost_eur=90.0,
        export_revenue_eur=0.0, baseline_annual_cost_eur=120.0, annual_saving_vs_baseline_eur=20.0,
        initial_capex_eur=100.0, project_npv_eur=10.0, simple_payback_years=5.0,
        baseline_emissions_tco2=10.0, scenario_emissions_tco2=5.0, emissions_reduction_tco2=5.0,
        emissions_reduction_fraction=0.5, abatement_cost_eur_per_tco2=-4.0, carbon_target=0.0,
        carbon_constraint_binding=False, carbon_constraint_slack_tco2=None,
        model_build_seconds=0.01, solve_seconds=0.01, total_seconds=0.02, solver_backend="test",
    )
    values.update(overrides)
    return OptimizationResult(**values)


def test_power_energy_and_battery_duration_examples_are_hand_checkable():
    assert energy_from_power(5, 3) == pytest.approx(15)
    assert battery_duration_hours(4, 2) == pytest.approx(2)
    assert co2_from_grid_energy_tco2(1000, 180) == pytest.approx(180)


def test_crf_learning_example_is_consistent():
    x = crf_learning_example(0.05, 25, 1_000_000)
    assert x["crf"] == pytest.approx(0.0709524573)
    assert x["annualized_capex_eur"] == pytest.approx(70_952.4573)


def test_three_hour_battery_lab_reuses_validated_physics():
    d = three_hour_battery_lab()
    assert d["grid_import_kwh"].tolist() == pytest.approx([10.0, 0.0, 1.9])
    assert d["soc_kwh"].tolist() == pytest.approx([0.0, 9.0, 0.0])
    assert d["battery_losses_kwh"].sum() == pytest.approx(1.9)
    assert max(abs(energy_balance_residual_kwh(row)) for _, row in d.iterrows()) < 1e-9


def test_hourly_story_is_derived_from_dispatch_row():
    row = three_hour_battery_lab().iloc[1]
    story = explain_dispatch_hour(row)
    assert any("PV supplies" in s for s in story)
    assert any("charges the battery" in s for s in story)


def test_learning_path_and_experiments_reference_real_glossary_terms():
    for _, ids in LEARNING_PATH:
        assert set(ids) <= set(GLOSSARY)
    for exp in GUIDED_EXPERIMENTS:
        assert set(exp.concept_ids) <= set(GLOSSARY)
    assert set(GLOSSARY) <= set(TERM_DIFFICULTY)
    assert set(TERM_DIFFICULTY.values()) <= {"FOUNDATION", "INTERMEDIATE", "ADVANCED"}


def test_question_catalog_is_structurally_valid_and_unique():
    ids = [q.question_id for q in QUESTIONS]
    assert len(ids) == len(set(ids))
    assert 10 <= len(ids) <= 15
    for q in QUESTIONS:
        assert q.correct_option in q.options
        assert q.explanation
        assert q.difficulty in {"FOUNDATION", "INTERMEDIATE", "ADVANCED"}


def test_six_guided_experiments_and_ten_step_case_walkthrough_exist():
    assert len(GUIDED_EXPERIMENTS) == 6
    assert len(CASTELLON_WALKTHROUGH) == 10
    assert len(COMMON_TRAPS) >= 12


def test_each_experiment_changes_only_intended_inputs():
    base = {
        "import_price_multiplier": 1.0, "pv_capex_eur_per_kw": 700.0, "wacc": 0.05,
        "carbon_target": 0.0, "battery_energy_capex_eur_per_kwh": 240.0,
        "battery_power_capex_eur_per_kw": 120.0,
    }
    expected_keys = {
        "electricity_price_up": {"import_price_multiplier"},
        "pv_capex_up": {"pv_capex_eur_per_kw"},
        "wacc_up": {"wacc"},
        "carbon_20_to_40": {"carbon_target"},
        "battery_capex_down": {"battery_energy_capex_eur_per_kwh", "battery_power_capex_eur_per_kw"},
        "pv_oversizing": {"fixed_pv_multiplier"},
    }
    for exp in GUIDED_EXPERIMENTS:
        modified = modified_parameters(base, exp.experiment_id)
        changed = {k for k in set(base) | set(modified) if base.get(k) != modified.get(k)}
        assert changed == expected_keys[exp.experiment_id]


def test_prediction_comparison_reports_observed_direction():
    c = compare_prediction("PV", "Increase", 2.97, 3.19, "MW", "tested")
    assert c.correct is True
    assert c.observed_direction == "Increase"
    c2 = compare_prediction("PV", "Decrease", 2.97, 3.19, "MW", "tested")
    assert c2.correct is False


def test_scenario_comparison_has_before_after_delta_and_percent():
    rows = result_comparison(result(), result(pv_capacity_kw=120, objective_annualized_cost_eur=110))
    pv = next(x for x in rows if x["metric"] == "PV capacity")
    assert pv["delta"] == pytest.approx(20)
    assert pv["percent_change"] == pytest.approx(0.2)
