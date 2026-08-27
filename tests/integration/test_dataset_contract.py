import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_demo_datasets_have_8760_unique_hourly_utc_rows() -> None:
    specs = {
        "industrial_load_8760.csv": "load_kw",
        "electricity_prices_8760.csv": "price_eur_per_mwh",
        "pv_profile_8760.csv": "capacity_factor",
    }
    for filename, value_column in specs.items():
        frame = pd.read_csv(ROOT / "data" / "demo" / filename)
        timestamps = pd.to_datetime(frame["timestamp_utc"], utc=True)
        assert len(frame) == 8760
        assert timestamps.is_unique
        assert (timestamps.diff().dropna() == pd.Timedelta(hours=1)).all()
        assert frame[value_column].notna().all()


def test_pv_reference_profile_is_normalized() -> None:
    pv = pd.read_csv(ROOT / "data" / "demo" / "pv_profile_8760.csv")
    assert pv["capacity_factor"].between(0.0, 1.0).all()


def test_every_demo_csv_has_metadata() -> None:
    for csv_path in (ROOT / "data" / "demo").glob("*.csv"):
        metadata_path = ROOT / "data" / "metadata" / f"{csv_path.stem}.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["rows"] == 8760
        assert metadata["dataset_version"] == "demo-v1"
        assert metadata["source"]
        assert metadata["units"]
