import pandas as pd
import pytest

from industrial_energy_lab.core.energy_balance import grid_only_balance


def test_grid_only_conserves_energy_hour_by_hour() -> None:
    load = pd.Series([100.0, 250.0, 75.0])
    result = grid_only_balance(load)
    assert (result["grid_import_kwh"] == result["load_kwh"]).all()
    assert result["grid_export_kwh"].sum() == pytest.approx(0.0)


def test_negative_load_is_rejected() -> None:
    with pytest.raises(ValueError):
        grid_only_balance(pd.Series([1.0, -1.0]))
