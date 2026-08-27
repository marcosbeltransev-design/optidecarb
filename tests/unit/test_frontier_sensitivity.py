import pandas as pd
import pytest

from industrial_energy_lab.optimization.sensitivity import battery_break_even_from_sensitivity


def test_battery_break_even_returns_first_tested_zero_after_positive_storage():
    frame = pd.DataFrame({
        "input_variable": ["battery_capex_multiplier"] * 4,
        "input_value": [0.70, 0.72, 0.74, 0.76],
        "battery_energy_capacity_kwh": [500.0, 200.0, 10.0, 0.0],
    })
    assert battery_break_even_from_sensitivity(frame) == pytest.approx(0.76)


def test_battery_break_even_is_none_without_transition():
    frame = pd.DataFrame({
        "input_variable": ["battery_capex_multiplier"] * 2,
        "input_value": [1.0, 1.2],
        "battery_energy_capacity_kwh": [0.0, 0.0],
    })
    assert battery_break_even_from_sensitivity(frame) is None
