import pytest

from industrial_energy_lab.explainability.calculations import WORKED_METRIC_IDS, explain_calculation
from industrial_energy_lab.optimization.model import OptimizationResult


def result(**overrides):
    values = dict(
        status="optimal", solver_message="ok", objective_annualized_cost_eur=880_000.0,
        pv_capacity_kw=3000.0, battery_energy_capacity_kwh=0.0, battery_power_capacity_kw=0.0,
        load_mwh=15_000.0, pv_generation_mwh=4_800.0, pv_self_consumption_mwh=4_560.0,
        pv_export_mwh=240.0, battery_charge_mwh=0.0, battery_discharge_mwh=0.0,
        battery_losses_mwh=0.0, grid_import_mwh=10_440.0, grid_export_mwh=240.0,
        self_consumption_ratio=0.95, self_sufficiency_ratio=0.304,
        annualized_pv_cost_eur=170_000.0, annualized_battery_cost_eur=0.0,
        annual_pv_opex_eur=21_000.0, annual_battery_opex_eur=0.0,
        grid_purchase_cost_eur=710_000.0, export_revenue_eur=0.0,
        baseline_annual_cost_eur=983_000.0, annual_saving_vs_baseline_eur=103_000.0,
        initial_capex_eur=2_100_000.0, project_npv_eur=500_000.0, simple_payback_years=8.33,
        baseline_emissions_tco2=1626.0, scenario_emissions_tco2=1131.76,
        emissions_reduction_tco2=494.24, emissions_reduction_fraction=494.24/1626.0,
        abatement_cost_eur_per_tco2=(880_000.0-983_000.0)/494.24,
        carbon_target=0.0, carbon_constraint_binding=False, carbon_constraint_slack_tco2=None,
        model_build_seconds=0.01, solve_seconds=0.01, total_seconds=0.02, solver_backend="test",
    )
    values.update(overrides)
    return OptimizationResult(**values)


PARAMS = {
    "grid_emissions_factor_kg_co2_per_mwh": 108.4,
    "pv_capex_eur_per_kw": 700.0,
    "battery_energy_capex_eur_per_kwh": 240.0,
    "battery_power_capex_eur_per_kw": 120.0,
    "pv_lifetime_years": 25,
    "wacc": 0.05,
    "project_life_years": 15,
}


def test_self_sufficiency_uses_real_result_numbers():
    c = explain_calculation("self_sufficiency", result(), PARAMS)
    assert c.result_value == pytest.approx((15000-10440)/15000)
    assert "15,000.00" in c.substitution
    assert "MWh / MWh" in c.unit_check


def test_self_consumption_is_not_self_sufficiency():
    c = explain_calculation("self_consumption", result(), PARAMS)
    assert c.result_value == pytest.approx(4560/4800)
    assert "what share of the PV" in c.interpretation


def test_emission_calculation_has_dimensional_check():
    r = result(scenario_emissions_tco2=10440*108.4/1000)
    c = explain_calculation("scenario_emissions", r, PARAMS)
    assert c.result_value == pytest.approx(1131.696)
    assert "kgCO₂/MWh" in c.unit_check


def test_abatement_cost_sign_is_transparent():
    c = explain_calculation("abatement_cost", result(), PARAMS)
    assert c.result_value < 0
    assert "Negative means" in c.interpretation
    assert c.result_unit == "€/tCO₂"


def test_crf_uses_current_wacc_and_pv_lifetime():
    c = explain_calculation("crf", result(), PARAMS)
    assert c.result_value == pytest.approx(0.0709524573)
    assert "25" in c.substitution


def test_initial_capex_substitution_uses_unit_costs():
    c = explain_calculation("initial_capex", result(), PARAMS)
    assert c.result_value == pytest.approx(2_100_000.0)
    assert "3,000.0×700" in c.substitution


def test_payback_and_npv_use_operating_cash_benefit_not_annualized_saving():
    p = explain_calculation("payback", result(), PARAMS)
    n = explain_calculation("npv", result(), PARAMS)
    assert p.inputs[1][1] == pytest.approx(252_000.0)
    assert "time value" in p.interpretation
    assert "automatic build" in n.interpretation


def test_all_declared_worked_metrics_are_implemented():
    r = result()
    # Adjust values that should be internally consistent with the example factor.
    r = result(
        baseline_emissions_tco2=15_000*108.4/1000,
        scenario_emissions_tco2=10_440*108.4/1000,
        emissions_reduction_tco2=(15_000-10_440)*108.4/1000,
        emissions_reduction_fraction=(15_000-10_440)/15_000,
        abatement_cost_eur_per_tco2=(880_000-983_000)/((15_000-10_440)*108.4/1000),
    )
    for metric_id in WORKED_METRIC_IDS:
        c = explain_calculation(metric_id, r, PARAMS)
        assert c.formula and c.substitution and c.interpretation
