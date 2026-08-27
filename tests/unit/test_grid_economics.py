import pandas as pd
import pytest

from industrial_energy_lab.economics.grid import annual_grid_cashflow_eur


def test_grid_cashflow_import_cost_export_revenue_and_net() -> None:
    result = annual_grid_cashflow_eur(
        pd.Series([1000.0, 2000.0]),
        pd.Series([500.0, 0.0]),
        pd.Series([100.0, 50.0]),
        40.0,
    )
    assert result["energy_purchase_cost_eur"] == pytest.approx(200.0)
    assert result["export_revenue_eur"] == pytest.approx(20.0)
    assert result["net_grid_energy_cost_eur"] == pytest.approx(180.0)
