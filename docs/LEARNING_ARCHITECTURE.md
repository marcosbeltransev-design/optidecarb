# OptiDecarb v1.3.2 — Industrial Energy Learning Architecture

## Purpose

OptiDecarb is not intended to be a generic junior-career course. Its main educational purpose is to help an engineering student learn **industrial electrical energy analysis** by using a real 8,760-hour model as a laboratory.

The learning chain is:

**industrial energy data → baseline → load/profile reasoning → PV/BESS → economics → optimization → CO₂ → sensitivity → site/project validation → professional energy recommendation**.

General professional skills appear only when they are attached to a real energy task: asking for interval data, reviewing a PV/BESS quotation, preparing an energy site visit, reconciling a price proxy with a real bill, or explaining an energy recommendation to management.

## Core learning areas

1. **Energy fundamentals** — MW vs MWh, interval energy, prices and CO₂ units.
2. **Industrial energy data** — missing intervals, duplicates, timezone/calendar issues, spikes, flatlines, mixed units and meter/sign conventions.
3. **Load and metering** — annual MWh, average/peak MW, load factor, meter boundary, import/export and interval meaning.
4. **PV and battery** — MWp, yield, coincidence, exports, self-consumption, MW/MWh, duration, SOC and efficiency.
5. **Energy modelling** — hourly balance, assumptions, traceability and model boundaries.
6. **Energy economics and tariffs** — wholesale proxy vs real industrial bill, CAPEX/OPEX, WACC, NPV, payback and sensitivity.
7. **Optimization and sensitivity** — objective, constraints, binding limits and robustness of the recommendation.
8. **Decarbonization** — electrical baseline, grid factor, targets and the electricity-only scope.
9. **Evidence and uncertainty** — distinguish measured site data, public evidence, supplier information, proxies and assumptions; use sensitivity to decide what evidence deserves better validation.
10. **Energy project development** — screening → site validation → feasibility → EPC quotation → detailed engineering/commissioning.
11. **Site and operations** — meters, transformer/SLD awareness, production schedule, shutdowns, export/grid constraints and maintenance access.
12. **Energy suppliers and communication** — comparable PV/BESS scope, guarantees, exclusions and clear professional recommendations.

## Active-learning method

The v1.3.x layer changes **how** the validated content is learned rather than expanding the mathematical scope.

For important concepts the preferred loop is:

**estimate → predict → calculate/run → compare → explain why → decide what to check next**.

The student should progressively be able to say:

**I have seen this → I understand it → I can estimate it → I can detect when it is wrong → I can explain why → I can support a better energy decision.**

### v1.3.1 — model intuition

Implemented through:

- formula → units → intuition cards;
- predict-before-reveal sensitivity exercises;
- load-profile reading with the committed 8,760-hour Castellón dataset;
- a load-duration curve with an explicit warning about lost chronology;
- one-day and one-hour electrical-balance reconstruction;
- a visual CO₂ target frontier showing the transition from non-binding to binding constraints;
- MODEL KNOWS / MODEL ASSUMES / MODEL DOES NOT KNOW cards;
- screening-versus-feasibility comparisons;
- one smaller unseen transfer case to test whether reasoning transfers beyond Castellón;
- session-only review items for concepts answered incorrectly.

### v1.3.2 — evidence judgement

The next layer adds three recurring habits:

**DIAGNOSE BEFORE CLEANING**  
A suspicious energy series is not automatically bad data. Missing intervals, duplicated timestamps, flatlines, unexpected scale and negative net-meter values must first be interpreted in their meter and operational context.

**TRACE BEFORE TRUSTING**  
Important results should be reversible through an evidence chain:

**source / evidence → proxy or assumption → calculation / model input → validated result → decision use**.

The student should be able to answer both:

- “Where did this number come from?”
- “What upstream assumption could make this recommendation change?”

**USE SENSITIVITY TO IMPROVE EVIDENCE**  
Sensitivity is not only a chart of model outputs. It is a way to decide what to validate next. If the PV recommendation moves materially when an electricity-price or CAPEX assumption changes, a real tariff or comparable EPC quotation may be more valuable than adding more numerical precision elsewhere.

The current sensitivity-priority visual uses specific frozen one-at-a-time tests. Their perturbations are not normalized to equal uncertainty, so it must **not** be interpreted as a global statistical ranking of parameter importance.

## Evidence-confidence ladder

