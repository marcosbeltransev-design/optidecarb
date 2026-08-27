"""Generate deterministic 8,760-hour demo datasets.

These profiles are software-validation inputs, not measurements and not a model of
any named industrial facility. Run from the repository root.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260827
YEAR = 2025
HOURS = 8760
TARGET_ANNUAL_LOAD_MWH = 22_000.0
ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "demo"
META = ROOT / "data" / "metadata"


def _timestamps() -> pd.DatetimeIndex:
    return pd.date_range(f"{YEAR}-01-01T00:00:00Z", periods=HOURS, freq="h")


def make_load(index: pd.DatetimeIndex) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    hour = index.hour.to_numpy()
    weekday = index.dayofweek.to_numpy() < 5
    day_of_year = index.dayofyear.to_numpy()

    # ASSUMPTION: deliberately generic three-shift-like industrial profile.
    weekday_factor = np.where(weekday, 1.04, 0.92)
    shift_factor = np.where((hour >= 7) & (hour < 23), 1.05, 0.94)
    seasonality = 1.0 + 0.04 * np.cos(2 * np.pi * (day_of_year - 20) / 365.0)
    controlled_noise = rng.normal(loc=1.0, scale=0.025, size=HOURS)
    raw_kw = 2500.0 * weekday_factor * shift_factor * seasonality * controlled_noise
    raw_kw = np.clip(raw_kw, 500.0, None)

    # Rescale to an exact annual energy target so regression expectations are stable.
    load_kw = raw_kw * (TARGET_ANNUAL_LOAD_MWH * 1000.0 / raw_kw.sum())
    return pd.DataFrame({"timestamp_utc": index, "load_kw": load_kw})


def make_price(index: pd.DatetimeIndex) -> pd.DataFrame:
    hour = index.hour.to_numpy()
    day_of_year = index.dayofyear.to_numpy()
    weekday = index.dayofweek.to_numpy() < 5

    # ASSUMPTION: deterministic synthetic tariff shape for validation only.
    base = np.full(HOURS, 78.0)
    daytime = np.where((hour >= 8) & (hour < 18), 18.0, 0.0)
    evening = np.where((hour >= 18) & (hour < 22), 27.0, 0.0)
    overnight = np.where((hour >= 0) & (hour < 6), -14.0, 0.0)
    weekday_adder = np.where(weekday, 4.0, -3.0)
    seasonal = 6.0 * np.cos(2 * np.pi * (day_of_year - 15) / 365.0)
    price = base + daytime + evening + overnight + weekday_adder + seasonal
    return pd.DataFrame({"timestamp_utc": index, "price_eur_per_mwh": price})


def make_pv(index: pd.DatetimeIndex) -> pd.DataFrame:
    hour = index.hour.to_numpy() + 0.5
    day_of_year = index.dayofyear.to_numpy()

    # ASSUMPTION: normalized synthetic solar shape used to validate the Iteration 2
    # PV and battery engine. It is not a PVGIS or measured production profile.
    daylight = np.maximum(0.0, np.sin(np.pi * (hour - 6.0) / 12.0))
    seasonal = 0.72 + 0.28 * np.sin(2 * np.pi * (day_of_year - 80) / 365.0)
    capacity_factor = np.clip(daylight * seasonal, 0.0, 1.0)
    return pd.DataFrame({"timestamp_utc": index, "capacity_factor": capacity_factor})


def write_metadata(filename: str, value_column: str, units: str, description: str) -> None:
    metadata = {
        "name": filename,
        "source": "Synthetic deterministic generator included in this repository",
        "status": "ASSUMPTION / SOFTWARE VALIDATION DATA",
        "generated_on": "2026-08-27",
        "generator": "scripts/generate_demo_data.py",
        "seed": SEED if "load" in filename else None,
        "calendar_year": YEAR,
        "timezone": "UTC",
        "case_timezone_context": "Europe/Madrid",
        "dst_policy": "Engine inputs use an uninterrupted UTC hourly index; local DST normalization is external to the engine.",
        "rows": HOURS,
        "value_column": value_column,
        "units": units,
        "license": "MIT (project-generated synthetic data)",
        "dataset_version": "demo-v1",
        "description": description,
    }
    (META / filename.replace(".csv", ".json")).write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    idx = _timestamps()

    load = make_load(idx)
    price = make_price(idx)
    pv = make_pv(idx)

    load.to_csv(DEMO / "industrial_load_8760.csv", index=False, float_format="%.6f")
    price.to_csv(DEMO / "electricity_prices_8760.csv", index=False, float_format="%.6f")
    pv.to_csv(DEMO / "pv_profile_8760.csv", index=False, float_format="%.8f")

    write_metadata(
        "industrial_load_8760.csv",
        "load_kw",
        "kW average over each 1-hour interval",
        "Generic synthetic industrial electrical demand, rescaled to exactly 22,000 MWh/year.",
    )
    write_metadata(
        "electricity_prices_8760.csv",
        "price_eur_per_mwh",
        "EUR/MWh",
        "Synthetic hourly electricity price shape for software validation; not a historical Spanish market series.",
    )
    write_metadata(
        "pv_profile_8760.csv",
        "capacity_factor",
        "p.u. [0,1]",
        "Synthetic normalized PV reference profile used by the Iteration 2 physical simulation; not PVGIS data.",
    )

    assumptions = {
        "status": "ASSUMPTION / SOFTWARE VALIDATION ONLY",
        "grid_emissions_factor_kg_co2_per_mwh": 180.0,
        "note": "This value is intentionally synthetic in Iteration 1 and is not presented as a current Spanish grid factor.",
        "model_version": "0.1.0",
        "dataset_version": "demo-v1",
        "case_version": "golden-v1",
    }
    (DEMO / "baseline_assumptions.json").write_text(
        json.dumps(assumptions, indent=2) + "\n", encoding="utf-8"
    )

    scenario_assumptions = {
        "status": "ASSUMPTION / SOFTWARE VALIDATION ONLY",
        "pv_capacity_kw": 4000.0,
        "battery_energy_capacity_kwh": 4000.0,
        "battery_power_capacity_kw": 2000.0,
        "battery_charge_efficiency": 0.95,
        "battery_discharge_efficiency": 0.95,
        "battery_min_soc_fraction": 0.10,
        "battery_max_soc_fraction": 0.90,
        "battery_initial_soc_fraction": 0.10,
        "export_price_eur_per_mwh": 45.0,
        "grid_emissions_factor_kg_co2_per_mwh": 180.0,
        "emissions_export_credit": False,
        "note": "Synthetic Iteration 2 regression assumptions; not a recommendation or current Spanish market dataset.",
        "model_version": "0.2.0",
        "dataset_version": "demo-v1",
        "case_version": "golden-v2"
    }
    (DEMO / "scenario_assumptions.json").write_text(
        json.dumps(scenario_assumptions, indent=2) + "\n", encoding="utf-8"
    )

    optimization_assumptions = {
        "status": "ASSUMPTION / SOFTWARE VALIDATION ONLY",
        "pv_capex_eur_per_kw": 1600.0,
        "pv_opex_eur_per_kw_year": 10.0,
        "pv_lifetime_years": 25,
        "battery_energy_capex_eur_per_kwh": 150.0,
        "battery_power_capex_eur_per_kw": 100.0,
        "battery_opex_eur_per_kwh_year": 2.0,
        "battery_opex_eur_per_kw_year": 1.0,
        "battery_lifetime_years": 15,
        "wacc": 0.05,
        "project_life_years": 15,
        "battery_charge_efficiency": 0.95,
        "battery_discharge_efficiency": 0.95,
        "battery_min_soc_fraction": 0.10,
        "battery_max_soc_fraction": 0.90,
        "battery_initial_soc_fraction": 0.10,
        "max_pv_capacity_kw": 12000.0,
        "max_battery_energy_kwh": 12000.0,
        "max_battery_power_kw": 6000.0,
        "export_price_eur_per_mwh": 20.0,
        "grid_emissions_factor_kg_co2_per_mwh": 180.0,
        "emissions_export_credit": False,
        "battery_charging_source": "PV surplus only",
        "optimization_problem": "linear programming (LP)",
        "solver_backend": "HiGHS via scipy.optimize.linprog",
        "note": "Synthetic Iteration 3 optimization assumptions for software validation; not a recommendation or current Spanish market dataset.",
        "model_version": "0.3.0",
        "dataset_version": "demo-v1",
        "case_version": "golden-v3"
    }
    (DEMO / "optimization_assumptions.json").write_text(
        json.dumps(optimization_assumptions, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
