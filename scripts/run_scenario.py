"""Run the deterministic Iteration 2 PV+battery golden scenario."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.scenario import run_pv_battery_scenario
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data" / "demo"
    assumptions = json.loads((data / "scenario_assumptions.json").read_text(encoding="utf-8"))
    battery = BatterySpec(
        energy_capacity_kwh=assumptions["battery_energy_capacity_kwh"],
        power_capacity_kw=assumptions["battery_power_capacity_kw"],
        charge_efficiency=assumptions["battery_charge_efficiency"],
        discharge_efficiency=assumptions["battery_discharge_efficiency"],
        min_soc_fraction=assumptions["battery_min_soc_fraction"],
        max_soc_fraction=assumptions["battery_max_soc_fraction"],
        initial_soc_fraction=assumptions["battery_initial_soc_fraction"],
    )
    _, result = run_pv_battery_scenario(
        pd.read_csv(data / "industrial_load_8760.csv"),
        pd.read_csv(data / "pv_profile_8760.csv"),
        pd.read_csv(data / "electricity_prices_8760.csv"),
        GridAssumptions(assumptions["grid_emissions_factor_kg_co2_per_mwh"]),
        pv_capacity_kw=assumptions["pv_capacity_kw"],
        battery=battery,
        export_price_eur_per_mwh=assumptions["export_price_eur_per_mwh"],
    )
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
