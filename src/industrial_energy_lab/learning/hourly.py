"""Human-readable explanations of one dispatch hour."""
from __future__ import annotations

from typing import Mapping


def explain_dispatch_hour(row: Mapping[str, object], *, tolerance: float = 1e-6) -> list[str]:
    load = float(row["load_kwh"]); pv = float(row["pv_generation_kwh"])
    direct = float(row["pv_to_load_kwh"]); charge = float(row["battery_charge_kwh"])
    discharge = float(row["battery_discharge_kwh"]); grid = float(row["grid_import_kwh"])
    export = float(row["grid_export_kwh"]); start = float(row["soc_start_kwh"]); end = float(row["soc_kwh"])
    out = [f"Load is {load:.2f} kWh and PV generation is {pv:.2f} kWh in this one-hour interval."]
    if direct > tolerance:
        out.append(f"PV supplies {direct:.2f} kWh directly to the site load.")
    if charge > tolerance:
        out.append(f"PV surplus charges the battery with {charge:.2f} kWh AC-side energy.")
    if discharge > tolerance:
        out.append(f"The battery delivers {discharge:.2f} kWh to reduce the remaining load deficit.")
    if grid > tolerance:
        out.append(f"The grid supplies the remaining {grid:.2f} kWh demand.")
    if export > tolerance:
        out.append(f"After direct use and battery charging, {export:.2f} kWh is exported.")
    out.append(f"Battery SOC moves from {start:.2f} to {end:.2f} kWh.")
    return out


def energy_balance_residual_kwh(row: Mapping[str, object]) -> float:
    """PV + grid + SOC_start - load - export - losses - SOC_end."""
    return float(
        float(row["pv_generation_kwh"]) + float(row["grid_import_kwh"]) + float(row["soc_start_kwh"])
        - float(row["load_kwh"]) - float(row["grid_export_kwh"])
        - float(row["battery_losses_kwh"]) - float(row["soc_kwh"])
    )
