"""Deterministic PV-first battery dispatch for Iteration 2."""

from __future__ import annotations

import math

import pandas as pd

from industrial_energy_lab.core.battery import BatterySpec, charge_from_ac, discharge_to_ac

RESULT_COLUMNS = [
    "timestamp_utc",
    "load_kwh",
    "pv_generation_kwh",
    "pv_to_load_kwh",
    "pv_to_battery_kwh",
    "pv_export_kwh",
    "battery_charge_kwh",
    "battery_discharge_kwh",
    "battery_losses_kwh",
    "soc_start_kwh",
    "soc_kwh",
    "grid_import_kwh",
    "grid_export_kwh",
]


def greedy_pv_battery_dispatch(
    timestamps: pd.Series,
    load_kwh: pd.Series,
    pv_generation_kwh: pd.Series,
    battery: BatterySpec,
    *,
    interval_hours: float = 1.0,
) -> pd.DataFrame:
    """Simulate transparent PV-first dispatch without price arbitrage.

    Priority in each interval:
    1. PV serves load directly.
    2. Surplus PV charges the battery within power/SOC constraints.
    3. Remaining PV is exported.
    4. During a deficit, the battery serves load within power/SOC constraints.
    5. The grid supplies any remaining deficit.

    The battery can only charge from PV and can only discharge to site load in this
    iteration. Therefore simultaneous import/export and charge/discharge cannot occur.
    """

    if interval_hours <= 0:
        raise ValueError("interval_hours must be positive.")
    if not (len(timestamps) == len(load_kwh) == len(pv_generation_kwh)):
        raise ValueError("Timestamps, load and PV series must have the same length.")
    if len(load_kwh) == 0:
        raise ValueError("Dispatch requires at least one interval.")

    ts = pd.Series(pd.to_datetime(timestamps, utc=True, errors="raise")).reset_index(drop=True)
    load = pd.to_numeric(load_kwh, errors="raise").astype(float).reset_index(drop=True)
    pv = pd.to_numeric(pv_generation_kwh, errors="raise").astype(float).reset_index(drop=True)
    if load.isna().any() or pv.isna().any():
        raise ValueError("Load and PV cannot contain NaN values.")
    if (load < 0).any() or (pv < 0).any():
        raise ValueError("Load and PV must be non-negative.")

    soc = battery.initial_soc_kwh
    rows: list[dict[str, float | pd.Timestamp]] = []

    for timestamp, demand, generation in zip(ts, load, pv, strict=True):
        soc_start = soc
        pv_to_load = min(demand, generation)
        surplus = generation - pv_to_load
        deficit = demand - pv_to_load

        charge = discharge = charge_loss = discharge_loss = 0.0
        pv_to_battery = pv_export = grid_import = 0.0

        if surplus > 0:
            charge, soc, charge_loss = charge_from_ac(
                soc,
                surplus,
                battery,
                interval_hours=interval_hours,
            )
            pv_to_battery = charge
            pv_export = surplus - charge
            grid_export = pv_export
        else:
            discharge, soc, discharge_loss = discharge_to_ac(
                soc,
                deficit,
                battery,
                interval_hours=interval_hours,
            )
            grid_import = deficit - discharge
            grid_export = 0.0

        battery_losses = charge_loss + discharge_loss

        # Numerical guardrails: fail fast rather than silently clipping real mistakes.
        load_residual = demand - (pv_to_load + discharge + grid_import)
        pv_residual = generation - (pv_to_load + pv_to_battery + pv_export)
        soc_residual = soc - (
            soc_start
            + charge * battery.charge_efficiency
            - discharge / battery.discharge_efficiency
        )
        if not math.isclose(load_residual, 0.0, abs_tol=1e-8):
            raise RuntimeError("Load balance failed during dispatch.")
        if not math.isclose(pv_residual, 0.0, abs_tol=1e-8):
            raise RuntimeError("PV balance failed during dispatch.")
        if not math.isclose(soc_residual, 0.0, abs_tol=1e-8):
            raise RuntimeError("Battery SOC conservation failed during dispatch.")
        if not battery.min_soc_kwh - 1e-8 <= soc <= battery.max_soc_kwh + 1e-8:
            raise RuntimeError("Battery SOC left allowed bounds during dispatch.")

        rows.append(
            {
                "timestamp_utc": timestamp,
                "load_kwh": float(demand),
                "pv_generation_kwh": float(generation),
                "pv_to_load_kwh": float(pv_to_load),
                "pv_to_battery_kwh": float(pv_to_battery),
                "pv_export_kwh": float(pv_export),
                "battery_charge_kwh": float(charge),
                "battery_discharge_kwh": float(discharge),
                "battery_losses_kwh": float(battery_losses),
                "soc_start_kwh": float(soc_start),
                "soc_kwh": float(soc),
                "grid_import_kwh": float(grid_import),
                "grid_export_kwh": float(grid_export),
            }
        )

    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def annual_dispatch_summary(dispatch: pd.DataFrame) -> dict[str, float]:
    """Aggregate physical annual metrics and two explicitly defined ratios."""

    required = set(RESULT_COLUMNS)
    missing = required.difference(dispatch.columns)
    if missing:
        raise ValueError(f"Missing dispatch columns: {sorted(missing)}")

    def mwh(column: str) -> float:
        return float(dispatch[column].sum() / 1000.0)

    load_mwh = mwh("load_kwh")
    pv_generation_mwh = mwh("pv_generation_kwh")
    grid_import_mwh = mwh("grid_import_kwh")
    grid_export_mwh = mwh("grid_export_kwh")
    pv_self_consumption_mwh = pv_generation_mwh - grid_export_mwh

    self_consumption_ratio = (
        0.0 if pv_generation_mwh == 0 else pv_self_consumption_mwh / pv_generation_mwh
    )
    self_sufficiency_ratio = 0.0 if load_mwh == 0 else (load_mwh - grid_import_mwh) / load_mwh

    return {
        "load_mwh": load_mwh,
        "pv_generation_mwh": pv_generation_mwh,
        "pv_self_consumption_mwh": float(pv_self_consumption_mwh),
        "pv_export_mwh": mwh("pv_export_kwh"),
        "battery_charge_mwh": mwh("battery_charge_kwh"),
        "battery_discharge_mwh": mwh("battery_discharge_kwh"),
        "battery_losses_mwh": mwh("battery_losses_kwh"),
        "grid_import_mwh": grid_import_mwh,
        "grid_export_mwh": grid_export_mwh,
        "self_consumption_ratio": float(self_consumption_ratio),
        "self_sufficiency_ratio": float(self_sufficiency_ratio),
        "initial_soc_mwh": float(dispatch["soc_start_kwh"].iloc[0] / 1000.0),
        "final_soc_mwh": float(dispatch["soc_kwh"].iloc[-1] / 1000.0),
        "net_stored_energy_change_mwh": float(
            (dispatch["soc_kwh"].iloc[-1] - dispatch["soc_start_kwh"].iloc[0]) / 1000.0
        ),
    }
