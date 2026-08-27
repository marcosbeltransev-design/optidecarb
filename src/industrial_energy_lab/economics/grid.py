"""Grid import/export cash-flow calculations."""

from __future__ import annotations

import numbers

import pandas as pd


def _price_series(price: float | pd.Series, length: int, label: str) -> pd.Series:
    if isinstance(price, numbers.Real):
        return pd.Series([float(price)] * length, dtype=float)
    series = pd.to_numeric(price, errors="raise").astype(float).reset_index(drop=True)
    if len(series) != length:
        raise ValueError(f"{label} must match the energy-series length.")
    if series.isna().any():
        raise ValueError(f"{label} cannot contain NaN values.")
    return series


def annual_grid_cashflow_eur(
    grid_import_kwh: pd.Series,
    grid_export_kwh: pd.Series,
    import_price_eur_per_mwh: float | pd.Series,
    export_price_eur_per_mwh: float | pd.Series = 0.0,
) -> dict[str, float]:
    """Return annual import cost, export revenue and net grid-energy cost."""

    imports = pd.to_numeric(grid_import_kwh, errors="raise").astype(float).reset_index(drop=True)
    exports = pd.to_numeric(grid_export_kwh, errors="raise").astype(float).reset_index(drop=True)
    if len(imports) != len(exports):
        raise ValueError("Grid import and export series must have the same length.")
    if imports.isna().any() or exports.isna().any():
        raise ValueError("Grid energy series cannot contain NaN values.")
    if (imports < 0).any() or (exports < 0).any():
        raise ValueError("Grid import/export energy must be non-negative.")

    buy = _price_series(import_price_eur_per_mwh, len(imports), "Import price")
    sell = _price_series(export_price_eur_per_mwh, len(imports), "Export price")
    import_cost = float(((imports / 1000.0) * buy).sum())
    export_revenue = float(((exports / 1000.0) * sell).sum())
    return {
        "energy_purchase_cost_eur": import_cost,
        "export_revenue_eur": export_revenue,
        "net_grid_energy_cost_eur": import_cost - export_revenue,
    }
