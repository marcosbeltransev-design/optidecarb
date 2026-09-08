# Changelog

## 1.3.2 — Energy Data Forensics & Evidence Traceability

### Added

- visual **Energy Data Forensics** exercises for missing intervals, duplicate timestamps, suspicious flatlines, unit-scale errors and net-meter sign conventions;
- qualitative evidence-confidence ladder covering measured site data, official/public evidence, supplier/EPC information, proxies/benchmarks and explicit model assumptions;
- **Trace the number** learning chains from source/evidence → assumption/proxy → calculation/model input → result → decision use;
- sensitivity-to-evidence training that converts frozen one-at-a-time scenario results into practical next-data requests;
- explicit warning that the sensitivity perturbations are not normalized to equal uncertainty and therefore are not a global statistical ranking;
- session-review integration for missed forensic and evidence-priority concepts.

### Changed

- application/package version advanced to **1.3.2**;
- README, static portfolio fallback and deployment recovery documentation aligned with the active learning architecture and current version;
- Industrial Energy Junior Lab now asks the student to diagnose data before cleaning it and trace important results before trusting them.

### Preserved

- Optimization Model remains **v0.3.0**;
- `ceramic-castellon-v1`, `ceramic-castellon-2025-v1` and frozen numerical regressions remain unchanged;
- no changes to `core/`, `optimization/` or `economics/`;
- no new energy technology, tariff engine, runtime AI or external runtime API.

## 1.3.1 — Active Industrial Energy Learning

### Added

- semantic learning palette: blue=data/concept, green=validated/correct, amber=assumption/check and red=inconsistency/risk;
- real 8,760-hour Castellón load/PV profile reading and load-duration curve;
- formula → units → intuition exercises;
- predict-before-reveal sensitivity lessons using frozen validated Castellón results;
- one-day and one-hour electrical-balance reconstruction;
- visual CO₂ frontier explaining non-binding versus binding targets;
- MODEL KNOWS / MODEL ASSUMES / MODEL DOES NOT KNOW result cards;
- screening-versus-feasibility comparison;
- one smaller unseen transfer case;
- session-only review of missed concepts and energy-specific interview defence.

### Preserved

- Optimization Model remains **v0.3.0** and the UI does not reimplement engineering equations;
- committed Castellón data and regression targets remain unchanged.

## 1.3.0 — Industrial Energy Learning Architecture

### Added / Changed

- refocused the Junior Engineer experience around **industrial electrical energy** rather than generic professional training;
- introduced an energy-readiness diagnostic, energy-data/sanity-check workflow, electricity economics, site/project practice, PV/BESS supplier review, energy communication, AI validation and a Castellón energy capstone;
- established the main learning chain: energy data → baseline → load/profile reasoning → PV/BESS → economics → optimization → CO₂ → sensitivity → site/project validation → recommendation;
- kept professional communication and career material only where directly connected to an industrial-energy task.

### Preserved

- Optimization Model remains **v0.3.0**;
- no new physics or energy technologies.

## 1.2.0 — Junior Engineer & Industry Learning Lab

### Added

- dedicated **Junior Engineer Lab** for imperfect data, sanity checks, client situations, supplier questions, stakeholder thinking and professional communication;
- optional **Industry Mode** layered on top of Learning Mode;
- eight deterministic mini industry cases with correct-answer reasoning, weaker-answer feedback, checks and next-data requests;
- professional vocabulary registry covering screening, feasibility, FEED, EPC, due diligence, PPA, curtailment, tariffs, commissioning, O&M and related terms;
- role-specific learning for operations, finance, sustainability, maintenance and management;
- practical checklists before modelling, trusting results, management presentation, supplier contact and CO₂ claims;
- explicit “Can I trust this result?” and “What would a company do next?” guidance for solved systems;
- original OptiDecarb logo, favicon sizes, ICO asset and lightweight engineering hero illustration;
- Windows installed-site guide;
- honest AI-assisted development and CV/interview positioning documentation.

