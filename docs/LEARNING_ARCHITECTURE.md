# OptiDecarb v1.3.1 — Industrial Energy Learning Architecture

## Purpose

OptiDecarb is not intended to be a generic junior-career course. Its main educational purpose is to help an engineering student learn **industrial electrical energy analysis** by using a real 8,760-hour model as a laboratory.

The learning chain is:

**industrial energy data → baseline → load/profile reasoning → PV/BESS → economics → optimization → CO₂ → sensitivity → site/project validation → professional energy recommendation**.

General professional skills appear only when they are attached to a real energy task: asking for interval data, reviewing a PV/BESS quotation, preparing an energy site visit, reconciling a price proxy with a real bill, or explaining an energy recommendation to management.

## Core learning areas

1. **Energy fundamentals** — MW vs MWh, interval energy, prices and CO₂ units.
2. **Industrial energy data** — missing intervals, duplicates, timezone/calendar issues, spikes, flatlines and mixed units.
3. **Load and metering** — annual MWh, average/peak MW, load factor, meter boundary, import/export and interval meaning.
4. **PV and battery** — MWp, yield, coincidence, exports, self-consumption, MW/MWh, duration, SOC and efficiency.
5. **Energy modelling** — hourly balance, assumptions, traceability and model boundaries.
6. **Energy economics and tariffs** — wholesale proxy vs real industrial bill, CAPEX/OPEX, WACC, NPV, payback and sensitivity.
7. **Optimization and sensitivity** — objective, constraints, binding limits and robustness of the recommendation.
8. **Decarbonization** — electrical baseline, grid factor, targets and the electricity-only scope.
9. **Energy project development** — screening → site validation → feasibility → EPC quotation → detailed engineering/commissioning.
10. **Site and operations** — meters, transformer/SLD awareness, production schedule, shutdowns, export/grid constraints and maintenance access.
11. **Energy suppliers and communication** — comparable PV/BESS scope, guarantees, exclusions and clear professional recommendations.

## v1.3.1 active-learning method

The v1.3.1 layer changes **how** the existing content is learned rather than expanding the mathematical scope.

For important concepts the preferred loop is:

**estimate → predict → calculate/run → compare → explain why → decide what to check next**.

This is implemented through:

- formula → units → intuition cards;
- predict-before-reveal sensitivity exercises;
- load-profile reading with the committed 8,760-hour Castellón dataset;
- a load-duration curve with an explicit warning about lost chronology;
- one-day and one-hour electrical-balance reconstruction;
- a visual CO₂ target frontier showing the transition from non-binding to binding constraints;
- MODEL KNOWS / MODEL ASSUMES / MODEL DOES NOT KNOW traceability cards;
- screening-versus-feasibility comparisons;
- one smaller unseen transfer case to test whether reasoning transfers beyond Castellón;
- session-only review items for concepts answered incorrectly.

The color system is semantic, not decorative:

- **Blue** — data / concept;
- **Green** — validated / correct;
- **Amber** — assumption / item to check;
- **Red** — inconsistency / risk.

## Recurring engineering mental models

- **UNITS FIRST** — do the units physically close?
- **ESTIMATE FIRST** — what rough MW/MWh/€/tCO₂ answer should I expect?
- **FOLLOW THE ENERGY** — where does each MWh go?
- **KNOW THE METER BOUNDARY** — what exactly is being measured?
- **WHAT IS THE BASELINE?** — compared with what?
- **FOLLOW THE MONEY** — which cost component is actually changing?
- **WHAT IS NOT MODELLED?** — site, tariff, operational or technical constraints?
- **WHAT WOULD CHANGE MY DECISION?** — which sensitivity matters?
- **IS THE RESULT NEAR A BOUND?** — is a model limit shaping the optimum?
- **IS THE PRECISION REAL?** — does the project stage support those decimals?

## Why the visualizations exist

Charts are included only where they help an engineering idea become intuitive.

- **Representative-day load/PV chart:** learn coincidence and industrial-load shape.
- **Load-duration curve:** learn load factor and demand distribution, while understanding why chronology is still required.
- **One-day supply chart:** reconstruct load = PV-to-load + grid import at the battery-free economic optimum.
- **CO₂ frontier:** see when an emissions constraint actually starts changing the optimized system.

The visual layer reads committed offline case data or uses frozen regression outputs. It does not add a second calculation engine inside the UI.

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
7. Why does the model select this PV/BESS configuration?
8. Which assumptions can change the recommendation?
9. What site/tariff/grid facts are missing?
10. What should the company do next?

## Transfer beyond Castellón

A second, deliberately smaller teaching case is included to test transfer rather than to create another full case study. Its purpose is to make the student use load factor, PV yield, hourly-profile reasoning and uncertainty on a different industrial context without being able to copy the Castellón conclusion.