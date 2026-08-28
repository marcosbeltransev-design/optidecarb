# OptiDecarb v1.0 — Validation Record

## Scope

Application/package v1.0.0 with optimization-model v0.3.0 and representative case `ceramic-castellon-v1` / dataset `ceramic-castellon-2025-v1`.

## Engineering validation

- Golden Case v1: baseline regression retained.
- Golden Case v2: deterministic PV+battery physical simulation retained.
- Golden Case v3: 8,760-hour optimization and binding-carbon regression retained.
- Ceramic case regression: economic optimum and 40% binding target frozen separately.
- Physical balances, SOC bounds, efficiencies, grid/PV residuals and zero cases covered by unit/integration tests.
- Economics covers annualized CAPEX, OPEX, grid purchases/export value, NPV, payback and abatement cost.
- Optimization uses cyclic annual SOC and PV-only battery charging in v1.

## Data/provenance validation

- all case datasets: exactly 8,760 UTC rows;
- no missing/duplicate timestamps;
- load/PV contract validation;
- monthly OMIE and solar calibration checks;
- source IDs resolve through a unique provenance registry;
- external values, derived values, proxies and model assumptions are explicitly classified;
- demo and ceramic builders are byte-reproducible for committed data/metadata.

## Educational validation

The central glossary includes 30+ concepts with:

- expanded acronym/full name;
- plain-language definition;
- technical definition;
- units when applicable;
- example;
- why it matters;
- related concepts;
- common confusion.

Key concepts include MW/MWh, PV, CF, battery MWh/MW, SOC, cyclic SOC, CAPEX/OPEX, annualized CAPEX, WACC, CRF, NPV, payback, baseline, LP, decision variables, objective, constraints, binding/infeasible, self-consumption/self-sufficiency, carbon target, abatement cost, sensitivity, proxy, derived value and model assumption.

## Test execution policy

All pytest files are executed in isolated processes by `python scripts/run_test_matrix.py` because repeated annual HiGHS solves can show cumulative runtime degradation in a single long Python process in some environments. CI mirrors that isolation for solver-heavy regressions.

Expected local sandbox result:

- 79 tests pass;
- 1 Streamlit AppTest is skipped only because the optional Streamlit dependency is unavailable in the sandbox.

When `.[app]` is installable, CI runs the Streamlit AppTest rather than skipping it.

## Streamlit limitation in this build sandbox

The application code imports Streamlit lazily, compiles, and UI service tests pass. Native AppTest/browser validation cannot run in this sandbox because Streamlit cannot be installed/downloaded here. This is treated as an external acceptance limitation, not a reason to alter the validated engineering engine.

## Deployment limitation

A standalone `marcosbeltransev-design/optidecarb` GitHub repository is not currently exposed through the connected GitHub integration. `notas-albinegras` is deliberately not reused. Public Streamlit deployment therefore remains an external post-v1 presentation step.

## Iteration 6 decision

**Not required for v1.0.** No physical, economic, optimization, provenance or reproducibility defect requiring a new iteration was found. Deployment/presentation polish is recorded in `FUTURE_IDEAS.md` rather than expanding v1 scope.
