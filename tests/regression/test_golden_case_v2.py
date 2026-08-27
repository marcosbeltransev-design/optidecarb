import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.scenario import run_pv_battery_scenario
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[2]


def test_golden_case_v2() -> None:
    data = ROOT / "data" / "demo"
    expected = json.loads((ROOT / "tests" / "regression" / "golden_case_v2.json").read_text())
    a = json.loads((data / "scenario_assumptions.json").read_text())
    battery = BatterySpec(
        a["battery_energy_capacity_kwh"],
        a["battery_power_capacity_kw"],
        a["battery_charge_efficiency"],
        a["battery_discharge_efficiency"],
        a["battery_min_soc_fraction"],
        a["battery_max_soc_fraction"],
        a["battery_initial_soc_fraction"],
    )
    _, result = run_pv_battery_scenario(
        pd.read_csv(data / "industrial_load_8760.csv"),
        pd.read_csv(data / "pv_profile_8760.csv"),
        pd.read_csv(data / "electricity_prices_8760.csv"),
        GridAssumptions(a["grid_emissions_factor_kg_co2_per_mwh"]),
        pv_capacity_kw=a["pv_capacity_kw"],
        battery=battery,
        export_price_eur_per_mwh=a["export_price_eur_per_mwh"],
    )

    actual = result.__dict__
    assert actual["model_version"] == expected["model_version"]
    assert actual["dataset_version"] == expected["dataset_version"]
    assert actual["case_version"] == expected["case_version"]
    for key, expected_value in expected.items():
        if key.endswith("version"):
            continue
        tolerance = 0.50 if key.endswith("_eur") else 1e-6
        assert actual[key] == pytest.approx(expected_value, abs=tolerance)
