# Industrial Energy Lab

**Industrial Decarbonization & Techno-Economic Screening**

Industrial Energy Lab is an offline-first Python pre-feasibility tool for industrial electrical-energy systems. Its v1 scope is intentionally narrow: 8,760-hour load modelling, PV, battery storage, grid exchange, transparent economics, grid-related CO2 accounting, linear optimization, deterministic sensitivity analysis, and a later representative ceramic-industry case for Castellón, Spain.

> **Status:** Iteration 3 — Optimization is complete locally. The project now contains a validated 8,760-hour physical simulator, an LP sizing/dispatch optimizer solved with HiGHS, carbon constraints, a cost-decarbonization frontier, deterministic sensitivity analysis, rule-based explainability, and frozen Golden Cases v1–v3. Streamlit and the sourced Castellón ceramic case remain intentionally deferred to Iterations 4 and 5.

## What problem does it solve?

The v1 screening question is:

> Given an industrial site's annual hourly electricity profile, what PV and battery configuration minimizes equivalent annual energy-system cost, and how does that solution change under explicit CO2-reduction targets?

The optimizer jointly chooses:

- PV capacity [kW];
- battery energy capacity [kWh];
- battery power capacity [kW];
- hourly PV allocation;
- hourly battery charge/discharge;
- hourly SOC;
- residual grid import/export.

The objective minimizes **total annualized cost**, while project NPV and simple payback are calculated afterwards as complementary investment indicators.

## What it does **not** claim

This is not detailed engineering, FEED, a certified energy model, financial advice, an industrial control system, a universal energy-system simulator, or a digital twin. All current demo economics and profiles are synthetic software-validation assumptions and must not be interpreted as current market quotes or measurements from a real factory.

## Architecture

```text
external data sources (future adapters)
        |
        v
versioned offline datasets
        |
        v
8,760h physical engine
  |       |       |
 load     PV    battery
          |       |
          +-- physical balances --+
                                  |
                                  v
                         economics + CO2
                                  |
                                  v
                       linear optimization
                         |      |       |
                       sizing  carbon  sensitivity
                                  |
                                  v
                         explainability registry
                                  |
                                  v
                        Streamlit UI (Iteration 4)
```

`core/`, `optimization/` and `explainability/` make no HTTP/API calls. Runtime calculations consume local snapshots.

## Implemented features

### Iteration 1 — frozen baseline

- strict 8,760-hour UTC dataset validation;
- deterministic synthetic industrial load and hourly electricity prices;
- exact grid-only baseline;
- annual consumption, cost and grid-related CO2;
- NPV, simple payback and CRF helpers;
- Golden Case v1.

### Iteration 2 — physical PV + battery simulation

- PV generation from installed capacity and normalized hourly capacity factor;
- battery energy/power limits, charge/discharge efficiency and SOC bounds;
- deterministic PV-first dispatch;
- PV direct use, PV-to-battery, battery-to-load and PV export;
- grid import/export and explicit battery losses;
- self-consumption and self-sufficiency metrics;
- scenario operating economics and emissions;
- Golden Case v2.

### Iteration 3 — optimization, carbon and explainability

- 8,760-hour linear-programming sizing and dispatch;
- optimal PV capacity, battery energy and battery power;
- cyclic annual SOC boundary;
- battery charging restricted to PV allocation, not grid arbitrage;
- residual grid import/export formulation with no redundant import/export variables;
- explicit model bounds for site feasibility and numerical robustness;
- total annualized cost objective;
- technology-specific CRFs and OPEX;
- post-processed project NPV and simple payback;
- optional minimum CO2-reduction constraint;
- solver states: `optimal`, `infeasible`, `unbounded`, `solver_error`;
- cost-decarbonization frontier (0/10/20/30/40/50% by default);
- deterministic one-at-a-time sensitivity analysis;
- on-demand sensitivity-family execution for interactive use;
- battery CAPEX break-even scan support;
- 58-metric explainability registry for future `?` help controls;
- deterministic result-based insights without generative AI;
- Golden Case v3 and binding-carbon regression.

## Solver backend

Iteration 3 is formulated as a sparse LP and solved with **HiGHS through SciPy `linprog`**:

- HiGHS dual simplex for unconstrained economic sizing;
- HiGHS interior-point for explicit carbon-constrained annual problems.

