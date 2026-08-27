import math

import pytest

from industrial_energy_lab.economics.cashflows import annualized_capex, capital_recovery_factor
from industrial_energy_lab.economics.npv import npv
from industrial_energy_lab.economics.payback import simple_payback_years


def test_npv_matches_manual_example() -> None:
    expected = -1000.0 + sum(300.0 / (1.10**year) for year in range(1, 5))
    assert npv(1000.0, [300.0] * 4, 0.10) == pytest.approx(expected, abs=1e-10)


def test_zero_rate_crf() -> None:
    assert capital_recovery_factor(0.0, 10) == pytest.approx(0.1)


def test_annualized_capex() -> None:
    crf = 0.08 * 1.08**20 / (1.08**20 - 1)
    assert annualized_capex(1_000_000, 0.08, 20) == pytest.approx(1_000_000 * crf)


def test_simple_payback() -> None:
    assert simple_payback_years(500_000, 100_000) == pytest.approx(5.0)
    assert simple_payback_years(500_000, 0.0) is None


def test_invalid_discount_rate_rejected() -> None:
    with pytest.raises(ValueError):
        npv(1000, [100], -1.0)


def test_npv_result_is_finite() -> None:
    assert math.isfinite(npv(5000, [1200] * 8, 0.07))
