![OptiDecarb](assets/optidecarb-logo.svg)

# OptiDecarb

**Industrial Energy Optimization & Learning for Future Engineers**

**Live app:** https://optidecarb.streamlit.app

> **Branding note:** the public project name is **OptiDecarb**. The internal Python import namespace remains `industrial_energy_lab` for backward compatibility with the validated codebase.

OptiDecarb is an offline-first Python **screening / pre-feasibility** tool for industrial **electrical** decarbonization. It combines a validated 8,760-hour energy model, PV and battery optimization, transparent economics, CO₂ constraints, sensitivity analysis and a public-data-calibrated representative ceramic-industry case for Castellón, Spain.

From **v1.3**, its educational purpose is deliberately focused: use the engineering model as a laboratory to learn **industrial energy analysis**. The learning path is not a generic junior-career course. It centres on load and metering, energy-data quality, PV/BESS, electricity economics, optimization, CO₂, sensitivity, site/project constraints, supplier quotations and defensible energy recommendations.

> **Model scope:** electricity + PV + battery + grid. Thermal process energy, kilns, dryers and natural-gas consumption remain outside the current model boundary.

> **Case disclaimer:** The Castellón representative case is constructed from public sector data and explicit modelling assumptions. It does not reproduce the operations, costs or energy consumption of any individual ceramic company.

## The learning goal

OptiDecarb should help a student move through:

```text
ENERGY DATA → BASELINE → LOAD/PROFILE REASONING → PV/BESS → ECONOMICS
→ OPTIMIZATION → CO₂ → SENSITIVITY → SITE/PROJECT VALIDATION → RECOMMENDATION
```

The recurring questions are practical energy-engineering questions:

- What exactly does this meter measure and in which unit?
- Do annual MWh, average MW and peak MW make sense together?
- Is the hourly timeline complete and correctly ordered?
- What would I expect before running the model?
- Is PV generation plausible for the installed MWp?
- What do battery MW, MWh, duration, SOC and efficiency mean?
- Is the electricity price a real tariff or only a wholesale proxy?
- Which assumption drives NPV or the optimal PV/BESS size?
- Is a CO₂ target binding?
- What site, grid or export fact is missing?
- What should I ask a PV/BESS supplier?
- Can I defend the recommendation as screening rather than construction-ready design?

## What problem does the engineering model solve?

> Given an industrial hourly electricity demand profile, what PV and battery configuration minimizes equivalent annual energy-system cost, and how does that solution change under explicit CO₂-reduction targets?

OptiDecarb jointly chooses PV capacity, battery energy/power capacity and hourly dispatch. Grid imports and PV exports follow from the hourly energy balance. The optimizer minimizes **total annualized cost**. Net Present Value (NPV) and simple payback are calculated afterwards as complementary screening indicators.

## Learn with OptiDecarb v1.3

The app combines:

1. **Engineering model** — validated 8,760-hour PV/battery/grid model and LP optimization.
2. **Learning Lab** — worked calculations, guided experiments and concept checks.
3. **Industrial Energy Junior Lab** — diagnostic, energy-data quality, quick estimates, tariffs/economics, site/project work, PV/BESS quotation review, energy communication and a final capstone.
4. **Clear professional English** — easy explanation first, professional term second, optional deeper technical detail after that.

General professional skills are included only when they support an energy task. For example, the app does not teach generic email writing; it shows how to request interval electricity data or clarify a PV/BESS quotation.

## Recommended study route

- [`docs/BEGINNER_GUIDE.md`](docs/BEGINNER_GUIDE.md) — foundations in clear English;
- in-app **Learning Lab** — predict, experiment and explain;
- in-app **Industrial Energy Junior Lab** — practise energy data, PV/BESS, economics, site and supplier reasoning;
- [`docs/LEARNING_ARCHITECTURE.md`](docs/LEARNING_ARCHITECTURE.md) — learning structure and scope;
- [`docs/JUNIOR_ENGINEER_GUIDE.md`](docs/JUNIOR_ENGINEER_GUIDE.md) — how to approach an early industrial-energy study;
- [`docs/INDUSTRY_CASES.md`](docs/INDUSTRY_CASES.md) — energy-focused junior cases;
- [`cases/ceramic_castellon/CASE_STUDY.md`](cases/ceramic_castellon/CASE_STUDY.md) — representative Castellón capstone;
- [`docs/STUDENT_LAB.md`](docs/STUDENT_LAB.md) — guided technical exercises;
- [`docs/OPTIMIZATION_GUIDE.md`](docs/OPTIMIZATION_GUIDE.md) — deeper LP formulation;
- [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) — technical interview preparation;
- [`docs/CV_AND_INTERVIEW_POSITIONING.md`](docs/CV_AND_INTERVIEW_POSITIONING.md) — honest AI-assisted project positioning.

