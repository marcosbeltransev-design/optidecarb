# Industrial Energy Lab

**Industrial Decarbonization & Techno-Economic Screening**

Industrial Energy Lab (IEL) is an offline-first Python **pre-feasibility** tool for industrial **electrical** decarbonization. It combines validated 8,760-hour energy balances, photovoltaic (PV) generation, battery storage, grid exchange, transparent economics, linear programming (LP), carbon constraints, deterministic sensitivity analysis, explainability, and a public-data-calibrated representative ceramic-industry case for Castellón, Spain.

> **v1.0 scope:** electricity + PV + battery + grid. Thermal process energy, kilns, dryers and natural-gas consumption are outside the model boundary.

> **Case disclaimer:** The Castellón representative case is constructed from public sector data and explicit modelling assumptions. It does not reproduce the operations, costs or energy consumption of any individual ceramic company.

## What problem does it solve?

> Given an industrial hourly electricity demand profile, what PV and battery configuration minimizes equivalent annual energy-system cost, and how does that solution change under explicit CO₂-reduction targets?

IEL jointly chooses:

- PV capacity [kW/MW];
- battery energy capacity [kWh/MWh];
- battery power capacity [kW/MW];
- hourly PV allocation;
- hourly battery charge/discharge;
- hourly state of charge (SOC).

Grid imports and PV exports are calculated consistently from hourly residual balances. The optimizer minimizes **total annualized cost**. Net present value (NPV) and simple payback are calculated afterwards as complementary screening indicators.

## New to energy optimization?

Start here:

- [`docs/BEGINNER_GUIDE.md`](docs/BEGINNER_GUIDE.md) — power vs energy, PV, batteries, economics, optimization and carbon from zero;
- [`docs/OPTIMIZATION_GUIDE.md`](docs/OPTIMIZATION_GUIDE.md) — the LP formulation in engineering language;
- [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) — short/deeper answers to common technical interview questions;
- [`cases/ceramic_castellon/CASE_STUDY.md`](cases/ceramic_castellon/CASE_STUDY.md) — the complete representative Castellón case.

The Streamlit interface also exposes a **Learning mode** plus contextual `?` help for important inputs/results. Definitions come from one central explainability registry, not duplicated page text.

## How IEL works

```text
PUBLIC DATA + EXPLICIT ASSUMPTIONS
                |
                v
           VALIDATION
                |
                v
      REPRESENTATIVE 8,760h CASE
                |
                v
             BASELINE
                |
                v
        PV + BATTERY PHYSICS
                |
                v
          LP OPTIMIZATION
          /      |       \
     ECONOMICS  CARBON  SENSITIVITY
          \      |       /
                v
          INTERPRETATION
```

The core and optimizer do not call HTTP/APIs. External research is converted into traceable offline case snapshots before runtime.

## Why 8,760 hours?

A non-leap year has `24 × 365 = 8,760` hours. Hourly modeling preserves:

- load/PV coincidence;
- battery state of charge;
- charge/discharge timing;
- hourly electricity-price exposure;
- PV export versus onsite use.

The UI may display one week, but the optimizer still solves the complete validated annual timeline.

## Key terminology

- **MW** = power (rate); **MWh** = energy (quantity). `1 MW × 1 h = 1 MWh`.
- **CAPEX — Capital Expenditure** = upfront investment.
- **OPEX — Operating Expenditure** = recurring operating expenditure.
- **WACC — Weighted Average Cost of Capital** = financing/discount rate used for annualization and NPV.
- **CRF — Capital Recovery Factor** = factor converting upfront CAPEX into equivalent annual cost.
- **SOC — State of Charge** = energy currently stored in the battery.
- **LP — Linear Programming** = method used to minimize annualized cost while respecting linear constraints.
- **Proxy** = transparent approximation used when exact plant-specific data are unavailable.

See the Beginner Guide and in-app glossary for examples and common confusions.

## Architecture

```text
adapters / public research
        |
        v
versioned offline snapshots + provenance
        |
        v
case bundles
        |
        +--> core/          physical simulation
        +--> economics/     cost/NPV/payback
        +--> optimization/  sparse 8,760h LP + carbon + sensitivity
        +--> explainability/ metric registry + glossary + rule-based insights
        +--> ui/            Streamlit orchestration/presentation only
```

The UI does not reimplement engineering equations.

## v1 features

### Physical model

- strict 8,760-hour UTC validation;
- industrial electricity load;
- PV normalized capacity-factor profile;
- battery energy and power limits;
- charge/discharge efficiencies and explicit losses;
- state-of-charge bounds;
- deterministic PV-first simulator;
- self-consumption and self-sufficiency;
- grid import/export.

### Optimization

- continuous sparse LP solved with HiGHS through SciPy `linprog`;
- optimal PV capacity;
- optimal battery energy capacity;
- optimal battery power capacity;
- hourly dispatch;
- PV-only battery charging in v1;
- cyclic annual SOC boundary;
- site/model capacity bounds;
- normalized solver statuses;
- no material simultaneous charge/discharge or import/export in validated results.

### Economics

- initial CAPEX;
- technology-specific annualized CAPEX using CRF;
- OPEX;
- grid purchase cost;
- export revenue;
- total annualized system cost;
- equivalent annual saving versus baseline;
- simplified project NPV;
- simple payback.

### Carbon

- constant explicit grid-emission factor;
- no export CO₂ credit;
- optional minimum CO₂-reduction target;
- binding/non-binding detection;
- infeasibility handling;
- abatement cost;
- cost-decarbonization frontier.

### Sensitivity

Deterministic, one-at-a-time, **on-demand** families:

