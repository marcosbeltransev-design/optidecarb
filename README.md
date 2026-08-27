# Industrial Energy Lab

**Industrial Decarbonization & Techno-Economic Screening**

Industrial Energy Lab is a Python-based pre-feasibility screening project for industrial energy systems. The long-term v1 scope is deliberately narrow: 8,760-hour electrical demand, PV, battery storage, grid exchange, techno-economics, CO2 accounting, optimization, deterministic sensitivity analysis, and a reproducible representative ceramic-industry case for Castellón, Spain.

> **Status:** Iteration 1 — Energy Engine. This repository currently implements and validates the grid-only annual baseline, financial primitives, emissions accounting, deterministic demo data, regression testing, and CI. PV, battery dispatch, optimization, Streamlit, and the Castellón case are intentionally not implemented yet.

## What problem does it solve?

The finished v1 will answer a pre-feasibility question:

> Given an industrial site's annual hourly electricity profile, what PV and battery configuration minimizes energy cost, and how does that solution change under explicit CO2-reduction targets?

Iteration 1 establishes the calculation and validation foundation before adding technologies.

## What it does **not** claim

This is not detailed engineering, FEED, a certified energy model, financial advice, a control system, a universal energy-system simulator, or a digital twin. Demo data are synthetic and must not be interpreted as measurements from a real factory.

## Architecture

```text
external data sources (future)
        |
        v
adapters / snapshots (future)
        |
        v
versioned offline datasets
        |
        v
energy engine
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

The core engine has no HTTP/API dependency. Runtime calculations operate on local, versioned datasets.

## Iteration 1 features

- strict 8,760-hour UTC dataset validation;
- deterministic synthetic industrial load profile;
- deterministic synthetic hourly electricity-price profile;
- synthetic normalized PV reference dataset reserved for Iteration 2;
- exact grid-only hourly energy balance;
- annual electricity consumption and commodity energy cost;
- grid-related CO2 calculation from an explicit emissions-factor assumption;
- NPV, simple payback and capital-recovery-factor helpers;
- dataset/model/case version identifiers;
- unit, integration and golden regression tests;
- GitHub Actions CI definition;
- methodology and assumptions documentation.

## Installation

Python 3.11+ is recommended.

```bash
git clone <repository-url>
cd industrial-energy-lab
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
```

## Reproduce the demo datasets

```bash
python scripts/generate_demo_data.py
```

The generator uses a fixed seed (`20260827`) and writes exactly 8,760 hourly rows per dataset.

## Run the baseline

```bash
python scripts/run_baseline.py
```

## Run validation

```bash
python -m compileall -q src scripts tests
pytest
```

## Data policy

Engine input is normalized to a fixed UTC hourly series. The MVP requires exactly 8,760 rows. Leap-year and local-DST datasets must be normalized before entering the engine; this prevents silent duplicate/missing-hour behavior. Metadata for every included dataset lives in `data/metadata/`.

## Demo-data warning

All Iteration 1 numeric demo assumptions are explicitly synthetic software-validation inputs. In particular, the electricity-price series and the `180 kgCO2/MWh` emissions factor are **not** presented as current Spanish market or grid values.

## Documentation

- `METHODOLOGY.md` — equations, units, sign conventions and validation rules.
- `ASSUMPTIONS.md` — every Iteration 1 assumption and limitation.
- `FUTURE_IDEAS.md` — explicitly deferred ideas; not part of the MVP.
- `CHANGELOG.md` — model/dataset changes.

## Roadmap

1. **Energy Engine** — baseline, economics, emissions, tests, reproducible data.
2. **8,760h + PV + Battery** — annual physical simulation and dispatch.
3. **Optimization** — Pyomo/HiGHS sizing, CO2 constraints, frontier, sensitivity.
4. **Web** — restrained Streamlit interface and deployment.
5. **Castellón Ceramic Case** — sourced representative case study.

After Iteration 5, v1.0 is considered complete. Further thermal or hydrogen work requires an explicit product decision.

## License

MIT for project code and project-generated synthetic demo data. External datasets added later must retain their own source/license metadata.
