import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.scenario import run_pv_battery_scenario
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "demo"


def _frames():
    return (
        pd.read_csv(DATA / "industrial_load_8760.csv"),
        pd.read_csv(DATA / "pv_profile_8760.csv"),
        pd.read_csv(DATA / "electricity_prices_8760.csv"),
    )


def test_annual_demo_scenario_obeys_physical_invariants() -> None:
    load, pv, price = _frames()
    assumptions = json.loads((DATA / "scenario_assumptions.json").read_text())
    battery = BatterySpec(
        assumptions["battery_energy_capacity_kwh"],
        assumptions["battery_power_capacity_kw"],
        assumptions["battery_charge_efficiency"],
        assumptions["battery_discharge_efficiency"],
        assumptions["battery_min_soc_fraction"],
        assumptions["battery_max_soc_fraction"],
        assumptions["battery_initial_soc_fraction"],
    )
    dispatch, result = run_pv_battery_scenario(
        load,
        pv,
        price,
        GridAssumptions(assumptions["grid_emissions_factor_kg_co2_per_mwh"]),
        pv_capacity_kw=assumptions["pv_capacity_kw"],
        battery=battery,
        export_price_eur_per_mwh=assumptions["export_price_eur_per_mwh"],
    )

    load_residual = dispatch["load_kwh"] - (
        dispatch["pv_to_load_kwh"]
        + dispatch["battery_discharge_kwh"]
        + dispatch["grid_import_kwh"]
    )
    pv_residual = dispatch["pv_generation_kwh"] - (
        dispatch["pv_to_load_kwh"]
        + dispatch["pv_to_battery_kwh"]
        + dispatch["pv_export_kwh"]
    )
    total_residual = (
        dispatch["pv_generation_kwh"]
        + dispatch["grid_import_kwh"]
        + dispatch["soc_start_kwh"]
        - dispatch["load_kwh"]
        - dispatch["grid_export_kwh"]
        - dispatch["battery_losses_kwh"]
        - dispatch["soc_kwh"]
    )

    assert load_residual.abs().max() < 1e-8
    assert pv_residual.abs().max() < 1e-8
    assert total_residual.abs().max() < 1e-8
    assert (dispatch["battery_charge_kwh"] - dispatch["pv_to_battery_kwh"]).abs().max() < 1e-12
    assert (dispatch["grid_export_kwh"] - dispatch["pv_export_kwh"]).abs().max() < 1e-12
    assert not ((dispatch["battery_charge_kwh"] > 1e-9) & (dispatch["battery_discharge_kwh"] > 1e-9)).any()
    assert not ((dispatch["grid_import_kwh"] > 1e-9) & (dispatch["grid_export_kwh"] > 1e-9)).any()
    assert dispatch["soc_kwh"].between(battery.min_soc_kwh - 1e-8, battery.max_soc_kwh + 1e-8).all()
    assert dispatch["battery_charge_kwh"].max() <= battery.power_capacity_kw + 1e-8
    assert dispatch["battery_discharge_kwh"].max() <= battery.power_capacity_kw + 1e-8
    assert result.grid_import_mwh < result.load_mwh
    assert result.annual_operating_savings_eur > 0


def test_zero_pv_and_zero_battery_reproduce_iteration_1_baseline() -> None:
    load, pv, price = _frames()
    grid = GridAssumptions(180.0)
    baseline = run_baseline(load, price, grid)
    dispatch, scenario = run_pv_battery_scenario(
        load,
        pv,
        price,
        grid,
        pv_capacity_kw=0.0,
        battery=BatterySpec.disabled(),
        export_price_eur_per_mwh=45.0,
    )

    assert scenario.load_mwh == pytest.approx(baseline.annual_consumption_mwh, abs=1e-9)
    assert scenario.grid_import_mwh == pytest.approx(baseline.annual_consumption_mwh, abs=1e-9)
    assert scenario.grid_export_mwh == pytest.approx(0.0, abs=1e-12)
    assert scenario.annual_net_grid_energy_cost_eur == pytest.approx(
        baseline.annual_energy_cost_eur, abs=1e-6
    )
    assert scenario.annual_emissions_tco2 == pytest.approx(baseline.annual_emissions_tco2, abs=1e-9)
    assert scenario.annual_operating_savings_eur == pytest.approx(0.0, abs=1e-6)
    assert dispatch["battery_charge_kwh"].sum() == 0.0
    assert dispatch["battery_discharge_kwh"].sum() == 0.0
