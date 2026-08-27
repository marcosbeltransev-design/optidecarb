"""Validation helpers for fixed-step hourly datasets."""

from __future__ import annotations

import pandas as pd

EXPECTED_HOURS = 8760


def validate_hourly_dataframe(
    frame: pd.DataFrame,
    *,
    value_column: str,
    expected_hours: int = EXPECTED_HOURS,
    allow_negative: bool = False,
    min_value: float | None = None,
    max_value: float | None = None,
) -> pd.DataFrame:
    """Validate a normalized UTC hourly series and return a defensive copy.

    The MVP policy is deliberately strict: one timestamp per UTC hour and exactly
    8,760 rows. Leap years or local-time DST series must be normalized before they
    enter the engine.
    """

    required = {"timestamp_utc", value_column}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(frame) != expected_hours:
        raise ValueError(f"Expected {expected_hours} rows, got {len(frame)}.")

    out = frame.loc[:, ["timestamp_utc", value_column]].copy()
    out["timestamp_utc"] = pd.to_datetime(out["timestamp_utc"], utc=True, errors="raise")

    if out["timestamp_utc"].duplicated().any():
        raise ValueError("Duplicate timestamps are not allowed.")
    if out[value_column].isna().any():
        raise ValueError(f"{value_column} contains NaN values.")

    out[value_column] = pd.to_numeric(out[value_column], errors="raise").astype(float)
    numeric = out[value_column]
    if not allow_negative and (numeric < 0).any():
        raise ValueError(f"{value_column} contains negative values.")
    if min_value is not None and (numeric < min_value).any():
        raise ValueError(f"{value_column} contains values below {min_value}.")
    if max_value is not None and (numeric > max_value).any():
        raise ValueError(f"{value_column} contains values above {max_value}.")

    ordered = out.sort_values("timestamp_utc").reset_index(drop=True)
    deltas = ordered["timestamp_utc"].diff().dropna()
    if not (deltas == pd.Timedelta(hours=1)).all():
        raise ValueError("Timestamps must form an uninterrupted hourly UTC series.")

    return ordered