- electricity price;
- PV CAPEX;
- battery CAPEX;
- WACC;
- grid-emission factor;
- carbon target.

IEL intentionally does not run every sensitivity family on every UI rerun.

### Explainability

- centralized metric registry;
- centralized beginner glossary;
- acronym expansion;
- definitions, units, formulas, interpretations, relationships and caveats;
- source/provenance context for case inputs;
- deterministic “Why this solution?” insights;
- no generative-AI dependency.

## Representative Ceramic Plant — Castellón

The default v1 showcase is **`ceramic-castellon-v1`**, a public-data-calibrated representative electrical case with reference year 2025.

### Evidence chain

- **ASCER:** ceramic-sector production/energy context and Castellón cluster concentration;
- **OMIE:** 2025 Spanish day-ahead market-price calibration; treated as a wholesale energy-price proxy, not an industrial bill;
- **PVGIS/JRC methodology:** solar-resource reference; v1 commits a deterministic PVGIS-calibrated profile rather than claiming raw hourly PVGIS data;
- **Red Eléctrica:** Spanish 2025 generation/emissions used to derive the grid-emission factor;
- **IDAE:** Spanish screening ranges for PV/storage cost reasonableness;
- **IRENA:** international/European cost cross-check.

Every external value, proxy, derived value and assumption is traceable in [`cases/ceramic_castellon/sources.json`](cases/ceramic_castellon/sources.json).

### Representative scale

The case uses **15,000 MWh/year**. It is a rounded representative scale consistent with public sector order of magnitude — **not** “the average Castellón ceramic factory.”

### Frozen economic optimum

| Metric | Result |
|---|---:|
| Annual load | 15,000 MWh/year |
| Baseline modeled energy cost | €983,366/year |
| Baseline grid emissions | 1,625.6 tCO₂eq/year |
| Optimal PV | 2.972 MW |
| Optimal battery | 0 MWh / 0 MW |
| PV generation | 4,804 MWh/year |
| PV self-consumption | 94.9% |
| Electrical self-sufficiency | 30.4% |
| Grid imports | 10,441 MWh/year |
| Initial CAPEX | €2.080 M |
| Annualized system cost | €880,203/year |
| Equivalent annual improvement | €103,163/year |
| Simplified NPV | +€522,604 |
| Simple payback | 8.30 years |
| CO₂ reduction | 30.4% |
| Abatement cost | -€208.8/tCO₂ |

Battery = 0 is a valid result. The model does not force every available technology into the solution.

### Cost-decarbonization frontier

| Minimum CO₂ reduction | PV MW | Battery MWh | Battery MW | Annualized cost €/y | Binding? |
|---:|---:|---:|---:|---:|:---:|
| 0% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 10% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 20% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 30% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 40% | 4.25 | 2.46 | 0.57 | 927,346 | Yes |
| 50% | 5.34 | 6.83 | 1.45 | 1,007,628 | Yes |

The unconstrained economic optimum already reduces modeled electrical CO₂ by ~30.4%. Therefore 10–30% targets do not alter the solution. The 40% target is binding and storage enters.

Read the case study for the evidence, formulas, sensitivity and limitations behind these numbers.

## Streamlit interface

Nine sections:

1. Overview
2. Inputs
3. Baseline
4. Optimized system
5. Hourly results
6. Economics
7. Decarbonization
8. Sensitivity
9. Methodology & learning

Inputs use `st.form`, so editing a value does not repeatedly trigger the 8,760-hour optimizer.

The case selector provides:

- **Representative Ceramic Plant — Castellón** (default showcase);
- **Synthetic software demo** (regression/education reference).

## Installation

Python 3.11+:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

python -m pip install -e ".[dev,app]"
```

Engine-only installation:

```bash
python -m pip install -e ".[dev]"
```

## Reproduce datasets

```bash
python scripts/generate_demo_data.py
python scripts/build_ceramic_castellon_case.py
```

The ceramic builder produces deterministic offline snapshots and metadata.

## Run models

```bash
python scripts/run_baseline.py
python scripts/run_scenario.py
python scripts/run_optimization.py
python scripts/run_ceramic_castellon_case.py
```

## Run web app

```bash
streamlit run app.py
```

## Validation

```bash
python -m compileall -q src scripts tests
pytest
```

Golden Cases v1–v3 protect the synthetic engine history. `ceramic_castellon_case_v1.json` freezes the sourced representative case separately.

## Versioning

- application/package: **v1.0.0**;
- optimization model: **v0.3.0**;
- representative case: **ceramic-castellon-v1**;
- representative dataset: **ceramic-castellon-2025-v1**.

The model version remains 0.3.0 because Iteration 5 adds data, case integration and education rather than new optimization equations.

## Important limitations

IEL v1 does **not** model:

- ceramic thermal-process energy, kilns, dryers or natural gas;
- plant-specific measured data or contracts;
- full industrial tariffs, network charges, demand charges or taxes;
- PV/battery degradation and replacement;
- taxes, depreciation, salvage value or detailed financing;
- hourly grid-emission factors;
- grid-to-battery arbitrage;
- stochastic uncertainty;
- detailed engineering, interconnection, structural studies or permitting.

These limits are intentional. **Depth, traceability and a finished v1 are preferred to uncontrolled scope growth.**

## CV-ready description

> Developed a Python techno-economic screening tool for industrial electrical decarbonization, combining 8,760-hour energy modelling, linear PV/battery sizing optimization, carbon constraints, NPV and sensitivity analysis, explainability, and a public-data-calibrated ceramic-industry case study for Castellón, Spain.

## License

MIT. External source data remain subject to their respective source terms; IEL stores provenance and calibrated/derived case values rather than claiming ownership of external datasets.
