# Industrial Energy Lab

**Industrial Decarbonization & Techno-Economic Screening**

Industrial Energy Lab is a Python-based pre-feasibility screening project for industrial electrical energy systems. The v1 scope is deliberately narrow: 8,760-hour demand, PV, battery storage, grid exchange, techno-economics, CO2 accounting, optimization, deterministic sensitivity analysis, and a reproducible representative ceramic-industry case for Castellón, Spain.

> **Status:** Iteration 2 — 8,760h + PV + Battery is complete locally. The engine now simulates a full annual PV+battery system with deterministic dispatch, explicit battery losses, grid import/export, scenario economics, emissions, physical invariants and frozen regression cases. Mathematical optimization, Streamlit and the Castellón case remain intentionally deferred.

## What problem does it solve?

The finished v1 will answer a pre-feasibility question:

> Given an industrial site's annual hourly electricity profile, what PV and battery configuration minimizes energy cost, and how does that solution change under explicit CO2-reduction targets?

Iteration 2 does **not** choose the optimal size. It validates the physical simulation that Iteration 3 will optimize.

## What it does **not** claim

This is not detailed engineering, FEED, a certified energy model, financial advice, an industrial control system, a universal energy-system simulator, or a digital twin. Demo data are synthetic and must not be interpreted as measurements from a real factory.

## Architecture

```text
external data sources (future adapters)
        |
        v
versioned offline datasets
        |
        v
8,760h energy engine
  |     |      |
 load   PV   battery
        |      |
        +-- dispatch --+--> grid import/export
                       |
                       +--> economics
                       +--> emissions
                       |
                       v
              optimization (Iteration 3)
                       |
                       v
              Streamlit UI (Iteration 4)
```

The calculation engine has no HTTP/API dependency. Runtime calculations operate on local, versioned datasets.

## Implemented features

### Iteration 1 — frozen baseline

- strict 8,760-hour UTC dataset validation;
- deterministic synthetic industrial load and hourly electricity-price profiles;
- exact grid-only baseline;
- annual electricity consumption, cost and grid-related CO2;
- NPV, simple payback and capital-recovery-factor helpers;
- golden regression case v1.

### Iteration 2 — physical PV + battery simulation

- PV generation from installed capacity and normalized hourly capacity factor;
- battery energy/power limits, charge/discharge efficiency and SOC bounds;
- deterministic PV-first dispatch with no price arbitrage;
- PV direct use, PV-to-battery, battery-to-load and PV export;
- grid import/export and explicit battery losses;
- hourly conservation checks and annual energy summary;
- self-consumption and self-sufficiency ratios;
- hourly import cost, export revenue and net grid-energy cost;
- annual operating savings versus the frozen grid-only baseline;
- grid-related scenario emissions with **no export CO2 credit**;
- golden regression case v2 and physical-invariant integration tests.

## Golden Case v2

The regression scenario is intentionally synthetic software-validation data:

- PV: 4,000 kW;
- battery: 4,000 kWh / 2,000 kW;
- charge/discharge efficiency: 95% / 95%;
- SOC window: 10% to 90%;
- initial SOC: 10%;
- export price: 45 EUR/MWh;
- grid emissions factor: 180 kgCO2/MWh.

These values are **ASSUMPTIONS**, not current Spanish market recommendations or plant data.

## Installation

Python 3.11+ is recommended.

```bash
git clone <repository-url>
cd industrial-energy-lab
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Reproduce the demo datasets

```bash
python scripts/generate_demo_data.py
```

The generator uses a fixed seed (`20260827`) and writes exactly 8,760 hourly rows per dataset.

## Run the models

```bash
python scripts/run_baseline.py
python scripts/run_scenario.py
```

## Run validation

```bash
python -m compileall -q src scripts tests
pytest
```

## Data and time policy

Engine input is normalized to a fixed UTC hourly series with exactly 8,760 rows. Leap-year and local-DST datasets must be normalized before entering the engine; duplicate, missing or non-hourly timestamps fail validation. Dataset metadata live in `data/metadata/`.

## Demo-data warning

All current numeric demo inputs are synthetic software-validation assumptions. The electricity-price series, normalized PV profile, `180 kgCO2/MWh` emissions factor and `45 EUR/MWh` export price are not presented as current Spanish data.

## Documentation

- `METHODOLOGY.md` — equations, units, sign conventions and validation rules.
- `ASSUMPTIONS.md` — explicit assumptions and limitations.
- `docs/ARCHITECTURE.md` — architecture decisions.
- `FUTURE_IDEAS.md` — deferred ideas outside the closed MVP.
- `CHANGELOG.md` — model and dataset changes.

## Roadmap

1. **Energy Engine** — complete and frozen.
2. **8,760h + PV + Battery** — complete and frozen after v0.2 validation.
3. **Optimization** — Pyomo/HiGHS sizing, CO2 constraints, frontier, sensitivity.
4. **Web** — restrained Streamlit interface and deployment.
5. **Castellón Ceramic Case** — sourced representative case study.

After Iteration 5, v1.0 is considered complete. Further thermal or hydrogen work requires an explicit product decision.

## License

MIT for project code and project-generated synthetic demo data. External datasets added later must retain their own source/license metadata.
