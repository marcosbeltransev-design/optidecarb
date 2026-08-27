"""Consistent UI labels, units and explainability text."""
from __future__ import annotations

from industrial_energy_lab.explainability.metrics import get_metric

ASSUMPTION_METRICS = {
    "import_price_multiplier", "export_price", "pv_capex_rate", "pv_opex_rate",
    "pv_lifetime", "battery_energy_capex_rate", "battery_power_capex_rate",
    "battery_charge_efficiency", "battery_discharge_efficiency", "soc_min_fraction",
    "soc_max_fraction", "max_pv_capacity", "max_battery_energy", "max_battery_power",
    "project_life", "battery_lifetime", "wacc", "grid_emission_factor", "carbon_target",
}


def metric_help(metric_id: str) -> str:
    """Render the central metric definition as compact Markdown help text."""
    metric = get_metric(metric_id)
    related = ", ".join(get_metric(i).label for i in metric.relationships) or "None"
    parts = [
        metric.short_description,
        f"**Unit:** {metric.unit}",
        f"**Why it matters:** {metric.why_it_matters}",
        f"**How it is calculated:** {metric.calculation}",
        f"**How to interpret it:** {metric.interpretation}",
        f"**Related:** {related}",
    ]
    if metric_id in ASSUMPTION_METRICS:
        parts.append("**Source:** Synthetic assumption for model validation until a sourced case replaces it.")
    if metric.caveats:
        parts.append(f"**Important limitation:** {metric.caveats}")
    return "\n\n".join(parts)


def format_power_kw(value: float | None) -> str:
    return "—" if value is None else f"{value / 1000:,.2f} MW"


def format_energy_kwh(value: float | None) -> str:
    return "—" if value is None else f"{value / 1000:,.2f} MWh"


def format_energy_mwh(value: float | None) -> str:
    return "—" if value is None else f"{value:,.0f} MWh"


def format_eur(value: float | None) -> str:
    if value is None:
        return "—"
    if abs(value) >= 1_000_000:
        return f"€{value / 1_000_000:,.2f} M"
    if abs(value) >= 1_000:
        return f"€{value / 1_000:,.0f}k"
    return f"€{value:,.0f}"


def format_eur_per_year(value: float | None) -> str:
    return "—" if value is None else f"{format_eur(value)}/year"


def format_percent(value: float | None, decimals: int = 1) -> str:
    return "—" if value is None else f"{100 * value:.{decimals}f}%"


def format_tco2(value: float | None) -> str:
    return "—" if value is None else f"{value:,.0f} tCO₂/year"


def format_years(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f} years"
