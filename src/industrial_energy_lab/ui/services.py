"""UI service layer: load validated case inputs and call the existing engine."""
from __future__ import annotations

from typing import Any

import pandas as pd

from industrial_energy_lab.case_studies.bundles import (
    CaseBundle,
    DEMO_CASE_ID,
    load_case_bundle,
    parameter_source_ids,
    source_index,
)
from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.frontier import DEFAULT_CARBON_TARGETS, cost_decarbonization_frontier
from industrial_energy_lab.optimization.sensitivity import DEFAULT_MULTIPLIERS, run_sensitivity_family
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe

ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]


def load_demo_bundle() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Backward-compatible Iteration 1–4 demo loader."""
    bundle = load_case_bundle(DEMO_CASE_ID)
    return bundle.load, bundle.pv, bundle.prices, bundle.config


def default_parameters(case_id: str = DEMO_CASE_ID) -> dict[str, Any]:
    config = load_case_bundle(case_id).config
    params = dict(config)
    params.update(import_price_multiplier=1.0, carbon_target=0.0)
    return params


def validate_custom_load(frame: pd.DataFrame, case_id: str = DEMO_CASE_ID) -> pd.DataFrame:
    """Validate upload and require the active case UTC timeline for PV/price alignment."""
    validated = validate_hourly_dataframe(frame, value_column="load_kw")
    bundle = load_case_bundle(case_id)
    reference = validate_hourly_dataframe(bundle.load, value_column="load_kw")
    if not validated["timestamp_utc"].equals(reference["timestamp_utc"]):
        raise ValueError(
            "Uploaded timestamps must exactly match the active case 8,760-hour UTC timeline "
            "because PV and price snapshots use that timeline."
        )
    return validated


def _frames(params: dict[str, Any], load_frame: pd.DataFrame | None, case_id: str):
    bundle = load_case_bundle(case_id)
    load = bundle.load if load_frame is None else validate_custom_load(load_frame, case_id)
    prices = bundle.prices.copy()
    prices["price_eur_per_mwh"] *= float(params["import_price_multiplier"])
    return load, bundle.pv, prices


def _grid(params: dict[str, Any]) -> GridAssumptions:
    return GridAssumptions(float(params["grid_emissions_factor_kg_co2_per_mwh"]))


def _assumptions(params: dict[str, Any]):
    return optimization_assumptions_from_mapping(params)


def run_baseline_request(params: dict[str, Any], load_frame: pd.DataFrame | None = None, *, case_id: str = DEMO_CASE_ID):
    load, _, prices = _frames(params, load_frame, case_id)
    return run_baseline(load, prices, _grid(params)), load, prices


def run_optimization_request(
    params: dict[str, Any],
    load_frame: pd.DataFrame | None = None,
    *,
    carbon_target: float | None = None,
    case_id: str = DEMO_CASE_ID,
):
    load, pv, prices = _frames(params, load_frame, case_id)
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
    case_id: str = DEMO_CASE_ID,
):
    load, pv, prices = _frames(params, load_frame, case_id)
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
    *,
    case_id: str = DEMO_CASE_ID,
):
    load, pv, prices = _frames(params, load_frame, case_id)
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


def parameter_provenance_help(case_id: str, parameter_key: str) -> str:
    """Return concise source/proxy context for case-specific UI input help."""
    bundle = load_case_bundle(case_id)
    if not bundle.sources:
        return "**Source:** Synthetic assumption for software validation."
    ids = parameter_source_ids(bundle, parameter_key)
    if not ids:
        return "**Source:** Explicit case/model assumption; see Data & assumptions."
    idx = source_index(bundle)
    lines = []
    for sid in ids:
        src = idx.get(sid)
        if src:
            lines.append(f"- **{src['classification']} — {src['source_name']}:** {src['used_value']}")
    return "**Source / why this value:**\n" + "\n".join(lines) if lines else ""
