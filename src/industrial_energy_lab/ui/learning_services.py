"""Thin orchestration layer for Student Learning Lab.

The learning UI calls the same validated engine as the rest of OptiDecarb. Full 8,760-hour
experiments are deliberately on demand and change one assumption at a time.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from industrial_energy_lab.case_studies.bundles import load_case_bundle
from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.scenario import run_pv_battery_scenario
from industrial_energy_lab.learning.experiments import modified_parameters, result_comparison
from industrial_energy_lab.optimization.model import OptimizationResult
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.ui.services import run_optimization_request, validate_custom_load


@dataclass(frozen=True)
class ExperimentRun:
    experiment_id: str
    before: OptimizationResult | None
    after: OptimizationResult | None
    comparison: tuple[dict[str, Any], ...]
    special_metrics: tuple[dict[str, Any], ...] = ()


def run_guided_experiment(
    parameters: dict[str, Any], experiment_id: str, *, case_id: str, load_frame: pd.DataFrame | None = None
) -> ExperimentRun:
    """Run one student experiment without changing the active application parameters."""
    base_params = dict(parameters)
    if experiment_id == "carbon_20_to_40":
        _, before = run_optimization_request(base_params, load_frame, carbon_target=0.20, case_id=case_id)
        _, after = run_optimization_request(base_params, load_frame, carbon_target=0.40, case_id=case_id)
        return ExperimentRun(experiment_id, before, after, tuple(result_comparison(before, after)))

    if experiment_id == "pv_oversizing":
        _, economic = run_optimization_request(base_params, load_frame, carbon_target=0.0, case_id=case_id)
        if economic.status != "optimal" or economic.pv_capacity_kw is None:
            return ExperimentRun(experiment_id, economic, None, ())
        bundle = load_case_bundle(case_id)
        load = bundle.load if load_frame is None else validate_custom_load(load_frame, case_id)
        prices = bundle.prices.copy()
        prices["price_eur_per_mwh"] *= float(base_params.get("import_price_multiplier", 1.0))
        grid = GridAssumptions(float(base_params["grid_emissions_factor_kg_co2_per_mwh"]))
        base_pv = float(economic.pv_capacity_kw)
        _, base_scenario = run_pv_battery_scenario(
            load, bundle.pv, prices, grid, pv_capacity_kw=base_pv, battery=BatterySpec.disabled(),
            export_price_eur_per_mwh=float(base_params["export_price_eur_per_mwh"]),
        )
        _, over_scenario = run_pv_battery_scenario(
            load, bundle.pv, prices, grid, pv_capacity_kw=base_pv * 1.5, battery=BatterySpec.disabled(),
            export_price_eur_per_mwh=float(base_params["export_price_eur_per_mwh"]),
        )
        rows = (
            {"metric": "PV capacity", "before": base_pv, "after": base_pv*1.5, "delta": base_pv*0.5, "unit": "kW"},
            {"metric": "PV self-consumption", "before": base_scenario.self_consumption_ratio, "after": over_scenario.self_consumption_ratio, "delta": over_scenario.self_consumption_ratio-base_scenario.self_consumption_ratio, "unit": "fraction"},
            {"metric": "Grid import", "before": base_scenario.grid_import_mwh, "after": over_scenario.grid_import_mwh, "delta": over_scenario.grid_import_mwh-base_scenario.grid_import_mwh, "unit": "MWh/year"},
            {"metric": "Grid export", "before": base_scenario.grid_export_mwh, "after": over_scenario.grid_export_mwh, "delta": over_scenario.grid_export_mwh-base_scenario.grid_export_mwh, "unit": "MWh/year"},
        )
        return ExperimentRun(experiment_id, economic, None, (), rows)

    varied = modified_parameters(base_params, experiment_id)
    _, before = run_optimization_request(base_params, load_frame, carbon_target=0.0, case_id=case_id)
    _, after = run_optimization_request(varied, load_frame, carbon_target=0.0, case_id=case_id)
    return ExperimentRun(experiment_id, before, after, tuple(result_comparison(before, after)))
