import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[2]


def test_demo_baseline_end_to_end() -> None:
    data = ROOT / "data" / "demo"
    load = pd.read_csv(data / "industrial_load_8760.csv")
    price = pd.read_csv(data / "electricity_prices_8760.csv")
    raw = json.loads((data / "baseline_assumptions.json").read_text(encoding="utf-8"))
    result = run_baseline(
        load,
        price,
        GridAssumptions(raw["grid_emissions_factor_kg_co2_per_mwh"]),
    )

    assert result.annual_consumption_mwh == pytest.approx(22_000.0, abs=0.01)
    assert result.annual_energy_cost_eur > 0
    assert result.annual_emissions_tco2 == pytest.approx(3960.0, abs=0.01)
