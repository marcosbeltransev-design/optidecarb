"""Iteration 2 annual PV+battery scenario orchestration."""

from __future__ import annotations

import pandas as pd

from industrial_energy_lab.core.baseline import annual_grid_cost_eur
from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.dispatch import annual_dispatch_summary, greedy_pv_battery_dispatch
from industrial_energy_lab.core.pv import pv_generation_kwh
from industrial_energy_lab.economics.emissions import grid_emissions_tco2
from industrial_energy_lab.economics.grid import annual_grid_cashflow_eur
from industrial_energy_lab.schemas.models import GridAssumptions, ScenarioResult
from industrial_energy_lab.utils.version import DATASET_VERSION, SCENARIO_MODEL_VERSION, SCENARIO_CASE_VERSION
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe


def run_pv_battery_scenario(
    load_frame: pd.DataFrame,
    pv_profile_frame: pd.DataFrame,
    price_frame: pd.DataFrame,
    grid_assumptions: GridAssumptions,
    *,
    pv_capacity_kw: float,
    battery: BatterySpec,
    export_price_eur_per_mwh: float | pd.Series = 0.0,
) -> tuple[pd.DataFrame, ScenarioResult]:
    """Run one deterministic 8,760-hour PV+battery scenario."""

    load = validate_hourly_dataframe(load_frame, value_column="load_kw")
    pv = validate_hourly_dataframe(
        pv_profile_frame,
        value_column="capacity_factor",
        min_value=0.0,
        max_value=1.0,
    )
    prices = validate_hourly_dataframe(
        price_frame,
        value_column="price_eur_per_mwh",
        allow_negative=True,
    )
    if not load["timestamp_utc"].equals(pv["timestamp_utc"]):
        raise ValueError("Load and PV timestamps must match exactly.")
    if not load["timestamp_utc"].equals(prices["timestamp_utc"]):
        raise ValueError("Load and price timestamps must match exactly.")

    generation = pv_generation_kwh(pv_capacity_kw, pv["capacity_factor"])
    dispatch = greedy_pv_battery_dispatch(
        load["timestamp_utc"],
        load["load_kw"],  # one-hour average kW -> same numeric interval kWh
        generation,
        battery,
    )
    physical = annual_dispatch_summary(dispatch)
    cashflow = annual_grid_cashflow_eur(
        dispatch["grid_import_kwh"],
        dispatch["grid_export_kwh"],
        prices["price_eur_per_mwh"],
        export_price_eur_per_mwh,
    )
    baseline_cost = annual_grid_cost_eur(load["load_kw"], prices["price_eur_per_mwh"])
    emissions = grid_emissions_tco2(
        physical["grid_import_mwh"],
        grid_assumptions.emissions_factor_kg_co2_per_mwh,
    )

    result = ScenarioResult(
        **physical,
        baseline_annual_energy_cost_eur=baseline_cost,
        annual_energy_purchase_cost_eur=cashflow["energy_purchase_cost_eur"],
        annual_export_revenue_eur=cashflow["export_revenue_eur"],
        annual_net_grid_energy_cost_eur=cashflow["net_grid_energy_cost_eur"],
        annual_operating_savings_eur=baseline_cost - cashflow["net_grid_energy_cost_eur"],
        annual_emissions_tco2=emissions,
        model_version=SCENARIO_MODEL_VERSION,
        dataset_version=DATASET_VERSION,
        case_version=SCENARIO_CASE_VERSION,
    )
    return dispatch, result
