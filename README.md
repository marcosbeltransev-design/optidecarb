![OptiDecarb](assets/optidecarb-logo.svg)

# OptiDecarb

**Industrial Energy Optimization & Learning for Future Engineers**

**Live app:** https://optidecarb.streamlit.app  
**Repository:** https://github.com/marcosbeltransev-design/optidecarb

OptiDecarb is an offline-first Python **screening / pre-feasibility** tool for industrial **electrical** decarbonization. It combines a validated 8,760-hour energy model, PV and battery optimization, techno-economics, CO₂ constraints, sensitivity analysis and a public-data-calibrated representative ceramic-industry case for Castellón, Spain.

Its educational purpose is deliberately narrow: use a real engineering model as a laboratory to learn **industrial energy analysis**.

> **Model scope:** electricity + PV + battery + grid. Thermal process energy, kilns, dryers and natural-gas consumption are outside Model v0.3.0.

> **Representative-case disclaimer:** The Castellón case is constructed from public sector data and explicit modelling assumptions. It does not reproduce the operations, costs or energy consumption of any individual ceramic company.

## What problem does the model solve?

> Given an industrial hourly electricity-demand profile, what PV and battery configuration minimizes equivalent annual energy-system cost, and how does that solution change under explicit electrical CO₂-reduction targets?

OptiDecarb jointly chooses PV capacity, battery energy/power capacity and hourly dispatch. Grid imports and PV exports follow from the hourly balance. The optimizer minimizes **total annualized cost**. NPV and simple payback are calculated afterwards as complementary screening indicators.

## Learn industrial energy by using the model

The learning chain is:

```text
ENERGY DATA → BASELINE → LOAD/PROFILE REASONING → PV/BESS → ECONOMICS
→ OPTIMIZATION → CO₂ → SENSITIVITY → SITE VALIDATION → RECOMMENDATION
```

The preferred learning loop is:

```text
ESTIMATE → PREDICT → CALCULATE / RUN → COMPARE → EXPLAIN WHY → CHECK NEXT
```

The aim is to move from:

```text
I have seen this
→ I understand it
→ I can estimate it
→ I can detect when it is wrong
→ I can explain why
→ I can support a better energy decision
```

### Active learning added in v1.3.1–v1.3.2

- real 8,760-hour Castellón load-profile reading;
- load-duration curve and explanation of what chronology it loses;
- formula → units → intuition exercises;
- predict-before-reveal sensitivity exercises;
- one-day and one-hour electrical-balance reconstruction;
- visual explanation of non-binding vs binding CO₂ constraints;
- **MODEL KNOWS / ASSUMES / DOES NOT KNOW** result interpretation;
- one unseen transfer case beyond Castellón;
- session-only review of missed concepts;
- energy-specific interview defence;
- **Energy Data Forensics** for missing intervals, duplicates, flatlines, unit-scale errors and net-meter sign conventions;
- evidence-quality ladder: measured / public / supplier / proxy / assumption;
- **Trace the number** chains from source → assumption → calculation → result → decision;
- sensitivity → **what data should I improve next?** training.

The colour language is semantic rather than decorative:

- **blue** = data / concept;
- **green** = validated / correct;
- **amber** = assumption / check;
- **red** = inconsistency / risk.

## Questions the app should teach you to ask

- What exactly does this meter measure?
- Are the units correct?
- Are all 8,760 timestamps present and unique?
- Do annual MWh, average MW and peak MW make physical sense together?
- What order of magnitude should I expect before running the model?
- Does PV generation look plausible for the installed MWp?
- What do battery MW, MWh, duration and SOC each mean?
- Is the electricity price a real tariff or only a wholesale proxy?
- Which assumption materially changes the recommendation?
- Is a constraint binding?
- Can I trace this number back to its source and assumption?
- What evidence should I request next?
- What does the model not know about the real site?
- Is this screening result strong enough for a feasibility decision?

## Why 8,760 hours?

A non-leap year has `24 × 365 = 8,760` hours. Hourly modelling preserves:

- load/PV coincidence;
- battery state of charge;
- charge/discharge timing;
- hourly electricity-price exposure;
- onsite PV use versus export.

Annual totals alone cannot reproduce those interactions.

## Representative Ceramic Plant — Castellón

Default showcase: **`ceramic-castellon-v1`**  
Dataset: **`ceramic-castellon-2025-v1`**

### Representative electrical scale

| Metric | Frozen result |
|---|---:|
| Annual load | 15,000 MWh/year |
| Average demand | 1.712 MW |
| Peak demand | 1.998 MW |
| Load factor | 85.7% |
| Baseline modeled energy cost | €983,366/year |
| Baseline grid emissions | 1,625.6 tCO₂eq/year |

### Frozen economic optimum

| Metric | Frozen result |
|---|---:|
| Optimal PV | 2.972 MWp |
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
| Electrical CO₂ reduction | 30.4% |

**Battery = 0 does not mean batteries are useless.** It means that, under the current economic assumptions and services represented by Model v0.3.0, storage is not selected in the unconstrained economic optimum.

### Cost-decarbonization frontier

| Minimum electrical CO₂ reduction | PV MWp | Battery MWh | Battery MW | Annualized cost €/y | Binding? |
|---:|---:|---:|---:|---:|:---:|
| 0% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 10% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 20% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 30% | 2.97 | 0.00 | 0.00 | 880,203 | No |
| 40% | 4.25 | 2.46 | 0.57 | 927,346 | Yes |
| 50% | 5.34 | 6.83 | 1.45 | 1,007,628 | Yes |

The economic optimum already reduces modeled electrical CO₂ by about 30.4%. Therefore a 20% target is non-binding. A 40% target is binding and the validated solution adds more PV and battery storage.

