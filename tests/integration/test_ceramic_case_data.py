import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.case_studies.ceramic_castellon import (
    CASE_VERSION,
    DATASET_VERSION,
    OMIE_MONTHLY_MEAN_EUR_PER_MWH,
    PVGIS_MONTHLY_KWH_PER_KWP,
    TARGET_ANNUAL_LOAD_MWH,
    build_case,
)
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "cases" / "ceramic_castellon"


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(CASE / "data" / name)


def test_ceramic_case_hourly_contract_and_calibration():
    load = validate_hourly_dataframe(_read("industrial_load_8760.csv"), value_column="load_kw")
    prices = validate_hourly_dataframe(_read("electricity_prices_8760.csv"), value_column="price_eur_per_mwh", allow_negative=True)
    pv = validate_hourly_dataframe(_read("pv_profile_8760.csv"), value_column="capacity_factor", min_value=0, max_value=1)

    assert len(load) == len(prices) == len(pv) == 8760
    assert load["timestamp_utc"].equals(prices["timestamp_utc"])
    assert load["timestamp_utc"].equals(pv["timestamp_utc"])
    assert load["load_kw"].sum() / 1000 == pytest.approx(TARGET_ANNUAL_LOAD_MWH, abs=2e-6)

    months = load["timestamp_utc"].dt.month
    for month, target in OMIE_MONTHLY_MEAN_EUR_PER_MWH.items():
        actual = prices.loc[months == month, "price_eur_per_mwh"].mean()
        assert actual == pytest.approx(target, abs=2e-9)
    for month, target in PVGIS_MONTHLY_KWH_PER_KWP.items():
        actual = pv.loc[months == month, "capacity_factor"].sum()
        assert actual == pytest.approx(target, abs=2e-6)


def test_ceramic_case_metadata_versions_and_profile_stats():
    meta = json.loads((CASE / "metadata" / "case_datasets.json").read_text())
    assert meta["dataset_version"] == DATASET_VERSION
    assert meta["case_version"] == CASE_VERSION
    assert meta["rows"] == 8760
    assert meta["timezone"] == "UTC"
    assert meta["load"]["statistics"]["annual_energy_mwh"] == pytest.approx(15_000.0)
    assert 0 < meta["load"]["statistics"]["load_factor"] <= 1
    assert meta["pv"]["annual_specific_yield_kwh_per_kwp"] == pytest.approx(1616.8, abs=1e-7)


def test_ceramic_case_build_is_byte_reproducible(tmp_path):
    build_case(tmp_path)
    for rel in (
        "data/industrial_load_8760.csv",
        "data/electricity_prices_8760.csv",
        "data/pv_profile_8760.csv",
        "metadata/case_datasets.json",
    ):
        assert (tmp_path / rel).read_bytes() == (CASE / rel).read_bytes(), rel
