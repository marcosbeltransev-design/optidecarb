# OptiDecarb — Student Learning Lab

A 30–60 minute guided practice for an engineering student who understands basic mathematics but is new to energy-system optimization.

**Recommended rule:** predict first, calculate second, run the model third, explain last.

> Technical terms remain in English because that is how you will see them in engineering work and interviews. Short Spanish clarifications are included where they prevent common confusion.

---

## Exercise 1 — MW vs MWh

### Objective
Distinguish **power (MW)** from **energy (MWh)**.

### Steps
1. Imagine a load of 5 MW sustained for 3 hours.
2. Use `Energy = Power × Time`.
3. Now imagine a 4 MWh / 2 MW battery.

### Questions
1. How much energy does the 5 MW load use in 3 h?
2. Ignoring efficiency and SOC limits, how long can the 4 MWh battery discharge at 2 MW?

### Expected observation
`5 MW × 3 h = 15 MWh` and `4 MWh / 2 MW = 2 h`.

### Explanation
MW is a **rate**; MWh is a **quantity**. In Spanish: MW is *potencia* and MWh is *energía*. Confusing them makes battery sizing and annual-load calculations meaningless.

---

## Exercise 2 — PV, load and self-consumption

### Objective
Understand why PV capacity and PV generation are different, and why **self-consumption** is not **self-sufficiency**.

### Steps
1. Use the Castellón case result: about 4,804 MWh/year PV generation.
2. About 4,559 MWh/year is used onsite.
3. Annual site load is 15,000 MWh/year and grid import is about 10,441 MWh/year.

### Questions
1. Calculate PV self-consumption.
2. Calculate electrical self-sufficiency.
3. Why can one be about 95% while the other is only about 30%?

### Expected observation
Self-consumption follows **PV energy**; self-sufficiency follows **site demand**.

### Explanation

```text
Self-consumption = PV used onsite / PV generation
Self-sufficiency = (Load - grid import) / Load
```

A plant can consume almost every solar MWh it generates but still buy most of its annual electricity from the grid.

---

## Exercise 3 — Battery: follow three hours by hand

### Objective
Understand SOC — **State of Charge** — and battery losses without treating the model as a black box.

### Data

```text
Load [kWh]:  10, 10, 10
PV [kWh]:     0, 20,  0
Charge efficiency:    90%
Discharge efficiency: 90%
Initial SOC: 0 kWh
```

### Steps
1. Hour 1: no PV. Supply the 10 kWh load.
2. Hour 2: PV = 20 kWh and load = 10 kWh. Find surplus and stored energy.
3. Hour 3: use the stored energy to serve load.

### Questions
- How much energy reaches SOC in hour 2?
- How much can the battery deliver in hour 3?
- How much grid import remains?
- What are total battery losses?

### Expected observation

```text
Charge input:       10.0 kWh
SOC increase:        9.0 kWh
Battery discharge:   8.1 kWh
Hour-3 grid import:  1.9 kWh
Total losses:        1.9 kWh
```

### Explanation
The two 90% efficiencies compound. Energy is not created by storage; some is lost during conversion.

---

## Exercise 4 — WACC, CRF and annualized CAPEX

### Objective
Follow the complete chain:

```text
WACC → CRF → annualized CAPEX → objective function → optimal sizing
```

### Definitions
- **WACC — Weighted Average Cost of Capital:** financing/discount rate used in OptiDecarb. Spanish clarification: *coste medio ponderado del capital*.
- **CRF — Capital Recovery Factor:** converts an upfront investment into an equivalent annual capital cost.
- **CAPEX — Capital Expenditure:** upfront investment.

### Steps
Use a €1,000,000 asset, 25-year life and 5% WACC.

```text
CRF = r(1+r)^n / ((1+r)^n - 1)
Annualized CAPEX = CAPEX × CRF
```

### Questions
1. What is the CRF?
2. What is the equivalent annual capital cost?
3. Predict what happens if WACC rises to 6%.

### Expected observation
At 5% / 25 years, CRF is about 0.071/year, so €1M corresponds to roughly €71k/year equivalent capital cost. A higher WACC raises the CRF.

### Explanation
The optimizer compares grid cost and capital-intensive technologies in the same `€/year` unit. A higher financing rate can therefore change the cost-optimal PV/battery sizing even when physical performance is identical.

---

## Exercise 5 — What does “economic optimum” actually mean?

### Objective
Understand **LP — Linear Programming**, decision variables, constraints and the objective function.

### Steps
Identify each item:

- PV capacity
- WACC
- battery SOC limit
- total annualized cost
- carbon target

Classify each as a **decision variable**, **input parameter**, **constraint** or **objective**.

### Expected observation
- PV capacity → decision variable.
- WACC → input parameter.
- SOC limit → constraint.
- total annualized cost → objective.
- carbon target → optional constraint parameter.

