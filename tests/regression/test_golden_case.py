import json
from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[2]


def test_golden_case_v1() -> None:
    data = ROOT / "data" / "demo"
    expected = json.loads((ROOT / "tests" / "regression" / "golden_case_v1.json").read_text())
    assumptions = json.loads((data / "baseline_assumptions.json").read_text())
    result = run_baseline(
        pd.read_csv(data / "industrial_load_8760.csv"),
        pd.read_csv(data / "electricity_prices_8760.csv"),
        GridAssumptions(assumptions["grid_emissions_factor_kg_co2_per_mwh"]),
    )

    assert result.model_version == expected["model_version"]
    assert result.dataset_version == expected["dataset_version"]
    assert result.case_version == expected["case_version"]
    assert result.annual_consumption_mwh == pytest.approx(expected["annual_consumption_mwh"], abs=0.01)
    assert result.annual_energy_cost_eur == pytest.approx(expected["annual_energy_cost_eur"], abs=0.50)
    assert result.annual_emissions_tco2 == pytest.approx(expected["annual_emissions_tco2"], abs=0.01)
