"""PVGIS refresh adapter contract (never imported by the offline core).

Iteration 5 ships a versioned, PVGIS-calibrated proxy because this sandbox cannot
retrieve the raw API payload. A future refresh can call the documented PVGIS API,
validate it, and replace only the snapshot while preserving the core interface.
"""
from urllib.parse import urlencode

PVGIS_BASE = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"


def build_seriescalc_url(*, lat=39.98567, lon=-0.04935, startyear=2023, endyear=2023) -> str:
    params = {
        "lat": lat, "lon": lon, "startyear": startyear, "endyear": endyear,
        "pvcalculation": 1, "peakpower": 1, "loss": 14,
        "optimalangles": 1, "raddatabase": "PVGIS-SARAH3", "outputformat": "json",
    }
    return f"{PVGIS_BASE}?{urlencode(params)}"
