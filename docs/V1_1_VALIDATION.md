# Industrial Energy Lab v1.1 — Student Learning Lab validation

## Scope

v1.1 adds **education/UI services only**. The physical and optimization model remains **v0.3.0**; Golden Cases v1–v3 and `ceramic-castellon-v1` remain the engineering regressions.

## Automated tests

Total discovered tests after Student Learning Lab: **102**.

Expected in the current sandbox:

- **101 PASS**
- **1 SKIP** — `tests/integration/test_streamlit_smoke.py` because Streamlit cannot be installed in this runtime
- **0 FAIL**

Solver-heavy files are validated in isolated processes because repeated annual HiGHS solves can degrade in one long-lived process in this environment.

## Student-learning checks

Validated deterministic examples:

- `5 MW × 3 h = 15 MWh`;
- `4 MWh / 2 MW = 2 h` battery duration before SOC/efficiency limits;
- `180 kgCO₂/MWh × 1,000 MWh = 180 tCO₂`;
- CRF at 5%, 25 years ≈ `0.07095/year`;
- three-hour battery lab reproduces `[10.0, 0.0, 1.9] kWh` grid imports, `[0.0, 9.0, 0.0] kWh` SOC and `1.9 kWh` losses;
- hourly energy-balance residual remains below numerical tolerance;
- worked-calculation registry covers self-consumption, self-sufficiency, emissions, CO₂ reduction, abatement cost, initial/annualized CAPEX, CRF, annual saving, NPV and payback;
- 12 deterministic concept questions are structurally validated;
- six guided experiments reference valid glossary concepts and change only intended inputs.

## Guided experiments — frozen Castellón case

Each full-year experiment was manually executed on demand against the same 8,760-hour engine:

| Experiment | Before | After | Observed learning point |
|---|---:|---:|---|
| Electricity price +20% | PV 2.972 MW | PV 3.193 MW | higher avoided grid cost increases cost-optimal PV under tested assumptions |
| PV CAPEX +20% | PV 2.972 MW | PV 2.788 MW | more expensive PV reduces cost-optimal PV |
| WACC 5% → 6% | PV 2.972 MW | PV 2.870 MW | higher CRF/annualized capital cost reduces capital-intensive sizing |
| Carbon target 20% → 40% | 20% non-binding | 40% binding; battery 2.460 MWh | constraint becomes active only when stricter than economic optimum |
| Battery CAPEX −20% | battery 0 MWh | battery 0 MWh | cheaper storage does not automatically make storage economical |
| Fixed PV +50% above optimum | self-consumption 94.9%; export 245 MWh/y | self-consumption 75.6%; export 1,761 MWh/y | imports fall, but marginal PV increasingly spills to export |

The experiment language remains conditional. These results are model/case outputs, not universal causal laws.

## Educational acceptance

The WACC learning journey now supports:

1. expanded name and plain definition;
2. worked numerical CRF example;
3. explicit relationship to annualized CAPEX;
4. editable learning WACC/lifetime calculator;
5. prediction before experiment;
6. on-demand 8,760-hour re-solve;
7. before/after comparison;
8. engineering interpretation and model limitation.

Equivalent pathways exist for PV/battery/SOC, CAPEX/NPV/payback, carbon targets, self-consumption/self-sufficiency and provenance concepts.

## Streamlit limitation

The application source, navigation and optional AppTest are present, but Streamlit is still unavailable in this sandbox. Native browser/AppTest validation therefore remains an external acceptance check. This does not change engine, learning-service or documentation validation.