## Evidence and provenance

The representative case keeps external evidence separate from model assumptions.

- **ASCER** — ceramic-sector and Castellón cluster context;
- **OMIE** — wholesale day-ahead electricity-price calibration;
- **PVGIS/JRC** — solar-resource reference for the deterministic PV profile;
- **Red Eléctrica** — public generation/emissions basis for the representative grid factor;
- **IDAE / IRENA** — screening reasonableness checks for technology costs.

OMIE is always treated as a **WHOLESALE ENERGY PRICE PROXY**, not as the complete electricity bill of an industrial company.

Every important case input is classified as public evidence, derived value, proxy or explicit model assumption in the case provenance files.

## Architecture

```text
public research / adapters
        |
        v
versioned offline snapshots + provenance
        |
        v
case bundles
        |
        +--> core/          physical simulation
        +--> economics/     cost / NPV / payback
        +--> optimization/  sparse 8,760h LP + carbon + sensitivity
        +--> explainability/ metric registry + deterministic insights
        +--> learning/      active industrial-energy learning content
        +--> ui/            Streamlit orchestration / presentation only
```

The UI does not reimplement engineering equations. The core and optimizer do not call external APIs at runtime.

## Model features

### Physical

- strict 8,760-hour UTC validation;
- industrial electricity load;
- PV capacity-factor profile;
- battery energy/power limits;
- charging/discharging efficiencies;
- SOC bounds;
- PV/grid/battery hourly balance;
- grid import/export;
- self-consumption and self-sufficiency.

### Optimization

- continuous sparse linear program;
- SciPy `linprog` / HiGHS;
- optimal PV capacity;
- optimal BESS energy and power capacity;
- hourly dispatch;
- PV-only battery charging in Model v0.3.0;
- cyclic annual SOC condition;
- explicit site/model capacity bounds;
- optional minimum electrical CO₂-reduction constraint.

### Economics

- initial CAPEX;
- annualized CAPEX using CRF;
- OPEX;
- grid-purchase cost;
- export revenue;
- equivalent annual saving;
- simplified NPV;
- simple payback.

### Sensitivity

Deterministic one-at-a-time families include electricity price, PV CAPEX, battery CAPEX, WACC, grid-emission factor and carbon target.

Sensitivity in OptiDecarb is used not only to say **what changed**, but also to ask:

> Which assumption should I validate better before I trust the recommendation?

## Screening vs feasibility

OptiDecarb is designed for screening / pre-feasibility learning.

A real feasibility study would still need, among other things:

- validated site meter data and invoices;
- real tariff / contract terms;
- buildable PV area and structural assessment;
- grid/export conditions;
- comparable EPC quotations;
- detailed yield/layout assessment;
- detailed electrical engineering;
- site-specific operational constraints.

A solver result such as `2.972 MWp` should therefore normally be communicated as **around 3 MWp under the current screening assumptions**.

## AI-assisted development — stated transparently

OptiDecarb was developed using **AI-assisted software development**. It is not presented as a project where every line was manually written by the student.

The engineering and educational value comes from:

- defining the problem and model boundary;
- challenging assumptions;
- researching traceable public evidence;
- validating model behaviour and frozen regressions;
- interpreting results;
- designing the learning workflow;
- understanding what the model can and cannot conclude.

The production app does not call an LLM at runtime to generate engineering conclusions.

## Recommended study route

1. [`docs/BEGINNER_GUIDE.md`](docs/BEGINNER_GUIDE.md)
2. in-app **Learning Lab**
3. in-app **Industrial Energy Junior Lab**
4. [`docs/LEARNING_ARCHITECTURE.md`](docs/LEARNING_ARCHITECTURE.md)
5. [`cases/ceramic_castellon/CASE_STUDY.md`](cases/ceramic_castellon/CASE_STUDY.md)
6. [`docs/OPTIMIZATION_GUIDE.md`](docs/OPTIMIZATION_GUIDE.md)
7. [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md)
8. [`docs/CV_AND_INTERVIEW_POSITIONING.md`](docs/CV_AND_INTERVIEW_POSITIONING.md)

## Install and run

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate  # Windows
python -m pip install -e ".[dev,app]"
streamlit run app.py
```

## Validation

```bash
python -m compileall -q src scripts tests app.py
python scripts/run_test_matrix.py
```

The isolated test runner is intentional. Repeated large 8,760-hour HiGHS solves can degrade when accumulated in one long-lived process, so the heavy regressions are validated in fresh processes.

## Versioning

- application/package: **v1.3.2**;
- optimization model: **v0.3.0**;
- representative case: **ceramic-castellon-v1**;
- representative dataset: **ceramic-castellon-2025-v1**.

The model version remains 0.3.0 because v1.3.x changes educational architecture, visualization and learning workflow — not optimization equations.

## Important limitations

OptiDecarb does **not** model ceramic thermal-process energy, plant-specific measured contracts, full industrial tariffs, degradation/replacement, taxes/depreciation, hourly grid-emission factors, grid-to-battery arbitrage, stochastic uncertainty or detailed engineering/interconnection/permitting.

It also does not replace industrial electrical safety competence, site experience, detailed electrical design, supplier negotiation or commissioning responsibility.

## CV-ready description

> Designed and developed OptiDecarb, an AI-assisted Python learning and screening tool for industrial electrical decarbonization, using the project to develop practical skills in 8,760-hour energy modelling, energy-data validation, PV/BESS techno-economics, optimization, sensitivity and engineering decision-making.

## License

MIT. External source data remain subject to their respective source terms; OptiDecarb stores provenance and calibrated/derived case values rather than claiming ownership of external datasets.