### Explanation
“Optimal” means the minimum of the stated objective **inside the stated model**, not “best in every real-world sense.” OptiDecarb does not know roof geometry, real supplier quotations, detailed grid connection constraints or the plant's actual financing contract.

---

## Exercise 6 — Carbon constraint: 20% vs 40%

### Objective
Understand a **binding constraint**.

### Steps
1. The Castellón economic optimum already reduces modeled electrical CO₂ by about 30.4%.
2. Apply a 20% minimum target.
3. Apply a 40% minimum target.

### Questions
- Which target is binding?
- Why does the 20% target not change the design?
- Why can storage appear at 40%?

### Expected observation
20% is non-binding because the economic optimum already exceeds it. At 40%, the carbon requirement becomes stricter than the unconstrained optimum, so the feasible solution space shrinks and the design changes.

### Explanation
In the frozen case, deeper import reduction requires more PV. More PV can create more surplus in some hours, so storage gains value as a way of shifting that energy to later demand.

---

## Exercise 7 — Sensitivity: one change at a time

### Objective
Learn what deterministic sensitivity does — and does **not** do.

### Steps
Before running each experiment, predict the direction:

1. Electricity price +20%.
2. PV CAPEX +20%.
3. WACC 5% → 6%.
4. Battery CAPEX −20%.

### Questions
- Which changes make PV more attractive?
- Does 20% cheaper battery automatically make storage optimal?
- Which result surprised you?

### Expected observation
In the frozen Castellón case the guided experiments currently produce:

| Experiment | Observed result |
|---|---|
| Electricity price +20% | optimal PV ~2.97 → ~3.19 MW |
| PV CAPEX +20% | optimal PV ~2.97 → ~2.79 MW |
| WACC 5% → 6% | optimal PV ~2.97 → ~2.87 MW |
| Battery CAPEX −20% | battery remains 0 MWh / 0 MW |

These are **conditional model results**, not universal engineering laws.

The dedicated PV-oversizing experiment increases fixed PV capacity by 50% above the economic optimum. In the frozen case, grid imports fall by about 886 MWh/year, but PV self-consumption falls from ~94.9% to ~75.6% and exports rise from ~245 to ~1,761 MWh/year. This is a practical illustration of diminishing marginal onsite value.

### Explanation
Sensitivity is a **what-if analysis**, not a forecast or probability distribution. Change one input at a time so the comparison stays interpretable.

---

## Exercise 8 — Interpret the Castellón case like an engineer

### Objective
Move from calculations to a defensible pre-feasibility conclusion.

### Evidence chain

```text
ASCER → sector context
OMIE → wholesale electricity-price proxy
PVGIS → solar calibration
Red Eléctrica → grid CO₂ factor
IDAE / IRENA → cost plausibility
Explicit assumptions → representative plant
Validated engine → conditional result
```

### Questions
1. Where does the 15 GWh/year scale come from?
2. Why is OMIE not the real industrial bill?
3. Why is the PV profile described as PVGIS-calibrated rather than raw PVGIS hourly data?
4. Why is battery = 0 a legitimate economic result?
5. Does a positive NPV mean “build now”?
6. Does this scenario justify further detailed study?

### Expected observation
A good answer separates **evidence**, **derived values**, **proxies**, **model assumptions** and **results**.

### Explanation
OptiDecarb is a **pre-feasibility** tool. The correct decision is whether a scenario is promising enough to justify real plant data, quotations and detailed engineering — not whether construction should start immediately.

---

# Suggested answers / self-check

1. **MW vs MWh:** 15 MWh and 2 h.
2. **Self-consumption vs self-sufficiency:** approximately 95% vs 30%; different denominators answer different questions.
3. **Battery:** 9 kWh stored, 8.1 kWh delivered, 1.9 kWh grid import, 1.9 kWh total losses.
4. **WACC/CRF:** higher WACC raises equivalent annual capital cost, all else equal.
5. **Optimization:** distinguish decisions, parameters, constraints and objective.
6. **Carbon:** 20% non-binding; 40% binding in the frozen Castellón case.
7. **Sensitivity:** use the actual solver result and conditional language; do not turn one scenario into a universal law.
8. **Castellón:** treat the result as a traceable screening case, not measured plant truth.

## Continue studying

1. Re-read [`BEGINNER_GUIDE.md`](BEGINNER_GUIDE.md) for concepts you missed.
2. Use [`OPTIMIZATION_GUIDE.md`](OPTIMIZATION_GUIDE.md) for the mathematical model.
3. Read [`../cases/ceramic_castellon/CASE_STUDY.md`](../cases/ceramic_castellon/CASE_STUDY.md) for evidence and assumptions.
4. Finish with [`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md) and explain the project aloud without reading.
