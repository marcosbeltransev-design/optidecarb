"""Load immutable case bundles for demo and sourced representative studies."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEMO_CASE_ID = "synthetic_demo"
CERAMIC_CASE_ID = "ceramic_castellon"
DEFAULT_CASE_ID = CERAMIC_CASE_ID
CASE_LABELS = {
    DEMO_CASE_ID: "Synthetic software demo",
    CERAMIC_CASE_ID: "Representative Ceramic Plant — Castellón",
}


@dataclass(frozen=True)
class CaseBundle:
    case_id: str
    label: str
    classification: str
    load: pd.DataFrame
    pv: pd.DataFrame
    prices: pd.DataFrame
    config: dict[str, Any]
    metadata: dict[str, Any]
    sources: tuple[dict[str, Any], ...]

    @property
    def dataset_version(self) -> str:
        return str(self.config.get("dataset_version", self.metadata.get("dataset_version", "unknown")))

    @property
    def case_version(self) -> str:
        return str(self.config.get("case_version", self.metadata.get("case_version", "unknown")))

    @property
    def disclaimer(self) -> str:
        return str(self.config.get("disclaimer", ""))


def available_cases() -> dict[str, str]:
    return dict(CASE_LABELS)


def _load_demo() -> CaseBundle:
    demo = ROOT / "data" / "demo"
    config = json.loads((demo / "optimization_assumptions.json").read_text(encoding="utf-8"))
    metadata = {
        "reference_year": 2025,
        "dataset_version": config["dataset_version"],
        "case_version": config["case_version"],
        "scope": "Synthetic software-validation case.",
    }
    return CaseBundle(
        case_id=DEMO_CASE_ID,
        label=CASE_LABELS[DEMO_CASE_ID],
        classification="SYNTHETIC SOFTWARE VALIDATION",
        load=pd.read_csv(demo / "industrial_load_8760.csv"),
        pv=pd.read_csv(demo / "pv_profile_8760.csv"),
        prices=pd.read_csv(demo / "electricity_prices_8760.csv"),
        config=config,
        metadata=metadata,
        sources=(),
    )


def _load_ceramic() -> CaseBundle:
    case = ROOT / "cases" / "ceramic_castellon"
    config = json.loads((case / "case_config.json").read_text(encoding="utf-8"))
    metadata = json.loads((case / "metadata" / "case_datasets.json").read_text(encoding="utf-8"))
    sources = tuple(json.loads((case / "sources.json").read_text(encoding="utf-8")))
    return CaseBundle(
        case_id=CERAMIC_CASE_ID,
        label=CASE_LABELS[CERAMIC_CASE_ID],
        classification=str(config["classification"]),
        load=pd.read_csv(case / "data" / "industrial_load_8760.csv"),
        pv=pd.read_csv(case / "data" / "pv_profile_8760.csv"),
        prices=pd.read_csv(case / "data" / "electricity_prices_8760.csv"),
        config=config,
        metadata=metadata,
        sources=sources,
    )


def load_case_bundle(case_id: str) -> CaseBundle:
    if case_id == DEMO_CASE_ID:
        return _load_demo()
    if case_id == CERAMIC_CASE_ID:
        return _load_ceramic()
    raise KeyError(f"Unknown case_id: {case_id}")


def source_index(bundle: CaseBundle) -> dict[str, dict[str, Any]]:
    return {str(row["source_id"]): row for row in bundle.sources}


def parameter_source_ids(bundle: CaseBundle, parameter_key: str) -> tuple[str, ...]:
    value = bundle.config.get(parameter_key)
    if parameter_key.endswith("_source_id") and isinstance(value, str):
        return (value,)
    if parameter_key.endswith("_source_ids") and isinstance(value, list):
        return tuple(str(x) for x in value)
    direct = bundle.config.get(f"{parameter_key}_source_id")
    if isinstance(direct, str):
        return (direct,)
    plural = bundle.config.get(f"{parameter_key}_source_ids")
    if isinstance(plural, list):
        return tuple(str(x) for x in plural)
    aliases = {
        "pv_capex_eur_per_kw": "pv_cost_source_ids",
        "pv_opex_eur_per_kw_year": "pv_cost_source_ids",
        "pv_lifetime_years": "pv_cost_source_ids",
        "battery_energy_capex_eur_per_kwh": "battery_cost_source_ids",
        "battery_power_capex_eur_per_kw": "battery_cost_source_ids",
        "battery_opex_eur_per_kwh_year": "battery_cost_source_ids",
        "battery_opex_eur_per_kw_year": "battery_cost_source_ids",
        "battery_lifetime_years": "battery_cost_source_ids",
        "wacc": "finance_source_id",
        "project_life_years": "finance_source_id",
        "grid_emissions_factor_kg_co2_per_mwh": "grid_emissions_source_id",
        "export_price_eur_per_mwh": "export_price_source_id",
    }
    key = aliases.get(parameter_key)
    if key:
        mapped = bundle.config.get(key)
        if isinstance(mapped, str):
            return (mapped,)
        if isinstance(mapped, list):
            return tuple(str(x) for x in mapped)
    return ()
