"""Small hand-checkable examples used by Student Learning Lab."""
from __future__ import annotations

import pandas as pd

from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.dispatch import greedy_pv_battery_dispatch
from industrial_energy_lab.economics.cashflows import capital_recovery_factor


def energy_from_power(power_mw: float, hours: float) -> float:
    if power_mw < 0 or hours < 0:
        raise ValueError("power_mw and hours must be non-negative")
    return float(power_mw * hours)


def battery_duration_hours(energy_mwh: float, power_mw: float) -> float:
    if energy_mwh < 0:
        raise ValueError("energy_mwh must be non-negative")
    if power_mw <= 0:
        raise ValueError("power_mw must be positive")
    return float(energy_mwh / power_mw)


def co2_from_grid_energy_tco2(grid_mwh: float, emission_factor_kg_per_mwh: float) -> float:
    if grid_mwh < 0 or emission_factor_kg_per_mwh < 0:
        raise ValueError("Energy and emission factor must be non-negative")
    return float(grid_mwh * emission_factor_kg_per_mwh / 1000.0)


def crf_learning_example(wacc: float = 0.05, lifetime_years: int = 25, investment_eur: float = 1_000_000.0) -> dict[str, float]:
    if investment_eur < 0:
        raise ValueError("investment_eur must be non-negative")
    crf = capital_recovery_factor(wacc, lifetime_years)
    return {"wacc": float(wacc), "lifetime_years": float(lifetime_years), "investment_eur": float(investment_eur), "crf": crf, "annualized_capex_eur": investment_eur * crf}


def three_hour_battery_lab() -> pd.DataFrame:
    """Return the exact 3-hour example already validated by the physical engine."""
    timestamps = pd.Series(pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"))
    spec = BatterySpec(
        energy_capacity_kwh=20.0, power_capacity_kw=20.0,
        charge_efficiency=0.90, discharge_efficiency=0.90,
        min_soc_fraction=0.0, max_soc_fraction=1.0, initial_soc_fraction=0.0,
    )
    return greedy_pv_battery_dispatch(
        timestamps,
        pd.Series([10.0, 10.0, 10.0]),
        pd.Series([0.0, 20.0, 0.0]),
        spec,
    )


def self_consumption_ratio(pv_used_mwh: float, pv_generation_mwh: float) -> float:
    if pv_used_mwh < 0 or pv_generation_mwh < 0:
        raise ValueError("Energy values must be non-negative")
    if pv_used_mwh > pv_generation_mwh + 1e-9:
        raise ValueError("PV used onsite cannot exceed PV generation")
    return 0.0 if pv_generation_mwh == 0 else float(pv_used_mwh / pv_generation_mwh)


def self_sufficiency_ratio(load_mwh: float, grid_import_mwh: float) -> float:
    if load_mwh < 0 or grid_import_mwh < 0:
        raise ValueError("Energy values must be non-negative")
    if grid_import_mwh > load_mwh + 1e-9:
        raise ValueError("Grid import cannot exceed load in this PV-only-battery model")
    return 0.0 if load_mwh == 0 else float((load_mwh - grid_import_mwh) / load_mwh)