Pyomo + HiGHS was the original preferred stack. In the current build environment, new Pyomo/highspy packages could not be installed, while SciPy already exposed a working HiGHS backend. Using SciPy preserves the essential open-source HiGHS solver, keeps the formulation linear/offline, reduces dependencies, and is fully tested. The optimization layer is kept separate so a future Pyomo adapter could be added without changing the physical/economic conventions if it ever adds concrete value.

## Golden Case v3 — synthetic optimization case

All inputs below are **ASSUMPTION / SOFTWARE VALIDATION ONLY**.

Economic optimum:

- annual load: **22,000 MWh**;
- PV: **4.088 MW**;
- battery: **0 MWh / 0 MW**;
- total annualized cost: **€1.750 million/year**;
- equivalent annual saving vs baseline: **€218.6k/year**;
- grid-import reduction / modeled CO2 reduction: **33.4%**;
- project NPV under the simplified 15-year post-processing model: **+€0.546 million**.

40% minimum CO2 reduction:

- PV: **5.210 MW**;
- battery: **2.596 MWh / 0.493 MW**;
- carbon constraint: **binding**;
- total annualized cost: **€1.774 million/year**;
- modeled reduction: **40.0%**.

This contrast is deliberate: it demonstrates that storage can be absent from the pure economic optimum but enter when a stricter decarbonization requirement changes the feasible solution.

## Cost-decarbonization frontier — Golden Case v3 assumptions

| Minimum CO2 reduction | PV MW | Battery MWh | Battery MW | Annualized cost M€/y | Binding? |
|---:|---:|---:|---:|---:|:---:|
| 0% | 4.09 | 0.00 | 0.00 | 1.750 | No |
| 10% | 4.09 | 0.00 | 0.00 | 1.750 | No |
| 20% | 4.09 | 0.00 | 0.00 | 1.750 | No |
| 30% | 4.09 | 0.00 | 0.00 | 1.750 | No |
| 40% | 5.21 | 2.60 | 0.49 | 1.774 | Yes |
| 50% | 6.61 | 9.42 | 1.59 | 1.836 | Yes |

Targets already met by the unconstrained economic optimum reuse that mathematically identical solution instead of re-solving the annual LP.

## Explainability and future `?` controls

`src/industrial_energy_lab/explainability/metrics.py` is the single source of truth for future help icons. Each important metric contains:

- label and unit;
- plain-language definition;
- why it matters;
- calculation/formula;
- interpretation;
- relationships with other metrics;
- caveats.

Iteration 4 will render that metadata beside each important metric card as a `?` help control. Explanations are not duplicated across pages.

`insights.py` adds deterministic result-driven statements such as whether a carbon constraint is binding, whether optimal storage is zero, how capacities change between two solved scenarios, and whether modeled abatement cost is positive or negative.

## Installation

Python 3.11+:

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

The generator uses seed `20260827` and creates exactly 8,760 UTC hours.

## Run the models

```bash
python scripts/run_baseline.py
python scripts/run_scenario.py
python scripts/run_optimization.py
```

## Run validation

```bash
python -m compileall -q src scripts tests
pytest
```

## Data/time policy

Engine input is normalized to exactly 8,760 uninterrupted UTC hours. Leap-year and local-DST data must be normalized before entering the engine. Duplicate, missing or non-hourly timestamps fail validation.

## Documentation

- `METHODOLOGY.md` — physical/economic/LP equations and conventions.
- `ASSUMPTIONS.md` — explicit synthetic assumptions and limitations.
- `docs/OPTIMIZATION_GUIDE.md` — pedagogical introduction to the optimization model.
- `docs/ARCHITECTURE.md` — architecture decisions.
- `FUTURE_IDEAS.md` — deferred scope.
- `CHANGELOG.md` — model changes.

## Roadmap

1. **Energy Engine** — complete/frozen.
2. **8,760h + PV + Battery** — complete/frozen.
3. **Optimization** — complete/frozen after v0.3 validation.
4. **Streamlit Web** — next; metric cards will consume the centralized `?` explainability registry.
5. **Castellón Ceramic Case** — sourced representative case study.

After Iteration 5, v1.0 is considered complete. Any thermal or hydrogen extension requires an explicit product decision.

## License

MIT for project code and project-generated synthetic demo data. External datasets added later must retain their own source/license metadata.
