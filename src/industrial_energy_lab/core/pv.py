"""Offline photovoltaic generation helpers."""

from __future__ import annotations

import pandas as pd


def pv_generation_kwh(
    capacity_kw: float,
    capacity_factor: pd.Series,
    *,
    interval_hours: float = 1.0,
) -> pd.Series:
    """Return AC PV energy available in each interval.

    ``capacity_factor`` is dimensionless and must be within [0, 1]. For the MVP,
    ``capacity_kw`` represents installed AC-equivalent capacity and each interval is
    one hour unless explicitly supplied otherwise.
    """

    if capacity_kw < 0:
        raise ValueError("PV capacity must be non-negative.")
    if interval_hours <= 0:
        raise ValueError("interval_hours must be positive.")
    if capacity_factor.isna().any():
        raise ValueError("PV capacity factor cannot contain NaN values.")
    cf = pd.to_numeric(capacity_factor, errors="raise").astype(float)
    if ((cf < 0) | (cf > 1)).any():
        raise ValueError("PV capacity factor must be within [0, 1].")
    return capacity_kw * cf * interval_hours


def annual_pv_generation_mwh(generation_kwh: pd.Series) -> float:
    """Return annual PV energy in MWh from non-negative interval energy."""

    if generation_kwh.isna().any() or (generation_kwh < 0).any():
        raise ValueError("PV generation must be non-negative and complete.")
    return float(generation_kwh.sum() / 1000.0)
