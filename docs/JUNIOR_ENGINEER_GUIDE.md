# Junior Engineer Guide

## What this guide is for

This guide is not a replacement for real project experience. It is a bridge between university-style exercises and the first questions you may meet in an industrial energy team.

The main habit is simple:

```text
UNDERSTAND THE REQUEST
→ ASK FOR DATA
→ CHECK THE DATA
→ WRITE DOWN ASSUMPTIONS
→ DO SIMPLE SANITY CHECKS
→ RUN THE SCREENING
→ CHALLENGE THE RESULT
→ TEST SENSITIVITY
→ COMMUNICATE CLEARLY
→ RECOMMEND THE NEXT STEP
```

A useful junior engineer does not need to know everything. They need to know what they know, what they do not know and what to check next.

## 1. Understand the request before modelling

A request such as “we want 5 MW of solar” already contains a proposed solution. Before accepting it, ask what problem the company is trying to solve.

Useful questions:

- Is the main objective electricity-cost reduction, CO₂ reduction, resilience or something else?
- Why 5 MW?
- What is the plant electricity demand and production schedule?
- Is surplus export allowed and at what value?
- Is there enough roof or land?
- Are there important operational constraints?

**Junior lesson:** Do not optimize the requested solution before you understand the real problem.

## 2. Ask for data like an engineer

For an early industrial PV/battery study, useful data may include:

- 12–24 months of interval electricity data;
- recent electricity invoices;
- electricity contract or tariff information;
- production calendar and planned shutdowns;
- roof / land availability;
- grid connection and export restrictions;
- existing electrical infrastructure;
- corporate investment assumptions such as WACC;
- supplier quotations when the project is mature enough.

Ask where every important number came from. Classify it as measured, public, derived, proxy or assumption.

## 3. Check the data before building a complex model

Simple checks often catch serious problems.

### Energy versus power

If annual consumption is 15 GWh/year:

`15,000 MWh / 8,760 h ≈ 1.71 MW average load`

If somebody also reports a 0.9 MW peak, the two numbers cannot describe the same site boundary and period.

### Time-series checks

For a non-leap hourly year:

- expect 8,760 timestamps;
- check that timestamps are ordered;
- check there are no duplicates;
- understand timezone and daylight-saving treatment;
- investigate missing or impossible values;
- check units before converting anything.

### Physical sanity checks

- average power ≤ peak power;
- battery duration ≈ MWh / MW;
- PV capacity is MW, annual PV production is MWh;
- self-consumption and self-sufficiency must be between 0% and 100%;
- SOC must remain inside battery capacity limits;
- night-time PV should not be positive unless there is a clear data definition that explains it.

## 4. Keep an assumptions log

An **assumptions log** is a simple record of important assumptions and their sources.

For each important assumption, record:

- the value;
- the unit;
- the source;
- whether it is measured, derived, proxy or assumption;
- why it is reasonable;
- who should confirm it;
- whether sensitivity should be tested.

Example:

| Assumption | Value | Type | Why used | What should replace it later? |
|---|---:|---|---|---|
| WACC | 5% | Model assumption | Screening value | Company finance assumption |
| Electricity price | OMIE-based | Proxy | Public wholesale reference | Actual contract / tariff |
| PV CAPEX | Public benchmark | Proxy | Early cost plausibility | EPC quotation |

## 5. Know what a screening can and cannot say

A screening can help answer:

- Is the opportunity large enough to deserve more work?
- Which technology appears useful under the current assumptions?
- Which assumptions drive the result?
- What rough scale should be investigated next?

A screening should **not** be presented as:

- a final construction design;
- a guaranteed saving;
- an investment approval;
- a substitute for site, grid, contract or supplier validation.

## 6. Challenge the model result

Do not stop at “the optimizer says X”. Ask:

- Does the result make physical sense?
- Is the optimum exactly at a capacity bound?
- Is a large share of PV exported?
- Does a small CAPEX or price change reverse the recommendation?
- Are important value streams missing from the model?
- Is a proxy likely to change the economics materially?

### Example: 2.972 MW PV

The mathematical output can be 2.972 MW.

Better professional communication:

> Around 3 MWp appears economically attractive under the current screening assumptions.

A next-stage team might compare practical layouts around that region. Do not claim a practical range is mathematically optimal unless it has actually been tested.

## 7. Understand why different departments ask different questions

### Operations

They may ask about shutdowns, reliability, safety, production schedules and equipment access.

### Finance

They may ask about CAPEX, annual saving, NPV, payback, sensitivity and downside scenarios.

### Sustainability

They may ask about the emissions baseline, emission factor, accounting boundary and audit trail.

### Maintenance

They may ask what equipment the site will own, who services it, what the warranty covers and what fails.

### Management

They may ask what decision is needed, what the benefit is, what the main risk is and what should happen next.

**Junior lesson:** The same technically correct result must be communicated differently depending on the audience.

## 8. Ask suppliers questions, not just prices

A supplier quotation should make inclusions, exclusions and assumptions clear.

For PV / EPC, ask about:

- modules, inverters and structures;
- electrical works and grid connection;
- engineering and permitting;
- commissioning;
- warranties;
- O&M;
- performance guarantees;
- contingency and exclusions.

For a battery, also ask about:

- power rating [MW];
- energy capacity [MWh];
- round-trip efficiency;
- usable SOC window;
- degradation;
- dispatch strategy;
- warranty and cycling conditions.

## 9. Communicate uncertainty professionally

Useful phrases:

- “Based on the available data...”
- “Under the current assumptions...”
- “The main uncertainty is...”
- “We would need to validate...”
- “This should be treated as a screening result.”
- “I would not conclude that yet because...”
- “The model does not currently include...”
- “The next practical step would be...”

Saying “I do not know yet” can be a good engineering answer if you explain what information is missing and how you would obtain it.

## 10. Match recommendation strength to project maturity

A simple maturity path is:

`Curiosity → Screening → Pre-feasibility → Feasibility → Budget quotation → Investment approval → Detailed engineering / EPC → Construction → Commissioning → Operation`

The further a project moves, the more real data, site detail, supplier input and formal review should replace early assumptions.

## 11. A good 30-second result

A junior engineer should be able to say:

> Under the current assumptions, the screening suggests that around 3 MWp of PV could be economically attractive for the representative Castellón case. Battery storage is not selected in the economic optimum, but it becomes useful under stricter carbon targets. The main next step is to validate the real tariff, site constraints and supplier pricing before treating the result as investment-ready.

## Final habit

Good engineering is not only finding answers. It is also knowing:

- what the model does not know;
- what data are missing;
- which assumptions matter;
- what could make the conclusion wrong;
- when more detailed work is required.
