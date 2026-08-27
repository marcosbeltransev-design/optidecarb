import pytest

from industrial_energy_lab.core.battery import BatterySpec, charge_from_ac, discharge_to_ac


def test_charge_and_discharge_apply_efficiencies_at_ac_bus() -> None:
    battery = BatterySpec(
        energy_capacity_kwh=100.0,
        power_capacity_kw=50.0,
        charge_efficiency=0.90,
        discharge_efficiency=0.80,
        min_soc_fraction=0.10,
        max_soc_fraction=0.90,
        initial_soc_fraction=0.10,
    )

    charge, soc_after_charge, charge_loss = charge_from_ac(10.0, 50.0, battery)
    assert charge == pytest.approx(50.0)
    assert soc_after_charge == pytest.approx(55.0)
    assert charge_loss == pytest.approx(5.0)

    discharge, soc_after_discharge, discharge_loss = discharge_to_ac(
        soc_after_charge, 20.0, battery
    )
    assert discharge == pytest.approx(20.0)
    assert soc_after_discharge == pytest.approx(30.0)
    assert discharge_loss == pytest.approx(5.0)


def test_charge_respects_soc_and_power_limits() -> None:
    battery = BatterySpec(
        energy_capacity_kwh=100.0,
        power_capacity_kw=10.0,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
        min_soc_fraction=0.0,
        max_soc_fraction=0.50,
        initial_soc_fraction=0.40,
    )
    charge, new_soc, _ = charge_from_ac(40.0, 100.0, battery)
    assert charge == pytest.approx(10.0)
    assert new_soc == pytest.approx(49.0)


def test_discharge_respects_min_soc_and_power_limits() -> None:
    battery = BatterySpec(
        energy_capacity_kwh=100.0,
        power_capacity_kw=10.0,
        charge_efficiency=0.90,
        discharge_efficiency=0.80,
        min_soc_fraction=0.20,
        max_soc_fraction=1.0,
        initial_soc_fraction=0.30,
    )
    discharge, new_soc, _ = discharge_to_ac(30.0, 100.0, battery)
    assert discharge == pytest.approx(8.0)
    assert new_soc == pytest.approx(20.0)


def test_disabled_battery_has_no_energy_flow() -> None:
    battery = BatterySpec.disabled()
    charge, soc, losses = charge_from_ac(0.0, 100.0, battery)
    assert (charge, soc, losses) == (0.0, 0.0, 0.0)
    discharge, soc, losses = discharge_to_ac(0.0, 100.0, battery)
    assert (discharge, soc, losses) == (0.0, 0.0, 0.0)


def test_zero_energy_with_nonzero_power_is_rejected() -> None:
    with pytest.raises(ValueError):
        BatterySpec(
            energy_capacity_kwh=0.0,
            power_capacity_kw=10.0,
            charge_efficiency=1.0,
            discharge_efficiency=1.0,
            min_soc_fraction=0.0,
            max_soc_fraction=0.0,
            initial_soc_fraction=0.0,
        )
