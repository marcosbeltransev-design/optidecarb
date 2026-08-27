from pathlib import Path

import pandas as pd
import pytest

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


def test_zero_battery_still_simulates_pv_direct_use_and_export() -> None:
    load, pv, price = _frames()
    dispatch, result = run_pv_battery_scenario(
        load,
        pv,
        price,
        GridAssumptions(180.0),
        pv_capacity_kw=4000.0,
        battery=BatterySpec.disabled(),
        export_price_eur_per_mwh=45.0,
    )
    assert dispatch["battery_charge_kwh"].sum() == 0.0
    assert dispatch["battery_discharge_kwh"].sum() == 0.0
    assert result.pv_generation_mwh > 0
    assert result.pv_export_mwh > 0
    assert result.grid_import_mwh < result.load_mwh


def test_zero_pv_with_battery_at_minimum_soc_behaves_as_grid_only() -> None:
    load, pv, price = _frames()
    battery = BatterySpec(
        energy_capacity_kwh=4000.0,
        power_capacity_kw=2000.0,
        charge_efficiency=0.95,
        discharge_efficiency=0.95,
        min_soc_fraction=0.10,
        max_soc_fraction=0.90,
        initial_soc_fraction=0.10,
    )
    dispatch, result = run_pv_battery_scenario(
        load,
        pv,
        price,
        GridAssumptions(180.0),
        pv_capacity_kw=0.0,
        battery=battery,
        export_price_eur_per_mwh=45.0,
    )
    assert dispatch["battery_charge_kwh"].sum() == 0.0
    assert dispatch["battery_discharge_kwh"].sum() == 0.0
    assert result.grid_import_mwh == pytest.approx(result.load_mwh, abs=1e-9)
    assert result.initial_soc_mwh == pytest.approx(result.final_soc_mwh, abs=1e-12)
