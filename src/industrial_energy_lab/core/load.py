"""Load-series input helpers."""

from pathlib import Path

import pandas as pd

from industrial_energy_lab.validation.datasets import validate_hourly_dataframe


def load_hourly_demand_csv(path: str | Path) -> pd.DataFrame:
    """Load and validate an 8,760-hour demand profile.

    ``load_kw`` is average electrical power during each one-hour interval, so its
    numeric value is also the interval energy in kWh.
    """

    frame = pd.read_csv(path)
    return validate_hourly_dataframe(frame, value_column="load_kw")


def annual_consumption_mwh(load_kw: pd.Series) -> float:
    """Convert hourly-average kW samples to annual MWh."""

    if load_kw.isna().any() or (load_kw < 0).any():
        raise ValueError("Load must be non-negative and complete.")
    return float(load_kw.sum() / 1000.0)
