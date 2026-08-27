import json
from pathlib import Path

from industrial_energy_lab.case_studies.bundles import (
    CERAMIC_CASE_ID,
    DEFAULT_CASE_ID,
    DEMO_CASE_ID,
    available_cases,
    load_case_bundle,
    parameter_source_ids,
    source_index,
)

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "cases" / "ceramic_castellon"


def test_source_registry_is_complete_and_unique():
    rows = json.loads((CASE / "sources.json").read_text())
    required = {
        "source_id", "source_name", "document_title", "publisher", "publication_date",
        "access_date", "url", "page_table_section", "original_unit", "used_value",
        "transformation", "geography", "reference_year", "classification", "license",
    }
    ids = [row["source_id"] for row in rows]
    assert len(ids) == len(set(ids))
    for row in rows:
        assert required <= set(row)
        for key in required - {"url"}:
            assert row[key] not in (None, ""), (row["source_id"], key)
        if row["classification"] != "MODEL ASSUMPTION":
            assert row["url"], row["source_id"]


def test_all_critical_config_source_ids_resolve():
    cfg = json.loads((CASE / "case_config.json").read_text())
    source_ids = {row["source_id"] for row in json.loads((CASE / "sources.json").read_text())}
    critical = {
        "annual_load_source_ids", "grid_emissions_source_id", "pv_cost_source_ids",
        "battery_cost_source_ids", "finance_source_id", "export_price_source_id",
        "price_source_id", "pv_profile_source_ids",
    }
    for key in critical:
        value = cfg[key]
        refs = value if isinstance(value, list) else [value]
        assert refs
        assert set(refs) <= source_ids, key


def test_case_bundle_selector_and_parameter_provenance():
    cases = available_cases()
    assert DEFAULT_CASE_ID == CERAMIC_CASE_ID
    assert {DEMO_CASE_ID, CERAMIC_CASE_ID} <= set(cases)
    bundle = load_case_bundle(CERAMIC_CASE_ID)
    assert bundle.case_version == "ceramic-castellon-v1"
    assert bundle.dataset_version == "ceramic-castellon-2025-v1"
    assert "does not reproduce" in bundle.disclaimer
    idx = source_index(bundle)
    refs = parameter_source_ids(bundle, "pv_capex_eur_per_kw")
    assert refs
    assert all(ref in idx for ref in refs)
    assert parameter_source_ids(bundle, "wacc") == ("model_finance",)
