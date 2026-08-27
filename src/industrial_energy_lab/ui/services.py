"""UI service layer: load validated inputs and call the existing engine."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.frontier import DEFAULT_CARBON_TARGETS, cost_decarbonization_frontier
from industrial_energy_lab.optimization.sensitivity import DEFAULT_MULTIPLIERS, run_sensitivity_family
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "data" / "demo"


def load_demo_bundle() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    load = pd.read_csv(DEMO / "industrial_load_8760.csv")
    pv = pd.read_csv(DEMO / "pv_profile_8760.csv")
    prices = pd.read_csv(DEMO / "electricity_prices_8760.csv")
    config = json.loads((DEMO / "optimization_assumptions.json").read_text(encoding="utf-8"))
    return load, pv, prices, config


def default_parameters() -> dict[str, Any]:
    _, _, _, config = load_demo_bundle()
    params = dict(config)
    params.update(import_price_multiplier=1.0, carbon_target=0.0)
    return params


def validate_custom_load(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate upload and require the demo UTC timeline so price/PV alignment is explicit."""
    validated = validate_hourly_dataframe(frame, value_column="load_kw")
    demo, _, _, _ = load_demo_bundle()
    demo_validated = validate_hourly_dataframe(demo, value_column="load_kw")
    if not validated["timestamp_utc"].equals(demo_validated["timestamp_utc"]):
        raise ValueError(
            "Uploaded timestamps must exactly match the 8,760-hour demo UTC timeline "
            "because the current PV and price snapshots use that timeline."
        )
    return validated


def _frames(params: dict[str, Any], load_frame: pd.DataFrame | None):
    demo_load, pv, prices, _ = load_demo_bundle()
    load = demo_load if load_frame is None else validate_custom_load(load_frame)
    prices = prices.copy()
    prices["price_eur_per_mwh"] *= float(params["import_price_multiplier"])
    return load, pv, prices


def _grid(params: dict[str, Any]) -> GridAssumptions:
    return GridAssumptions(float(params["grid_emissions_factor_kg_co2_per_mwh"]))


def _assumptions(params: dict[str, Any]):
    return optimization_assumptions_from_mapping(params)


def run_baseline_request(params: dict[str, Any], load_frame: pd.DataFrame | None = None):
    load, _, prices = _frames(params, load_frame)
    return run_baseline(load, prices, _grid(params)), load, prices


def run_optimization_request(
    params: dict[str, Any],
    load_frame: pd.DataFrame | None = None,
    *,
    carbon_target: float | None = None,
):
    load, pv, prices = _frames(params, load_frame)
    target = float(params.get("carbon_target", 0.0) if carbon_target is None else carbon_target)
    return optimize_annual_system(
        load, pv, prices, _grid(params), _assumptions(params),
        export_price_eur_per_mwh=float(params["export_price_eur_per_mwh"]),
        carbon_target=target,
    )


def run_frontier_request(
    params: dict[str, Any],
    load_frame: pd.DataFrame | None = None,
    *,
    targets=DEFAULT_CARBON_TARGETS,
    economic_optimum=None,
):
    load, pv, prices = _frames(params, load_frame)
    return cost_decarbonization_frontier(
        load, pv, prices, _grid(params), _assumptions(params),
        export_price_eur_per_mwh=float(params["export_price_eur_per_mwh"]),
        carbon_targets=targets,
        economic_optimum=economic_optimum,
    )


def run_sensitivity_request(
    params: dict[str, Any],
    variable: str,
    load_frame: pd.DataFrame | None = None,
):
    load, pv, prices = _frames(params, load_frame)
    kwargs: dict[str, Any] = {}
    if variable == "wacc":
        base = float(params["wacc"])
        kwargs["wacc_values"] = tuple(base * m for m in DEFAULT_MULTIPLIERS)
    elif variable == "carbon_target":
        kwargs["carbon_targets"] = DEFAULT_CARBON_TARGETS
    return run_sensitivity_family(
        load, pv, prices, _grid(params), _assumptions(params),
        variable=variable,
        export_price_eur_per_mwh=float(params["export_price_eur_per_mwh"]),
        **kwargs,
    )
