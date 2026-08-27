"""Public-data-calibrated representative ceramic electrical case for Castellón.

This module deliberately generates *proxies*, not company data. Public sector and
market evidence calibrates annual/monthly magnitudes; deterministic assumptions
supply the missing intra-day industrial and market shapes. Runtime use is offline.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

REFERENCE_YEAR = 2025
CASE_VERSION = "ceramic-castellon-v1"
DATASET_VERSION = "ceramic-castellon-2025-v1"
FIXED_SEED = 20260827
TARGET_ANNUAL_LOAD_MWH = 15_000.0
GRID_EMISSIONS_FACTOR_KG_CO2_PER_MWH = 29.5e9 / 272_201_000.0  # REE 2025 derived

# OMIE official monthly arithmetic means, Spanish day-ahead market, 2025.
OMIE_MONTHLY_MEAN_EUR_PER_MWH = {
    1: 96.69, 2: 108.31, 3: 53.03, 4: 26.81, 5: 16.93, 6: 72.60,
    7: 70.01, 8: 68.45, 9: 61.04, 10: 75.78, 11: 58.65, 12: 77.91,
}

# PVGIS-v5.3-derived monthly production for a 5 kWp system in Castelló de la Plana,
# divided by 5 to obtain kWh/kWp. The hourly shape below is a deterministic proxy,
# scaled month-by-month to exactly reproduce these public monthly yields.
PVGIS_MONTHLY_KWH_PER_KWP = {
    1: 113.4, 2: 116.4, 3: 139.4, 4: 145.0, 5: 155.8, 6: 154.0,
    7: 160.2, 8: 154.6, 9: 137.0, 10: 127.2, 11: 108.2, 12: 105.6,
}


def timestamps_2025() -> pd.DatetimeIndex:
    return pd.date_range("2025-01-01T00:00:00Z", periods=8760, freq="h")


def generate_representative_load() -> pd.DataFrame:
    """Build a smooth industrial proxy and scale it to exactly 15 GWh/year.

    Shape assumptions are deliberately generic: high continuous base load, modest
    daytime production uplift, smaller weekend activity, mild seasonality and fixed-
    seed process variability. They are not claimed as measured ceramic-plant data.
    """
    ts = timestamps_2025()
    rng = np.random.default_rng(FIXED_SEED)
    hour = ts.hour.to_numpy()
    weekday = ts.dayofweek.to_numpy() < 5
    doy = ts.dayofyear.to_numpy()

    continuous_base = np.full(len(ts), 0.84)
    daytime = np.where((hour >= 6) & (hour < 22), 0.14, 0.05)
    weekend = np.where(weekday, 1.0, 0.92)
    seasonality = 1.0 + 0.025 * np.cos(2 * np.pi * (doy - 20) / 365.0)
    process_variation = np.clip(rng.normal(1.0, 0.025, len(ts)), 0.92, 1.08)
    raw = (continuous_base + daytime) * weekend * seasonality * process_variation

    target_kwh = TARGET_ANNUAL_LOAD_MWH * 1000.0
    load_kw = raw * (target_kwh / raw.sum())
    return pd.DataFrame({"timestamp_utc": ts, "load_kw": load_kw})


def _solar_proxy_shape(ts: pd.DatetimeIndex, latitude_deg: float = 39.98567) -> np.ndarray:
    """Simple daylight geometry used only to distribute public monthly PV yields hourly."""
    lat = np.radians(latitude_deg)
    doy = ts.dayofyear.to_numpy()
    hour = ts.hour.to_numpy() + 0.5
    decl = np.radians(23.44) * np.sin(2 * np.pi * (284 + doy) / 365.0)
    cos_omega0 = np.clip(-np.tan(lat) * np.tan(decl), -1.0, 1.0)
    omega0 = np.arccos(cos_omega0)
    day_length = 24.0 * omega0 / np.pi
    sunrise = 12.0 - day_length / 2.0
    sunset = 12.0 + day_length / 2.0
    phase = (hour - sunrise) / np.maximum(sunset - sunrise, 1e-9)
    shape = np.zeros(len(ts), dtype=float)
    daylight = (phase > 0) & (phase < 1)
    shape[daylight] = np.sin(np.pi * phase[daylight]) ** 1.55

    # Fixed-seed day-level cloud modulation avoids an unrealistically identical day.
    rng = np.random.default_rng(FIXED_SEED + 1)
    day_cloud = np.clip(rng.normal(1.0, 0.13, 365), 0.58, 1.16)
    shape *= day_cloud[doy - 1]
    return shape


def generate_pv_profile() -> pd.DataFrame:
    """Generate a normalized hourly PV profile calibrated to public PVGIS monthly yield."""
    ts = timestamps_2025()
    raw = _solar_proxy_shape(ts)
    cf = np.zeros(len(ts), dtype=float)
    months = ts.month.to_numpy()
    for month, target in PVGIS_MONTHLY_KWH_PER_KWP.items():
        mask = months == month
        total = float(raw[mask].sum())
        if total <= 0:
            raise RuntimeError(f"PV proxy has no daylight energy for month {month}.")
        cf[mask] = raw[mask] * (target / total)
    if float(cf.max()) > 1.0 + 1e-12:
        raise RuntimeError("Calibrated PV capacity factor exceeds 1; review proxy shape.")
    return pd.DataFrame({"timestamp_utc": ts, "capacity_factor": cf})


def generate_wholesale_price_proxy() -> pd.DataFrame:
    """Positive hourly wholesale-price proxy matching all OMIE 2025 monthly means.

    It is *not* the raw OMIE hourly series. The public official monthly means are
    preserved exactly; an explicit deterministic shape supplies intra-month timing.
    Negative-price events and quarter-hour detail are intentionally not reconstructed.
    """
    ts = timestamps_2025()
    rng = np.random.default_rng(FIXED_SEED + 2)
    hour = ts.hour.to_numpy()
    weekday = ts.dayofweek.to_numpy() < 5
    months = ts.month.to_numpy()

    evening = np.exp(-0.5 * ((hour - 20) / 2.3) ** 2)
    morning = 0.50 * np.exp(-0.5 * ((hour - 9) / 2.2) ** 2)
    solar_dip = 0.45 * np.exp(-0.5 * ((hour - 14) / 2.8) ** 2)
    weekday_factor = np.where(weekday, 1.03, 0.92)
    noise = np.clip(rng.normal(1.0, 0.055, len(ts)), 0.82, 1.18)
    raw_factor = np.clip((1.0 + 0.24 * evening + 0.10 * morning - 0.24 * solar_dip) * weekday_factor * noise, 0.35, None)

    prices = np.zeros(len(ts), dtype=float)
    for month, target in OMIE_MONTHLY_MEAN_EUR_PER_MWH.items():
        mask = months == month
        local = raw_factor[mask]
        prices[mask] = local * (target / local.mean())
    return pd.DataFrame({"timestamp_utc": ts, "price_eur_per_mwh": prices})


def profile_statistics(load: pd.DataFrame) -> dict[str, float]:
    s = load["load_kw"].astype(float)
    annual_mwh = float(s.sum() / 1000.0)
    avg_kw = float(s.mean())
    peak_kw = float(s.max())
    weekdays = pd.to_datetime(load["timestamp_utc"], utc=True).dt.dayofweek < 5
    return {
        "annual_energy_mwh": annual_mwh,
        "peak_demand_mw": peak_kw / 1000.0,
        "average_demand_mw": avg_kw / 1000.0,
        "load_factor": avg_kw / peak_kw,
        "p5_demand_mw": float(s.quantile(0.05) / 1000.0),
        "p50_demand_mw": float(s.quantile(0.50) / 1000.0),
        "p95_demand_mw": float(s.quantile(0.95) / 1000.0),
        "weekday_weekend_ratio": float(s[weekdays].mean() / s[~weekdays].mean()),
    }


def build_case(output_dir: Path) -> dict[str, object]:
    output_dir = Path(output_dir)
    data_dir = output_dir / "data"
    metadata_dir = output_dir / "metadata"
    data_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    load = generate_representative_load()
    pv = generate_pv_profile()
    prices = generate_wholesale_price_proxy()
    load.to_csv(data_dir / "industrial_load_8760.csv", index=False, float_format="%.9f")
    prices.to_csv(data_dir / "electricity_prices_8760.csv", index=False, float_format="%.9f")
    pv.to_csv(data_dir / "pv_profile_8760.csv", index=False, float_format="%.9f")

    stats = profile_statistics(load)
    metadata = {
        "dataset_version": DATASET_VERSION,
        "case_version": CASE_VERSION,
        "reference_year": REFERENCE_YEAR,
        "timezone": "UTC",
        "rows": 8760,
        "fixed_seed": FIXED_SEED,
        "load": {
            "classification": "DERIVED VALUE / REPRESENTATIVE SCALE ASSUMPTION",
            "target_annual_mwh": TARGET_ANNUAL_LOAD_MWH,
            "source_ids": ["ascer_2025_energy", "ascer_membership"],
            "transformation": "Rounded representative scale calibrated to sector electricity consumption divided by more than 100 manufacturers; hourly shape is an explicit deterministic model assumption.",
            "statistics": stats,
        },
        "price": {
            "classification": "PROXY calibrated to OFFICIAL DATA",
            "source_ids": ["omie_2025_market"],
            "transformation": "Deterministic positive hourly shape rescaled separately in each month to match OMIE 2025 official monthly arithmetic day-ahead means exactly; not raw OMIE hourly settlement data.",
        },
        "pv": {
            "classification": "PROXY calibrated to PVGIS-derived public data",
            "source_ids": ["pvgis_official", "pvgis_castello_proxy"],
            "transformation": "Deterministic solar/day-cloud shape rescaled monthly to public PVGIS-v5.3-derived Castelló yield totals; not raw PVGIS hourly series.",
            "annual_specific_yield_kwh_per_kwp": float(pv["capacity_factor"].sum()),
        },
    }
    (metadata_dir / "case_datasets.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata
