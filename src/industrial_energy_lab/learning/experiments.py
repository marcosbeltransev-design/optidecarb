"""Deterministic helpers for prediction and scenario-comparison learning."""
from __future__ import annotations
from dataclasses import replace
from typing import Mapping

from industrial_energy_lab.learning.catalog import GUIDED_EXPERIMENTS
from industrial_energy_lab.learning.models import PredictionComparison
from industrial_energy_lab.optimization.model import OptimizationResult


def experiment_by_id(experiment_id: str):
    for item in GUIDED_EXPERIMENTS:
        if item.experiment_id == experiment_id:
            return item
    raise KeyError(f"Unknown experiment_id: {experiment_id}")


def modified_parameters(parameters: Mapping[str, object], experiment_id: str) -> dict[str, object]:
    """Return a copy with exactly the intended experiment change applied."""
    p = dict(parameters)
    exp = experiment_by_id(experiment_id)
    if experiment_id == "electricity_price_up":
        p["import_price_multiplier"] = float(p.get("import_price_multiplier", 1.0)) * 1.20
    elif experiment_id == "pv_capex_up":
        p["pv_capex_eur_per_kw"] = float(p["pv_capex_eur_per_kw"]) * 1.20
    elif experiment_id == "wacc_up":
        p["wacc"] = 0.06
    elif experiment_id == "carbon_20_to_40":
        p["carbon_target"] = 0.40
    elif experiment_id == "battery_capex_down":
        p["battery_energy_capex_eur_per_kwh"] = float(p["battery_energy_capex_eur_per_kwh"]) * 0.80
        p["battery_power_capex_eur_per_kw"] = float(p["battery_power_capex_eur_per_kw"]) * 0.80
    elif experiment_id == "pv_oversizing":
        p["fixed_pv_multiplier"] = 1.50
    else:  # pragma: no cover - catalog and function are tested together
        raise KeyError(exp.experiment_id)
    return p


def direction(before: float, after: float, *, rel_tol: float = 1e-4) -> str:
    scale = max(abs(before), abs(after), 1.0)
    if abs(after - before) <= scale * rel_tol:
        return "Stay similar"
    return "Increase" if after > before else "Decrease"


def compare_prediction(metric: str, prediction: str, before: float, after: float, unit: str, explanation: str) -> PredictionComparison:
    observed = direction(before, after)
    normalized = prediction.strip().lower()
    accepted = {
        "increase": "increase", "more investment": "increase", "more likely": "increase",
        "decrease": "decrease", "less investment": "decrease", "less likely": "decrease",
        "stay similar": "stay similar", "similar": "stay similar", "same": "stay similar",
    }
    expected = accepted.get(normalized, normalized)
    correct = expected == observed.lower()
    return PredictionComparison(metric, prediction, observed, correct, float(before), float(after), unit, explanation)


def result_comparison(before: OptimizationResult, after: OptimizationResult) -> list[dict[str, float | str | None]]:
    if before.status != "optimal" or after.status != "optimal":
        raise ValueError("Scenario comparison requires two optimal results.")
    fields = (
        ("PV capacity", "pv_capacity_kw", "kW"),
        ("Battery energy", "battery_energy_capacity_kwh", "kWh"),
        ("Battery power", "battery_power_capacity_kw", "kW"),
        ("Grid import", "grid_import_mwh", "MWh/year"),
        ("Annualized cost", "objective_annualized_cost_eur", "€/year"),
        ("NPV", "project_npv_eur", "€"),
        ("CO₂ reduction", "emissions_reduction_fraction", "fraction"),
    )
    rows = []
    for label, attr, unit in fields:
        b = getattr(before, attr); a = getattr(after, attr)
        if b is None or a is None:
            continue
        b = float(b); a = float(a); delta = a - b
        pct = None if abs(b) < 1e-12 else delta / abs(b)
        rows.append({"metric": label, "before": b, "after": a, "delta": delta, "percent_change": pct, "unit": unit})
    return rows
