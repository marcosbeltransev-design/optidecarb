"""Run and persist the public-data-calibrated Castellón ceramic case."""
from __future__ import annotations

import json
from pathlib import Path

from industrial_energy_lab.case_studies.bundles import CERAMIC_CASE_ID, load_case_bundle
from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.frontier import cost_decarbonization_frontier
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION

ROOT = Path(__file__).resolve().parents[1]


def _result_dict(r):
    fields = (
        "status", "solver_backend", "objective_annualized_cost_eur", "pv_capacity_kw",
        "battery_energy_capacity_kwh", "battery_power_capacity_kw", "load_mwh",
        "pv_generation_mwh", "pv_self_consumption_mwh", "pv_export_mwh",
        "battery_charge_mwh", "battery_discharge_mwh", "battery_losses_mwh",
        "grid_import_mwh", "grid_export_mwh", "self_consumption_ratio",
        "self_sufficiency_ratio", "annualized_pv_cost_eur", "annualized_battery_cost_eur",
        "annual_pv_opex_eur", "annual_battery_opex_eur", "grid_purchase_cost_eur",
        "export_revenue_eur", "baseline_annual_cost_eur", "annual_saving_vs_baseline_eur",
        "initial_capex_eur", "project_npv_eur", "simple_payback_years",
        "baseline_emissions_tco2", "scenario_emissions_tco2", "emissions_reduction_tco2",
        "emissions_reduction_fraction", "abatement_cost_eur_per_tco2", "carbon_target",
        "carbon_constraint_binding", "model_build_seconds", "solve_seconds", "total_seconds",
    )
    return {name: getattr(r, name) for name in fields}


def main() -> None:
    bundle = load_case_bundle(CERAMIC_CASE_ID)
    cfg = bundle.config
    grid = GridAssumptions(cfg["grid_emissions_factor_kg_co2_per_mwh"])
    assumptions = optimization_assumptions_from_mapping(cfg)

    baseline = run_baseline(bundle.load, bundle.prices, grid)
    dispatch, economic = optimize_annual_system(
        bundle.load, bundle.pv, bundle.prices, grid, assumptions,
        export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"], carbon_target=0.0,
    )
    frontier = cost_decarbonization_frontier(
        bundle.load, bundle.pv, bundle.prices, grid, assumptions,
        export_price_eur_per_mwh=cfg["export_price_eur_per_mwh"],
        carbon_targets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5),
        economic_optimum=economic,
    )

    payload = {
        "case_name": bundle.label,
        "case_version": bundle.case_version,
        "dataset_version": bundle.dataset_version,
        "model_version": OPTIMIZATION_MODEL_VERSION,
        "reference_year": cfg["reference_year"],
        "classification": bundle.classification,
        "baseline": {
            "annual_load_mwh": baseline.annual_consumption_mwh,
            "energy_component_cost_eur": baseline.annual_energy_cost_eur,
            "grid_emissions_tco2": baseline.annual_emissions_tco2,
        },
        "economic_optimum": _result_dict(economic),
        "carbon_frontier": frontier.to_dict(orient="records"),
        "dispatch_checks": {
            "rows": len(dispatch) if dispatch is not None else None,
            "initial_soc_kwh": float(dispatch["soc_start_kwh"].iloc[0]) if dispatch is not None else None,
            "final_soc_kwh": float(dispatch["soc_kwh"].iloc[-1]) if dispatch is not None else None,
        },
    }
    out = ROOT / "cases" / "ceramic_castellon" / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "case_results_v1.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
