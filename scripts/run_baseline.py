"""Run the deterministic Iteration 1 baseline from repository demo data."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.schemas.models import GridAssumptions

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data" / "demo"
    load = pd.read_csv(data / "industrial_load_8760.csv")
    price = pd.read_csv(data / "electricity_prices_8760.csv")
    assumptions = json.loads((data / "baseline_assumptions.json").read_text(encoding="utf-8"))

    result = run_baseline(
        load,
        price,
        GridAssumptions(
            emissions_factor_kg_co2_per_mwh=assumptions[
                "grid_emissions_factor_kg_co2_per_mwh"
            ]
        ),
    )
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