### Changed

- user-facing education rewritten toward **clear international professional English**: simple idea first, professional term second, optional technical detail after;
- glossary expanded with easy explanations, difficulty metadata and limited Spanish clarification for selected difficult terms;
- Overview, Inputs, errors, Optimization, Economics, Decarbonization, Sensitivity and Methodology receive clearer educational / junior-engineer context;
- README and learning documentation reposition OptiDecarb as both a validated engineering model and a learning environment.

### Preserved

- optimization model remains **v0.3.0**;
- no new physics, energy technologies, database, accounts, chatbot or runtime AI;
- `ceramic-castellon-v1`, `ceramic-castellon-2025-v1` and frozen regression targets remain unchanged.

## 1.1.1 — OptiDecarb rebrand

- renamed the public product from **Industrial Energy Lab** to **OptiDecarb**;
- changed the recommended GitHub/Streamlit slug to `optidecarb`;
- updated Streamlit titles, documentation, tests, source attribution and portfolio wording;
- retained the internal Python module `industrial_energy_lab` for backward-compatible imports;
- no physical, economic or optimization equations changed; model version remains **0.3.0**.

## 1.1.0 — Student Learning Lab

### Added

- dedicated Streamlit **Learning Lab** with six progressive learning modules;
- structured worked-calculation layer using the active solved scenario;
- formula → numerical substitution → result → unit-check explanations;
- hand-checkable power/energy, battery-duration, CRF and three-hour battery labs;
- six one-change-at-a-time guided experiments with prediction-before-run workflow;
- scenario A/B comparison for capacities, grid imports, annualized cost, NPV and CO₂;
- `Explain this hour` dispatch narration and hourly energy-balance residual;
- ten-step Castellón walkthrough and evidence-chain exercise;
- common engineering traps, concept dependencies and 12-question deterministic concept check;
- final student scenario challenge framed as a pre-feasibility next-study decision;
- `docs/STUDENT_LAB.md` plus Beginner/Interview Guide cross-links.

### Preserved

- optimization model remains **v0.3.0**;
- `ceramic-castellon-v1` and `ceramic-castellon-2025-v1` remain unchanged;
- Golden Cases v1–v3 and ceramic regression remain unchanged;
- no new physics, technologies, database, accounts, chatbot or generative-AI dependency.

## 1.0.0 — Representative Castellón case + learning layer

### Added
- `ceramic-castellon-v1` public-data-calibrated representative electrical case.
- 8,760-hour deterministic load, OMIE-calibrated wholesale-price proxy and PVGIS-calibrated solar profile.
- Case provenance registry with official/sector data, derived values, proxies and model assumptions.
- Offline case builder, runners, regression and source-provenance tests.
- Streamlit case selector with Castellón showcase as default and synthetic demo retained.
- Source/provenance context in input help.
- Central beginner glossary for energy, finance, optimization and provenance concepts.
- Learning mode and expanded methodology/glossary presentation.
- `CASE_STUDY.md`, `BEGINNER_GUIDE.md` and `INTERVIEW_GUIDE.md`.

### Fixed
- Imported `CERAMIC_CASE_ID` explicitly in the Streamlit application, preventing a `NameError` when rendering ceramic-case Inputs.

### Unchanged
- Optimization model equations remain **v0.3.0**.
- Golden Cases v1, v2 and v3 remain historical regression references.

## 0.4.0 — Iteration 4: Streamlit Web

### Added

- Streamlit engineering interface with nine focused sections;
- form-submit optimization workflow and limited session-state result persistence;
- central metric/input help rendered through native Streamlit `help` controls;
- deterministic result explanations and sensitivity observations;
- baseline, hourly, SOC, economics, cost-decarbonization and sensitivity Plotly charts;
- on-demand carbon-frontier and one-family sensitivity execution;
- strict optional 8,760-hour custom-load upload aligned to the versioned demo timeline;
- friendly infeasible/unbounded/solver-error presentation;
- `requirements.txt`, pinned Streamlit 1.62.0 app extra and Streamlit theme configuration;
- UI unit/service tests and optional native `AppTest` smoke test for CI.

