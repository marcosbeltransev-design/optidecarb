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

Use the Castellón case: about 4,804 MWh/year PV generation, about 4,559 MWh/year used onsite, 15,000 MWh/year load and about 10,441 MWh/year grid import.

```text
Self-consumption = PV used onsite / PV generation
Self-sufficiency = (Load - grid import) / Load
```

A plant can consume almost every solar MWh it generates but still buy most of its annual electricity from the grid.

---

## Exercise 3 — Battery: follow three hours by hand

### Data

```text
Load [kWh]:  10, 10, 10
PV [kWh]:     0, 20,  0
Charge efficiency:    90%
Discharge efficiency: 90%
Initial SOC: 0 kWh
```

Expected result:

```text
Charge input:       10.0 kWh
SOC increase:        9.0 kWh
Battery discharge:   8.1 kWh
Hour-3 grid import:  1.9 kWh
Total losses:        1.9 kWh
```

The two 90% efficiencies compound. Energy is not created by storage; some is lost during conversion.

---

## Exercise 4 — WACC, CRF and annualized CAPEX

Follow:

```text
WACC → CRF → annualized CAPEX → objective function → optimal sizing
```

Use a €1,000,000 asset, 25-year life and 5% WACC. At 5% / 25 years, CRF is about 0.071/year, so €1M corresponds to roughly €71k/year equivalent capital cost.

---

## Exercise 5 — What does “economic optimum” actually mean?

Classify PV capacity, WACC, battery SOC limit, total annualized cost and carbon target as decision variable, input parameter, constraint or objective.

“Optimal” means the minimum of the stated objective **inside the stated model**, not “best in every real-world sense.”

---

## Exercise 6 — Carbon constraint: 20% vs 40%

The Castellón economic optimum already reduces modeled electrical CO₂ by about 30.4%. A 20% minimum target is non-binding. At 40%, the carbon requirement becomes stricter than the unconstrained optimum, so the design changes and storage enters.

---

## Exercise 7 — Sensitivity: one change at a time

Before running each experiment, predict the direction:

1. Electricity price +20%.
2. PV CAPEX +20%.
3. WACC 5% → 6%.
4. Battery CAPEX −20%.

Sensitivity is a **what-if analysis**, not a forecast or probability distribution.

---

## Exercise 8 — Interpret the Castellón case like an engineer

Evidence chain:

```text
ASCER → sector context
OMIE → wholesale electricity-price proxy
PVGIS → solar calibration
Red Eléctrica → grid CO₂ factor
IDAE / IRENA → cost plausibility
Explicit assumptions → representative plant
Validated engine → conditional result
```

A good answer separates **evidence**, **derived values**, **proxies**, **model assumptions** and **results**.

OptiDecarb is a **pre-feasibility** tool. The correct decision is whether a scenario is promising enough to justify real plant data, quotations and detailed engineering — not whether construction should start immediately.

---

## v1.2 industry reflection — after the technical exercises

After completing the calculations, do not stop at the numerical answer. For each exercise, ask:

1. **Where would this input come from at a real company?**
2. **What quick sanity check could catch a bad value?**
3. **Which assumption could change the conclusion?**
4. **Who in the company would care about this result — operations, finance, sustainability, maintenance or management?**
5. **What would you ask for next before making a stronger recommendation?**

Example for the battery exercise:

> Technical result: a 4 MWh / 2 MW battery has roughly 2 hours of duration before efficiency and SOC limits.
>
> Industry question: if a supplier only gives you “4 MWh”, ask for the power rating too. Energy capacity alone does not tell you how fast the battery can respond.

Then continue with the in-app **Junior Engineer Lab** or [`JUNIOR_ENGINEER_GUIDE.md`](JUNIOR_ENGINEER_GUIDE.md).
