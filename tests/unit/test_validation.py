import pandas as pd
import pytest

from industrial_energy_lab.validation.datasets import validate_hourly_dataframe


def _small_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp_utc": pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC"),
            "value": [1.0, 2.0, 3.0],
        }
    )


def test_accepts_contiguous_hourly_series() -> None:
    out = validate_hourly_dataframe(_small_frame(), value_column="value", expected_hours=3)
    assert len(out) == 3


def test_rejects_negative_when_not_allowed() -> None:
    frame = _small_frame()
    frame.loc[1, "value"] = -1
    with pytest.raises(ValueError, match="negative"):
        validate_hourly_dataframe(frame, value_column="value", expected_hours=3)


def test_rejects_duplicate_timestamp() -> None:
    frame = _small_frame()
    frame.loc[2, "timestamp_utc"] = frame.loc[1, "timestamp_utc"]
    with pytest.raises(ValueError, match="Duplicate"):
        validate_hourly_dataframe(frame, value_column="value", expected_hours=3)
