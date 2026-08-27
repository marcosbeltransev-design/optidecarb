"""Solve one ceramic-case sensitivity point in an isolated process.

Isolation is intentional: repeated annual HiGHS solves can degrade in a long-lived
process in the deployment/sandbox environment. The public UI therefore runs one
family on demand, while this script lets validation execute each point independently.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json

from industrial_energy_lab.case_studies.bundles import CERAMIC_CASE_ID, load_case_bundle
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("variable", choices=("electricity_price_multiplier", "pv_capex_multiplier", "battery_capex_multiplier", "wacc"))
    ap.add_argument("value", type=float)
    args = ap.parse_args()

    bundle = load_case_bundle(CERAMIC_CASE_ID)
    cfg = dict(bundle.config)
    assumptions = optimization_assumptions_from_mapping(cfg)
    prices = bundle.prices.copy()
    if args.variable == "electricity_price_multiplier":
        if args.value <= 0:
            raise ValueError("Price multiplier must be positive.")
        prices["price_eur_per_mwh"] *= args.value
    elif args.variable == "pv_capex_multiplier":
        if args.value <= 0:
            raise ValueError("CAPEX multiplier must be positive.")
        assumptions = replace(assumptions, pv_capex_eur_per_kw=assumptions.pv_capex_eur_per_kw * args.value)
    elif args.variable == "battery_capex_multiplier":
        if args.value <= 0:
            raise ValueError("CAPEX multiplier must be positive.")
        assumptions = replace(
            assumptions,
            battery_energy_capex_eur_per_kwh=assumptions.battery_energy_capex_eur_per_kwh * args.value,
            battery_power_capex_eur_per_kw=assumptions.battery_power_capex_eur_per_kw * args.value,
        )
    else:
        if args.value < 0:
            raise ValueError("WACC must be non-negative.")
        assumptions = replace(assumptions, wacc=args.value)

    _, result = optimize_annual_system(
        bundle.load,
        bundle.pv,
        prices,
        GridAssumptions(cfg["grid_emissions_factor_kg_co2_per_mwh"]),
        assumptions,
        export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"],
        carbon_target=0.0,
    )
    payload = {
        "input_variable": args.variable,
        "input_value": args.value,
        "status": result.status,
        "pv_capacity_kw": result.pv_capacity_kw,
        "battery_energy_capacity_kwh": result.battery_energy_capacity_kwh,
        "battery_power_capacity_kw": result.battery_power_capacity_kw,
        "annualized_cost_eur": result.objective_annualized_cost_eur,
        "project_npv_eur": result.project_npv_eur,
        "annual_saving_eur": result.annual_saving_vs_baseline_eur,
        "co2_reduction_fraction": result.emissions_reduction_fraction,
        "solve_seconds": result.solve_seconds,
        "total_seconds": result.total_seconds,
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
