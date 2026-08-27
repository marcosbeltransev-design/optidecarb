"""Configuration helpers for the versioned optimization assumptions."""
from __future__ import annotations

from collections.abc import Mapping

from industrial_energy_lab.optimization.model import OptimizationAssumptions, OptimizationBounds


def optimization_assumptions_from_mapping(values: Mapping[str, object]) -> OptimizationAssumptions:
    """Build validated optimizer assumptions from a JSON-like mapping."""
    bounds = OptimizationBounds(
        max_pv_capacity_kw=float(values["max_pv_capacity_kw"]),
        max_battery_energy_kwh=float(values["max_battery_energy_kwh"]),
        max_battery_power_kw=float(values["max_battery_power_kw"]),
    )
    return OptimizationAssumptions(
        pv_capex_eur_per_kw=float(values["pv_capex_eur_per_kw"]),
        pv_opex_eur_per_kw_year=float(values["pv_opex_eur_per_kw_year"]),
        pv_lifetime_years=int(values["pv_lifetime_years"]),
        battery_energy_capex_eur_per_kwh=float(values["battery_energy_capex_eur_per_kwh"]),
        battery_power_capex_eur_per_kw=float(values["battery_power_capex_eur_per_kw"]),
        battery_opex_eur_per_kwh_year=float(values["battery_opex_eur_per_kwh_year"]),
        battery_opex_eur_per_kw_year=float(values["battery_opex_eur_per_kw_year"]),
        battery_lifetime_years=int(values["battery_lifetime_years"]),
        wacc=float(values["wacc"]),
        project_life_years=int(values["project_life_years"]),
        battery_charge_efficiency=float(values["battery_charge_efficiency"]),
        battery_discharge_efficiency=float(values["battery_discharge_efficiency"]),
        battery_min_soc_fraction=float(values["battery_min_soc_fraction"]),
        battery_max_soc_fraction=float(values["battery_max_soc_fraction"]),
        battery_initial_soc_fraction=float(values["battery_initial_soc_fraction"]),
        bounds=bounds,
    )
