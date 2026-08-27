import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.utils.version import DATASET_VERSION, OPTIMIZATION_CASE_VERSION, OPTIMIZATION_MODEL_VERSION

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "data" / "demo"
GOLDEN = json.loads((ROOT / "tests" / "regression" / "golden_case_v3.json").read_text())


@pytest.fixture(scope="module")
def solved_cases():
    cfg = json.loads((DEMO / "optimization_assumptions.json").read_text())
    assumptions = optimization_assumptions_from_mapping(cfg)
    grid = GridAssumptions(cfg["grid_emissions_factor_kg_co2_per_mwh"])
    load = pd.read_csv(DEMO / "industrial_load_8760.csv")
    pv = pd.read_csv(DEMO / "pv_profile_8760.csv")
    prices = pd.read_csv(DEMO / "electricity_prices_8760.csv")
    kwargs = dict(export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"])
    economic_dispatch, economic = optimize_annual_system(load, pv, prices, grid, assumptions, carbon_target=0.0, **kwargs)
    carbon_dispatch, carbon = optimize_annual_system(load, pv, prices, grid, assumptions, carbon_target=0.40, **kwargs)
    return economic_dispatch, economic, carbon_dispatch, carbon


def assert_result(result, expected):
    assert result.status == expected["status"]
    numeric = [
        "objective_annualized_cost_eur", "pv_capacity_kw", "battery_energy_capacity_kwh",
        "battery_power_capacity_kw", "grid_import_mwh", "grid_export_mwh",
        "initial_capex_eur", "project_npv_eur", "simple_payback_years",
        "baseline_emissions_tco2", "scenario_emissions_tco2", "emissions_reduction_tco2",
        "emissions_reduction_fraction", "abatement_cost_eur_per_tco2",
    ]
    for field in numeric:
        assert getattr(result, field) == pytest.approx(expected[field], rel=2e-7, abs=2e-6), field
    assert result.carbon_constraint_binding is expected["carbon_constraint_binding"]


def test_golden_v3_economic_optimum_and_physical_invariants(solved_cases):
    dispatch, result, _, _ = solved_cases
    assert GOLDEN["model_version"] == OPTIMIZATION_MODEL_VERSION
    assert GOLDEN["dataset_version"] == DATASET_VERSION
    assert GOLDEN["case_version"] == OPTIMIZATION_CASE_VERSION
    assert_result(result, GOLDEN["economic_optimum"])
    assert len(dispatch) == 8760
    assert (dispatch["grid_import_kwh"] >= -1e-8).all()
    assert (dispatch["grid_export_kwh"] >= -1e-8).all()
    assert (dispatch["battery_charge_kwh"] * dispatch["battery_discharge_kwh"] <= 1e-7).all()
    assert (dispatch["grid_import_kwh"] * dispatch["grid_export_kwh"] <= 1e-7).all()
    assert dispatch["soc_kwh"].iloc[-1] == pytest.approx(
        0.1 * result.battery_energy_capacity_kwh, abs=1e-6
    )


def test_golden_v3_binding_40pct_carbon_case(solved_cases):
    _, _, dispatch, result = solved_cases
    assert_result(result, GOLDEN["carbon_target_40pct"])
    assert result.emissions_reduction_fraction == pytest.approx(0.40, abs=1e-7)
    assert result.carbon_constraint_binding is True
    assert dispatch["soc_kwh"].iloc[-1] == pytest.approx(
        0.1 * result.battery_energy_capacity_kwh, abs=1e-6
    )
