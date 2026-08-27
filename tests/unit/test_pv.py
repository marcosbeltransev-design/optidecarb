import pandas as pd
import pytest

from industrial_energy_lab.core.pv import annual_pv_generation_mwh, pv_generation_kwh


def test_pv_generation_scales_capacity_factor() -> None:
    cf = pd.Series([0.0, 0.25, 1.0])
    generation = pv_generation_kwh(1000.0, cf)
    assert generation.tolist() == pytest.approx([0.0, 250.0, 1000.0])
    assert annual_pv_generation_mwh(generation) == pytest.approx(1.25)


def test_pv_rejects_invalid_capacity_factor() -> None:
    with pytest.raises(ValueError):
        pv_generation_kwh(1000.0, pd.Series([0.0, 1.01]))
    with pytest.raises(ValueError):
        pv_generation_kwh(-1.0, pd.Series([0.5]))
