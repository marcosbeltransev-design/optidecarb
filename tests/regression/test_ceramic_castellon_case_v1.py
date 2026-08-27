import json
from pathlib import Path

import pytest

from industrial_energy_lab.case_studies.bundles import CERAMIC_CASE_ID, load_case_bundle
from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = json.loads((ROOT / "tests/regression/ceramic_castellon_case_v1.json").read_text())


@pytest.fixture(scope="module")
def solved_case():
    bundle = load_case_bundle(CERAMIC_CASE_ID)
    cfg = bundle.config
    grid = GridAssumptions(cfg["grid_emissions_factor_kg_co2_per_mwh"])
    assumptions = optimization_assumptions_from_mapping(cfg)
    baseline = run_baseline(bundle.load, bundle.prices, grid)
    econ_dispatch, econ = optimize_annual_system(
        bundle.load, bundle.pv, bundle.prices, grid, assumptions,
        export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"], carbon_target=0.0,
    )
    carbon_dispatch, carbon = optimize_annual_system(
        bundle.load, bundle.pv, bundle.prices, grid, assumptions,
        export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"], carbon_target=0.40,
    )
    return bundle, baseline, econ_dispatch, econ, carbon_dispatch, carbon


def test_ceramic_case_economic_regression(solved_case):
    bundle, baseline, dispatch, result, _, _ = solved_case
    assert bundle.case_version == EXPECTED["case_version"]
    assert bundle.dataset_version == EXPECTED["dataset_version"]
    assert EXPECTED["model_version"] == OPTIMIZATION_MODEL_VERSION
    assert baseline.annual_consumption_mwh == pytest.approx(EXPECTED["annual_load_mwh"], abs=2e-6)
    assert baseline.annual_energy_cost_eur == pytest.approx(EXPECTED["baseline_energy_component_cost_eur"], rel=2e-8)
    assert baseline.annual_emissions_tco2 == pytest.approx(EXPECTED["baseline_grid_emissions_tco2"], rel=2e-8)
    exp = EXPECTED["economic_optimum"]
    assert result.status == exp["status"]
    for field in ("pv_capacity_kw","battery_energy_capacity_kwh","battery_power_capacity_kw","objective_annualized_cost_eur","grid_import_mwh","grid_export_mwh","initial_capex_eur","project_npv_eur","simple_payback_years","scenario_emissions_tco2","emissions_reduction_fraction","abatement_cost_eur_per_tco2"):
        assert getattr(result, field) == pytest.approx(exp[field], rel=3e-7, abs=3e-6), field
    assert len(dispatch) == 8760
    assert (dispatch["grid_import_kwh"] * dispatch["grid_export_kwh"] <= 1e-7).all()


def test_ceramic_case_binding_40pct_regression(solved_case):
    _, _, _, _, dispatch, result = solved_case
    exp = EXPECTED["carbon_target_40pct"]
    assert result.status == exp["status"]
    field_map = {"objective_annualized_cost_eur":"annualized_cost_eur", "scenario_emissions_tco2":"emissions_tco2"}
    for field in ("pv_capacity_kw","battery_energy_capacity_kwh","battery_power_capacity_kw","objective_annualized_cost_eur","grid_import_mwh","grid_export_mwh","initial_capex_eur","scenario_emissions_tco2","emissions_reduction_fraction","abatement_cost_eur_per_tco2"):
        assert getattr(result, field) == pytest.approx(exp[field_map.get(field, field)], rel=4e-7, abs=4e-6), field
    assert result.carbon_constraint_binding is True
    assert result.emissions_reduction_fraction == pytest.approx(0.40, abs=1e-7)
    assert dispatch["soc_kwh"].iloc[-1] == pytest.approx(0.1 * result.battery_energy_capacity_kwh, abs=1e-6)
