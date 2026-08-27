"""Baseline energy balance for the grid-only system."""

from __future__ import annotations

import pandas as pd


def grid_only_balance(load_kw: pd.Series) -> pd.DataFrame:
    """Return an exact grid-only hourly energy balance.

    In Iteration 1 there is no PV or battery. Therefore grid import must equal load
    in every hour and export is identically zero.
    """

    if load_kw.isna().any() or (load_kw < 0).any():
        raise ValueError("Load must be non-negative and complete.")

    balance = pd.DataFrame(
        {
            "load_kwh": load_kw.astype(float).to_numpy(),
            "grid_import_kwh": load_kw.astype(float).to_numpy(),
            "grid_export_kwh": 0.0,
        }
    )
    residual = balance["grid_import_kwh"] - balance["load_kwh"]
    if not (residual.abs() < 1e-9).all():
        raise RuntimeError("Baseline energy balance failed conservation check.")
    return balance
