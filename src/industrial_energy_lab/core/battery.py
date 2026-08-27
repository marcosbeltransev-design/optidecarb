"""Physical battery state helpers for deterministic simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BatterySpec:
    """Battery parameters using an AC-bus energy convention.

    ``charge_efficiency`` converts AC charging energy into stored energy.
    ``discharge_efficiency`` converts stored-energy withdrawal into AC energy
    delivered to the site load. State of charge is stored internally in kWh.
    """

    energy_capacity_kwh: float
    power_capacity_kw: float
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    min_soc_fraction: float = 0.10
    max_soc_fraction: float = 0.90
    initial_soc_fraction: float = 0.10

    def __post_init__(self) -> None:
        if self.energy_capacity_kwh < 0 or self.power_capacity_kw < 0:
            raise ValueError("Battery energy and power capacities must be non-negative.")
        if not 0 < self.charge_efficiency <= 1:
            raise ValueError("charge_efficiency must be within (0, 1].")
        if not 0 < self.discharge_efficiency <= 1:
            raise ValueError("discharge_efficiency must be within (0, 1].")
        if not 0 <= self.min_soc_fraction <= self.max_soc_fraction <= 1:
            raise ValueError("SOC fractions must satisfy 0 <= min <= max <= 1.")
        if not self.min_soc_fraction <= self.initial_soc_fraction <= self.max_soc_fraction:
            raise ValueError("initial_soc_fraction must be within SOC bounds.")
        if self.energy_capacity_kwh == 0 and self.power_capacity_kw != 0:
            raise ValueError("A zero-energy battery must also have zero power capacity.")
        if self.energy_capacity_kwh == 0 and self.initial_soc_fraction != 0:
            # Fraction is immaterial for a zero-size battery; require a canonical value
            # to avoid implying stored energy where none exists.
            raise ValueError("A zero-energy battery must use initial_soc_fraction=0.")
        if self.energy_capacity_kwh == 0 and (
            self.min_soc_fraction != 0 or self.max_soc_fraction != 0
        ):
            raise ValueError("A zero-energy battery must use zero SOC fractions.")

    @property
    def min_soc_kwh(self) -> float:
        return self.energy_capacity_kwh * self.min_soc_fraction

    @property
    def max_soc_kwh(self) -> float:
        return self.energy_capacity_kwh * self.max_soc_fraction

    @property
    def initial_soc_kwh(self) -> float:
        return self.energy_capacity_kwh * self.initial_soc_fraction

    @classmethod
    def disabled(cls) -> "BatterySpec":
        """Return a canonical zero-size battery."""

        return cls(
            energy_capacity_kwh=0.0,
            power_capacity_kw=0.0,
            charge_efficiency=1.0,
            discharge_efficiency=1.0,
            min_soc_fraction=0.0,
            max_soc_fraction=0.0,
            initial_soc_fraction=0.0,
        )


def charge_from_ac(
    soc_kwh: float,
    available_ac_kwh: float,
    spec: BatterySpec,
    *,
    interval_hours: float = 1.0,
) -> tuple[float, float, float]:
    """Charge from AC energy and return (AC input, new SOC, losses), all in kWh."""

    if available_ac_kwh < 0:
        raise ValueError("Available charging energy must be non-negative.")
    if interval_hours <= 0:
        raise ValueError("interval_hours must be positive.")
    if not spec.min_soc_kwh - 1e-9 <= soc_kwh <= spec.max_soc_kwh + 1e-9:
        raise ValueError("SOC is outside battery bounds.")
    if spec.energy_capacity_kwh == 0 or spec.power_capacity_kw == 0:
        return 0.0, float(soc_kwh), 0.0

    power_limit_kwh = spec.power_capacity_kw * interval_hours
    headroom_stored_kwh = max(0.0, spec.max_soc_kwh - soc_kwh)
    headroom_ac_kwh = headroom_stored_kwh / spec.charge_efficiency
    charge_ac_kwh = min(available_ac_kwh, power_limit_kwh, headroom_ac_kwh)
    stored_increment_kwh = charge_ac_kwh * spec.charge_efficiency
    new_soc_kwh = soc_kwh + stored_increment_kwh
    losses_kwh = charge_ac_kwh - stored_increment_kwh
    return float(charge_ac_kwh), float(new_soc_kwh), float(losses_kwh)


def discharge_to_ac(
    soc_kwh: float,
    demand_ac_kwh: float,
    spec: BatterySpec,
    *,
    interval_hours: float = 1.0,
) -> tuple[float, float, float]:
    """Discharge to the AC bus and return (AC output, new SOC, losses), in kWh."""

    if demand_ac_kwh < 0:
        raise ValueError("Requested discharge energy must be non-negative.")
    if interval_hours <= 0:
        raise ValueError("interval_hours must be positive.")
    if not spec.min_soc_kwh - 1e-9 <= soc_kwh <= spec.max_soc_kwh + 1e-9:
        raise ValueError("SOC is outside battery bounds.")
    if spec.energy_capacity_kwh == 0 or spec.power_capacity_kw == 0:
        return 0.0, float(soc_kwh), 0.0

    power_limit_kwh = spec.power_capacity_kw * interval_hours
    withdrawable_stored_kwh = max(0.0, soc_kwh - spec.min_soc_kwh)
    deliverable_ac_kwh = withdrawable_stored_kwh * spec.discharge_efficiency
    discharge_ac_kwh = min(demand_ac_kwh, power_limit_kwh, deliverable_ac_kwh)
    stored_withdrawal_kwh = discharge_ac_kwh / spec.discharge_efficiency
    new_soc_kwh = soc_kwh - stored_withdrawal_kwh
    losses_kwh = stored_withdrawal_kwh - discharge_ac_kwh
    return float(discharge_ac_kwh), float(new_soc_kwh), float(losses_kwh)
