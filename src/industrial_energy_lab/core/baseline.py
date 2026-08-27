"""Grid-only baseline orchestration."""

from __future__ import annotations

import pandas as pd

from industrial_energy_lab.core.load import annual_consumption_mwh
from industrial_energy_lab.economics.emissions import grid_emissions_tco2
from industrial_energy_lab.schemas.models import BaselineResult, GridAssumptions
from industrial_energy_lab.utils.version import (
    BASELINE_CASE_VERSION,
    BASELINE_MODEL_VERSION,
    DATASET_VERSION,
)
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe


def annual_grid_cost_eur(load_kw: pd.Series, price_eur_per_mwh: pd.Series) -> float:
    """Return annual commodity energy cost for matched one-hour intervals."""

    if len(load_kw) != len(price_eur_per_mwh):
        raise ValueError("Load and price series must have the same length.")
    if load_kw.isna().any() or price_eur_per_mwh.isna().any():
        raise ValueError("Load and price series cannot contain NaN values.")
    if (load_kw < 0).any():
        raise ValueError("Load must be non-negative.")
    return float(((load_kw / 1000.0) * price_eur_per_mwh).sum())


def run_baseline(
    load_frame: pd.DataFrame,
    price_frame: pd.DataFrame,
    assumptions: GridAssumptions,
) -> BaselineResult:
    """Calculate annual demand, electricity cost and grid-related emissions."""

    load = validate_hourly_dataframe(load_frame, value_column="load_kw")
    price = validate_hourly_dataframe(
        price_frame,
        value_column="price_eur_per_mwh",
        allow_negative=True,
    )
    if not load["timestamp_utc"].equals(price["timestamp_utc"]):
        raise ValueError("Load and price timestamps must match exactly.")

    consumption_mwh = annual_consumption_mwh(load["load_kw"])
    cost_eur = annual_grid_cost_eur(load["load_kw"], price["price_eur_per_mwh"])
    emissions_tco2 = grid_emissions_tco2(
        consumption_mwh,
        assumptions.emissions_factor_kg_co2_per_mwh,
    )

    return BaselineResult(
        annual_consumption_mwh=consumption_mwh,
        annual_energy_cost_eur=cost_eur,
        annual_emissions_tco2=emissions_tco2,
        model_version=BASELINE_MODEL_VERSION,
        dataset_version=DATASET_VERSION,
        case_version=BASELINE_CASE_VERSION,
    )
