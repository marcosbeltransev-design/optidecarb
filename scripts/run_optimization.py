"""Run the synthetic Iteration 3 economic optimum and carbon frontier."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.frontier import cost_decarbonization_frontier
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "demo"


def main() -> None:
    load = pd.read_csv(DEMO / "industrial_load_8760.csv")
    prices = pd.read_csv(DEMO / "electricity_prices_8760.csv")
    pv = pd.read_csv(DEMO / "pv_profile_8760.csv")
    config = json.loads((DEMO / "optimization_assumptions.json").read_text())
    assumptions = optimization_assumptions_from_mapping(config)
    grid = GridAssumptions(float(config["grid_emissions_factor_kg_co2_per_mwh"]))
    export_price = float(config["export_price_eur_per_mwh"])

    _, economic = optimize_annual_system(
        load, pv, prices, grid, assumptions,
        export_price_eur_per_mwh=export_price, carbon_target=0.0,
    )
    print("Economic optimum")
    print(f"  status: {economic.status}")
    print(f"  PV: {economic.pv_capacity_kw / 1000:.3f} MW")
    print(f"  battery energy: {economic.battery_energy_capacity_kwh / 1000:.3f} MWh")
    print(f"  battery power: {economic.battery_power_capacity_kw / 1000:.3f} MW")
    print(f"  annualized cost: EUR {economic.objective_annualized_cost_eur:,.2f}/year")
    print(f"  CO2 reduction: {economic.emissions_reduction_fraction:.2%}")

    frontier = cost_decarbonization_frontier(
        load, pv, prices, grid, assumptions,
        export_price_eur_per_mwh=export_price,
        economic_optimum=economic,
    )
    print("\nCost-decarbonization frontier")
    print(frontier[[
        "carbon_target", "status", "pv_capacity_kw",
        "battery_energy_capacity_kwh", "battery_power_capacity_kw",
        "annualized_cost_eur", "emissions_reduction_fraction",
        "carbon_constraint_binding",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