### Preserved

- v0.3 optimization model and Golden Cases v1–v3;
- engineering equations remain outside Streamlit;
- no database, backend, auth, generative AI or external runtime API dependency.

### Validation and deployment state

- 66 non-Streamlit tests pass locally after reinstalling the editable package from the active repository;
- clean-clone regression, dataset reproducibility and compile checks pass;
- the optional native Streamlit `AppTest` is present in CI but is skipped in this sandbox because Streamlit cannot be downloaded here;
- browser visual verification, screenshots and Community Cloud deployment remain external acceptance checks until a standalone GitHub remote and an installable Streamlit runtime are available;
- the v0.4 implementation itself is frozen rather than left open for further micro-patches.

## 0.3.0 — Iteration 3: Optimization + Carbon + Explainability

### Added

- sparse 8,760-hour linear sizing/dispatch optimization;
- optimal PV, battery energy and battery power capacities;
- cyclic annual SOC condition;
- PV-only battery charging and load-only battery discharge;
- configurable site/model capacity bounds;
- exact residual grid-import and PV-export formulation;
- HiGHS solver backend through SciPy `linprog`;
- dual-simplex strategy for economic optimum and interior-point strategy for carbon-constrained annual cases;
- technology-specific annualized CAPEX/OPEX objective;
- post-processed project NPV and simple payback;
- explicit CO2-reduction constraint and binding/slack detection;
- solver-state normalization (`optimal`, `infeasible`, `unbounded`, `solver_error`);
- cost-decarbonization frontier with exact reuse of non-binding economic optimum;
- deterministic one-at-a-time sensitivity analysis;
- on-demand sensitivity-family API for the future Streamlit interface;
- battery CAPEX break-even transition helper;
- 58-metric centralized explainability registry for Iteration 4 help icons;
- deterministic result/scenario comparison insights;
- `data/demo/optimization_assumptions.json`;
- Golden Case v3 economic optimum and binding-carbon regression;
- `docs/OPTIMIZATION_GUIDE.md`.

### Performance/architecture

- eliminated redundant hourly import/export decision variables, reducing annual LP size from `6n+3` to `4n+3` variables without changing physical results;
- avoided repeated solves for carbon targets already met by the economic optimum;
- avoided redundant re-optimization when only a constant grid-emissions factor changes with no carbon constraint.

### Preserved

- Golden Case v1 remains frozen (`0.1.0`, `golden-v1`);
- Golden Case v2 remains frozen (`0.2.0`, `golden-v2`);
- hourly dataset version remains `demo-v1`;
- engine remains offline with no runtime HTTP/API dependency.

### Explicitly not included

Streamlit UI, public deployment, real Castellón ceramic assumptions, thermal technologies, hydrogen, Monte Carlo and generative-AI explanations.

## 0.2.0 — Iteration 2: 8,760h PV + Battery

### Added

- offline PV generation module using installed capacity and normalized hourly capacity factor;
- battery specification with energy/power limits, AC-side efficiencies and SOC bounds;
- deterministic PV-first annual dispatch;
- explicit battery losses and SOC trajectory;
- annual physical/economic/emissions summary;
- Golden Case v2.

### Preserved

- Golden Case v1;
- `demo-v1` datasets;
- offline runtime.

## 0.1.0 — Iteration 1: Energy Engine

### Added

- package structure and version identifiers;
- strict hourly dataset validation;
- deterministic 8,760-hour synthetic demo datasets;
- grid-only baseline;
- annual energy/cost/emissions calculations;
- NPV, payback and CRF helpers;
- tests, CI definition and initial documentation.
