# Changelog

## 0.2.0 — Iteration 2: 8,760h PV + Battery

### Added

- offline PV generation module using installed capacity and normalized hourly capacity factor;
- battery specification with energy/power limits, AC-side charge/discharge efficiencies and SOC bounds;
- deterministic PV-first annual dispatch;
- explicit PV-to-load, PV-to-battery, PV export, battery discharge and grid import/export flows;
- explicit battery conversion losses and SOC trajectory;
- annual physical summary, self-consumption and self-sufficiency ratios;
- grid import cost, export revenue, net grid-energy cost and operating-savings calculation;
- scenario grid-emissions calculation with no export credit;
- synthetic `scenario_assumptions.json` for reproducible software validation;
- hand-checkable dispatch tests, annual physical-invariant tests and Golden Case v2;
- `scripts/run_scenario.py`.

### Preserved

- Golden Case v1 remains frozen with `model_version=0.1.0` and `case_version=golden-v1`;
- dataset version remains `demo-v1` because the three hourly CSV datasets are unchanged;
- core runtime remains offline with no HTTP/API calls.

### Explicitly not included

Mathematical optimization, price-arbitrage dispatch, degradation, sensitivity analysis, Streamlit UI and the Castellón ceramic case.

## 0.1.0 — Iteration 1 Energy Engine

### Added

- package structure and version identifiers;
- strict normalized hourly dataset validation;
- deterministic 8,760-hour synthetic demo datasets and metadata;
- grid-only baseline energy balance;
- annual consumption and hourly-price cost calculation;
- emissions, reduction and abatement-cost helpers;
- NPV, simple payback and capital-recovery-factor helpers;
- unit, integration and golden regression test structure;
- GitHub Actions CI definition;
- initial README, methodology, assumptions and future-scope documentation.
