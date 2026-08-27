import pandas as pd
import pytest

from industrial_energy_lab.core.battery import BatterySpec
from industrial_energy_lab.core.dispatch import annual_dispatch_summary, greedy_pv_battery_dispatch


def _timestamps(n: int) -> pd.Series:
    return pd.Series(pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC"))


def test_manual_three_hour_dispatch_is_exact() -> None:
    # Manual case: charge 10 kWh from PV at 90% efficiency -> +9 kWh SOC,
    # then deliver 8.1 kWh at 90% discharge efficiency -> return to zero SOC.
    battery = BatterySpec(
        energy_capacity_kwh=20.0,
        power_capacity_kw=20.0,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
        min_soc_fraction=0.0,
        max_soc_fraction=1.0,
        initial_soc_fraction=0.0,
    )
    dispatch = greedy_pv_battery_dispatch(
        _timestamps(3),
        pd.Series([10.0, 10.0, 10.0]),
        pd.Series([0.0, 20.0, 0.0]),
        battery,
    )

    assert dispatch["pv_to_load_kwh"].tolist() == pytest.approx([0.0, 10.0, 0.0])
    assert dispatch["battery_charge_kwh"].tolist() == pytest.approx([0.0, 10.0, 0.0])
    assert dispatch["battery_discharge_kwh"].tolist() == pytest.approx([0.0, 0.0, 8.1])
    assert dispatch["grid_import_kwh"].tolist() == pytest.approx([10.0, 0.0, 1.9])
    assert dispatch["grid_export_kwh"].tolist() == pytest.approx([0.0, 0.0, 0.0])
    assert dispatch["soc_kwh"].tolist() == pytest.approx([0.0, 9.0, 0.0])
    assert dispatch["battery_losses_kwh"].sum() == pytest.approx(1.9)


def test_surplus_beyond_battery_limit_is_exported() -> None:
    battery = BatterySpec(
        energy_capacity_kwh=5.0,
        power_capacity_kw=2.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
        min_soc_fraction=0.0,
        max_soc_fraction=1.0,
        initial_soc_fraction=0.0,
    )
    dispatch = greedy_pv_battery_dispatch(
        _timestamps(1), pd.Series([1.0]), pd.Series([10.0]), battery
    )
    row = dispatch.iloc[0]
    assert row["battery_charge_kwh"] == pytest.approx(2.0)
    assert row["pv_export_kwh"] == pytest.approx(7.0)
    assert row["grid_export_kwh"] == pytest.approx(7.0)


def test_dispatch_invariants_and_ratios() -> None:
    battery = BatterySpec(
        energy_capacity_kwh=20.0,
        power_capacity_kw=10.0,
        charge_efficiency=0.95,
        discharge_efficiency=0.95,
        min_soc_fraction=0.0,
        max_soc_fraction=1.0,
        initial_soc_fraction=0.0,
    )
    dispatch = greedy_pv_battery_dispatch(
        _timestamps(6),
        pd.Series([10.0] * 6),
        pd.Series([0.0, 5.0, 20.0, 20.0, 5.0, 0.0]),
        battery,
    )

    load_residual = dispatch["load_kwh"] - (
        dispatch["pv_to_load_kwh"]
        + dispatch["battery_discharge_kwh"]
        + dispatch["grid_import_kwh"]
    )
    pv_residual = dispatch["pv_generation_kwh"] - (
        dispatch["pv_to_load_kwh"]
        + dispatch["pv_to_battery_kwh"]
        + dispatch["pv_export_kwh"]
    )
    assert load_residual.abs().max() < 1e-9
    assert pv_residual.abs().max() < 1e-9
    assert not ((dispatch["battery_charge_kwh"] > 0) & (dispatch["battery_discharge_kwh"] > 0)).any()
    assert not ((dispatch["grid_import_kwh"] > 0) & (dispatch["grid_export_kwh"] > 0)).any()

    summary = annual_dispatch_summary(dispatch)
    assert 0 <= summary["self_consumption_ratio"] <= 1
    assert 0 <= summary["self_sufficiency_ratio"] <= 1
