import pytest

from industrial_energy_lab.explainability.insights import explain_optimization_result, explain_scenario_change, explain_sensitivity_results
from industrial_energy_lab.explainability.metrics import METRICS, get_metric, validate_metric_registry
from industrial_energy_lab.optimization.model import OptimizationResult


def result(**overrides):
    values = dict(
        status="optimal", solver_message="ok", objective_annualized_cost_eur=100.0,
        pv_capacity_kw=100.0, battery_energy_capacity_kwh=0.0,
        battery_power_capacity_kw=0.0, load_mwh=10.0, pv_generation_mwh=5.0,
        pv_self_consumption_mwh=5.0, pv_export_mwh=0.0, battery_charge_mwh=0.0,
        battery_discharge_mwh=0.0, battery_losses_mwh=0.0, grid_import_mwh=5.0,
        grid_export_mwh=0.0, self_consumption_ratio=1.0, self_sufficiency_ratio=0.5,
        annualized_pv_cost_eur=10.0, annualized_battery_cost_eur=0.0,
        annual_pv_opex_eur=1.0, annual_battery_opex_eur=0.0,
        grid_purchase_cost_eur=90.0, export_revenue_eur=0.0,
        baseline_annual_cost_eur=120.0, annual_saving_vs_baseline_eur=20.0,
        initial_capex_eur=100.0, project_npv_eur=10.0, simple_payback_years=5.0,
        baseline_emissions_tco2=10.0, scenario_emissions_tco2=5.0,
        emissions_reduction_tco2=5.0, emissions_reduction_fraction=0.5,
        abatement_cost_eur_per_tco2=-4.0, carbon_target=0.0,
        carbon_constraint_binding=False, carbon_constraint_slack_tco2=None,
        model_build_seconds=0.01, solve_seconds=0.01, total_seconds=0.02,
        solver_backend="test",
    )
    values.update(overrides)
    return OptimizationResult(**values)


def test_metric_registry_is_internally_valid():
    validate_metric_registry()
    assert len(METRICS) >= 39


def test_required_learning_fields_exist_for_key_metric():
    metric = get_metric("wacc")
    assert metric.unit == "%"
    assert metric.why_it_matters
    assert metric.calculation
    assert metric.interpretation
    assert metric.relationships


def test_unknown_metric_fails_clearly():
    with pytest.raises(KeyError, match="Unknown metric_id"):
        get_metric("not_a_metric")


def test_zero_battery_insight_is_result_driven():
    messages = explain_optimization_result(result())
    assert any("battery energy capacity is zero" in m for m in messages)


def test_binding_carbon_insight_uses_economic_optimum_context():
    economic = result(emissions_reduction_fraction=0.30)
    constrained = result(carbon_target=0.40, carbon_constraint_binding=True, emissions_reduction_fraction=0.40)
    messages = explain_optimization_result(constrained, economic_optimum=economic)
    assert any("binding" in m for m in messages)
    assert any("stricter" in m for m in messages)


def test_scenario_change_reports_capacity_and_cost_direction():
    previous = result(carbon_target=0.30, pv_capacity_kw=100.0, objective_annualized_cost_eur=100.0)
    current = result(carbon_target=0.40, pv_capacity_kw=130.0, objective_annualized_cost_eur=110.0)
    messages = explain_scenario_change(previous, current)
    assert any("PV capacity increases" in m for m in messages)
    assert any("cost rises" in m for m in messages)


def test_sensitivity_explanation_is_derived_from_endpoints():
    import pandas as pd
    frame = pd.DataFrame({
        "status": ["optimal", "optimal"],
        "input_value": [0.8, 1.2],
        "pv_capacity_kw": [3000.0, 5000.0],
        "battery_energy_capacity_kwh": [0.0, 1000.0],
        "annualized_cost_eur": [1_500_000.0, 2_000_000.0],
    })
    messages = explain_sensitivity_results(frame, "electricity_price_multiplier")
    assert any("PV capacity increases" in m for m in messages)
    assert any("battery energy increases" in m for m in messages)
    assert any("Annualized cost increases" in m for m in messages)


def test_sensitivity_explanation_brackets_battery_transition():
    import pandas as pd
    frame = pd.DataFrame({
        "status": ["optimal", "optimal", "optimal"],
        "input_value": [0.70, 0.74, 0.76],
        "pv_capacity_kw": [4000.0, 4050.0, 4050.0],
        "battery_energy_capacity_kwh": [500.0, 100.0, 0.0],
        "annualized_cost_eur": [1_700_000.0, 1_710_000.0, 1_715_000.0],
    })
    messages = explain_sensitivity_results(frame, "battery_capex_multiplier")
    assert any("0.74× and 0.76×" in m for m in messages)