## AI-assisted development — stated honestly

OptiDecarb was developed using **AI-assisted software development**. It is not presented as a project where every line of code was manually written by the student. The engineering and educational value comes from defining the problem and scope, challenging assumptions, researching public evidence, validating model behaviour, interpreting results, designing the learning workflow and making sure the methodology and limitations can be explained.

AI is used here as a tool to learn and build faster — **not as a substitute for understanding**. The production app does not call an LLM at runtime to generate engineering explanations.

## How OptiDecarb works

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

A non-leap year has `24 × 365 = 8,760` hours. Hourly modeling preserves load/PV coincidence, battery state of charge, charge/discharge timing, hourly electricity-price exposure and PV export versus onsite use.

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
        +--> learning/      worked examples + industrial-energy learning content
        +--> ui/            Streamlit orchestration/presentation only
```

The UI does not reimplement engineering equations.

## Engineering features

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

Deterministic, one-at-a-time, **on-demand** families: electricity price, PV CAPEX, battery CAPEX, WACC, grid-emission factor and carbon target.

### Industrial Energy Junior Lab

- 12-question energy diagnostic without gamification;
- 9 energy-data quality cases including missing/duplicate intervals, leap year, sign/boundary, spikes, flatlines and unit/locale errors;
- back-of-the-envelope MW/MWh, PV-yield and BESS-duration checks;
- first energy-data request with the reason for every item;
- assumptions log and traceability;
- wholesale price proxy versus real industrial-bill context;
- PV/BESS site, grid/export and project-risk awareness;
- supplier quotation and simplified datasheet review;
- energy-specific communication exercises;
- AI verification using units, evidence and model-boundary checks;
- final Industrial PV + BESS capstone and Castellón investment-committee questions.

## Representative Ceramic Plant — Castellón

The default showcase is **`ceramic-castellon-v1`**, a public-data-calibrated representative electrical case with reference year 2025.

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

## Installation

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate  # Windows
python -m pip install -e ".[dev,app]"
```

## Run web app

```bash
streamlit run app.py
```

## Validation

```bash
python -m compileall -q src scripts tests
python scripts/run_test_matrix.py
```

The isolated test runner is intentional: repeated annual HiGHS solves can degrade when many large LPs are accumulated in a single long-lived process in the current environment. Each heavy regression is therefore validated in a fresh process. SciPy is pinned to the validated solver interface for strict reproducibility.

## Versioning

- application/package: **v1.3.0**;
- optimization model: **v0.3.0**;
- representative case: **ceramic-castellon-v1**;
- representative dataset: **ceramic-castellon-2025-v1**.

The model version remains 0.3.0 because v1.3 changes educational architecture and UI only, not the optimization equations.

## Important limitations

OptiDecarb does **not** model ceramic thermal-process energy, plant-specific measured contracts, full industrial tariffs, degradation/replacement, taxes/depreciation, hourly grid-emission factors, grid-to-battery arbitrage, stochastic uncertainty or detailed engineering/interconnection/permitting.

It also does not replace real site experience, industrial electrical safety, detailed electrical design, supplier negotiation or commissioning responsibility.

## CV-ready description

> Designed and developed OptiDecarb, an AI-assisted Python learning and screening tool for industrial electrical decarbonization, using the project to develop practical skills in 8,760-hour energy modelling, energy-data validation, PV/BESS techno-economics, optimization, sensitivity and engineering decision-making.

## License

MIT. External source data remain subject to their respective source terms; OptiDecarb stores provenance and calibrated/derived case values rather than claiming ownership of external datasets.