OptiDecarb teaches a qualitative evidence hierarchy without inventing confidence percentages:

1. **Measured site data** — highest site relevance when meter boundary and quality are confirmed.
2. **Official / public data** — strong external evidence, but still requires correct boundary and adaptation.
3. **Supplier / EPC data** — useful when technical scope, exclusions and guarantees are comparable.
4. **Proxy / benchmark** — appropriate for screening when clearly labelled as a proxy.
5. **Model assumption** — transparent placeholder to challenge through sensitivity and replace when better evidence becomes available.

This is not a rule that measured data are always correct. A measured series can still have the wrong meter boundary, timestamps, sign convention or units.

## Semantic visual language

The color system is semantic, not decorative:

- **Blue** — data / concept;
- **Green** — validated / correct;
- **Amber** — assumption / item to check;
- **Red** — inconsistency / risk.

Colour must never be the only carrier of meaning; labels and text remain explicit.

## Recurring engineering mental models

- **UNITS FIRST** — do the units physically close?
- **ESTIMATE FIRST** — what rough MW/MWh/€/tCO₂ answer should I expect?
- **FOLLOW THE ENERGY** — where does each MWh go?
- **KNOW THE METER BOUNDARY** — what exactly is being measured?
- **CHECK THE TIME AXIS** — are intervals complete, unique and correctly ordered?
- **WHAT IS THE BASELINE?** — compared with what?
- **FOLLOW THE MONEY** — which cost component is actually changing?
- **TRACE THE NUMBER** — which source, proxy or assumption created it?
- **WHAT IS NOT MODELLED?** — site, tariff, operational or technical constraints?
- **WHAT WOULD CHANGE MY DECISION?** — which sensitivity matters?
- **WHAT EVIDENCE SHOULD I IMPROVE NEXT?** — where would better data most reduce decision uncertainty?
- **IS THE RESULT NEAR A BOUND?** — is a model limit shaping the optimum?
- **IS THE PRECISION REAL?** — does the project stage support those decimals?

## Why the visualizations exist

Charts are included only where they help an engineering idea become intuitive.

- **Representative-day load/PV chart:** learn coincidence and industrial-load shape.
- **Load-duration curve:** learn load factor and demand distribution, while understanding why chronology is still required.
- **One-day supply chart:** reconstruct load = PV-to-load + grid import at the battery-free economic optimum.
- **CO₂ frontier:** see when an emissions constraint actually starts changing the optimized system.
- **Forensic snippets:** practise spotting timestamp, scale, sign and data-lineage issues before applying a cleaning rule.
- **Sensitivity-to-evidence chart:** turn observed scenario movement into a practical next-data request while retaining the limits of one-at-a-time sensitivity.
- **Trace-the-number cards:** make provenance and assumption chains visible instead of hiding them behind a final metric.

The visual layer reads committed offline case data, illustrative teaching snippets, or frozen regression outputs. It does not add a second calculation engine inside the UI.

## What OptiDecarb deliberately does not teach in depth

OptiDecarb can introduce the questions, but it does not replace real experience in:

- live industrial electrical work and safety;
- detailed single-line/electrical design;
- structural roof assessment;
- detailed grid-connection studies;
- full tariff/billing engineering;
- real supplier negotiation and contracting;
- construction supervision and commissioning responsibility;
- full Measurement & Verification programmes.

These limits are intentional. The application is a **screening and learning environment**, not a substitute for site-specific engineering.

## Castellón as the capstone

The representative ceramic case remains the main capstone because it forces the student to connect public evidence, representative assumptions, a full-year load, PV resource, price proxy, techno-economics, optimization, carbon targets, sensitivity and professional limitations.

The final learning objective is to be able to answer:

1. What is the energy objective?
2. What data do I need?
3. Can I trust the load and meter data?
4. What simple estimates should I calculate first?
5. What is the electrical baseline?
6. Which assumptions are proxies or benchmarks?
7. Where did each important result come from?
8. Why does the model select this PV/BESS configuration?
9. Which assumptions can change the recommendation?
10. Which missing piece of evidence should I improve first?
11. What site/tariff/grid facts are still unknown?
12. What should the company do next?

## Transfer beyond Castellón

A second, deliberately smaller teaching case is included to test transfer rather than to create another full case study. Its purpose is to make the student use load factor, PV yield, hourly-profile reasoning and uncertainty on a different industrial context without being able to copy the Castellón conclusion.
