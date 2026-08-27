# Industrial Energy Lab — From Zero to Understanding the Model

This guide is the fastest route from basic engineering knowledge to understanding **why Industrial Energy Lab behaves the way it does**. For active practice, pair it with [`STUDENT_LAB.md`](STUDENT_LAB.md).

## 1. Start with units: MW is not MWh

**Power** answers “how fast is energy being used or delivered?” Units: kW or MW.

**Energy** answers “how much electricity over time?” Units: kWh or MWh.

```text
5 MW × 3 h = 15 MWh
4 MWh / 2 MW = 2 h
```

Think of the first relation as a dimensional sanity check: `MW × h = MWh`.

**Common mistake:** saying “the factory consumes 2 MW per year.” MW is power, not annual energy.

**Mini question:** can a 2 MW / 4 MWh battery discharge at 2 MW for roughly four hours? **No — roughly two hours before efficiency/SOC limits.**

## 2. Why 8,760 hours?

A non-leap year has `24 × 365 = 8,760` hours. IEL models the full year because annual averages cannot tell us **when** load, PV generation and electricity prices occur.

Timing matters for:

- direct PV consumption;
- exports;
- battery charge/discharge;
- State of Charge (SOC);
- hourly electricity purchases.

The UI may display a week for readability, but the optimizer still solves all 8,760 hours.

## 3. PV — Photovoltaic

**PV capacity** is power: kW/MW. **PV generation** is energy: kWh/MWh.

```text
PV generation[t] = PV capacity × capacity factor[t] × interval
```

**CF — Capacity Factor** compares actual output with continuous operation at rated power. It is **not** panel conversion efficiency.

Why does the optimum not install infinite PV? The first PV capacity often displaces valuable grid purchases. With more PV, additional generation can increasingly occur when the site already has enough solar electricity, increasing exports and reducing the **marginal value** of further PV.

## 4. Battery: MW, MWh and SOC

A battery needs two sizes:

- **energy capacity [MWh]** — how much it can store;
- **power capacity [MW]** — how quickly it can charge/discharge.

**SOC — State of Charge** is stored energy at a particular time.

IEL models charge/discharge efficiency. Storage shifts energy; it does not create it.

### Cyclic SOC

The annual optimization requires the battery to end with the same SOC condition it started with. This prevents free boundary energy — for example, starting full without paying for that energy or ending empty simply to improve the objective.

**Student Lab:** Exercise 3 walks through the exact 3-hour battery example used by the physical tests.

## 5. Grid and baseline

After direct PV and battery discharge, remaining demand is imported from the grid. Surplus PV can be exported.

The **baseline** is the reference case used for comparison. In IEL it is grid-only electricity supply for the same load and price series.

Savings, emissions reduction and abatement cost only make sense relative to a clearly defined baseline.

## 6. Economics: follow the chain

### CAPEX vs OPEX

**CAPEX — Capital Expenditure:** upfront investment in long-lived assets.

**OPEX — Operating Expenditure:** recurring annual operating/maintenance cost.

A €2M PV system is not €2M/year.

### WACC

**WACC — Weighted Average Cost of Capital** is the financing/discount rate used by IEL. Spanish clarification: *coste medio ponderado del capital*.

It matters through this chain:

```text
WACC ↑
  ↓
CRF ↑
  ↓
Annualized CAPEX ↑
  ↓
Capital-intensive options can become less attractive
```

This is a ceteris-paribus relationship, not a universal prediction of the exact optimal size.

### CRF

**CRF — Capital Recovery Factor** converts upfront CAPEX into equivalent annual capital cost:

```text
CRF = r(1+r)^n / ((1+r)^n - 1)
Annualized CAPEX = CAPEX × CRF
```

At 5% WACC and 25 years, CRF is about `0.071/year`; a €1M investment is therefore roughly €71k/year of equivalent annual capital cost.

### NPV

**NPV — Net Present Value**:

```text
NPV = -initial CAPEX + Σ cash_flow[t] / (1+r)^t
```

- NPV > 0: modeled discounted benefits exceed CAPEX under the assumptions;
- NPV < 0: they do not.

Positive NPV **does not mean “build the project.”** IEL is pre-feasibility.

### Payback

**Simple payback = initial CAPEX / annual operating cash benefit.** It is intuitive but ignores time value of money. NPV and payback answer different questions.

**Student Lab:** Exercise 4 connects WACC → CRF → annualized CAPEX.

## 7. Optimization without the black box

**LP — Linear Programming** chooses continuous decision variables while respecting linear constraints.

### Decision variables
What the optimizer may choose, such as:

- PV capacity;
- battery MWh;
- battery MW;
- hourly dispatch.

### Parameters
Inputs the optimizer does not choose, such as WACC or PV unit CAPEX.

### Objective
IEL minimizes equivalent **annualized system cost**:

```text
annualized PV + battery cost
+ OPEX
+ grid purchases
- export revenue
```

### Constraints
Rules the optimizer cannot break: hourly energy balance, PV availability, battery power, SOC bounds, model/site capacity bounds and optional carbon target.

**Economic optimum** means minimum objective value **inside these assumptions and constraints**. It does not mean universally best real-world design.

## 8. Binding and infeasible

A **binding constraint** is active at the solution. If the unconstrained economic optimum already reduces CO₂ by about 30%, a 20% minimum target does not restrict it; a 40% target can.

**Infeasible** means there is no solution satisfying all current constraints. It is different from solver error.

## 9. Self-consumption vs self-sufficiency

These use different denominators.

```text
Self-consumption = PV used onsite / PV generated
Self-sufficiency = (Load - grid imports) / Load
```

Using the frozen Castellón result:

```text
Self-consumption ≈ 4,559 / 4,804 ≈ 94.9%
Self-sufficiency ≈ (15,000 - 10,441) / 15,000 ≈ 30.4%
```

So almost all PV can stay onsite while most annual demand is still supplied by the grid.

## 10. Carbon and abatement cost

IEL v1.1 models electrical grid-related emissions as:

```text
CO₂ = grid import [MWh] × grid emission factor [kgCO₂/MWh] / 1,000
```

Unit check: `MWh × kgCO₂/MWh = kgCO₂`; divide by 1,000 for tonnes.

A **carbon target** is a minimum reduction versus baseline. It is not renewable share.

**Abatement cost**:

```text
(Scenario annualized cost - baseline annual cost) / avoided tCO₂
```

- negative €/tCO₂: emissions reduction also lowers modeled annualized cost;
- positive €/tCO₂: deeper reduction requires extra annualized cost.

## 11. Sensitivity is an experiment, not a forecast

Sensitivity changes one assumption and re-solves the model. It helps identify which assumptions matter and whether a conclusion is robust.

It is **not** Monte Carlo, a probability statement or proof of universal causality.

Use conditional language: “under this model and these assumptions...”

## 12. Evidence, proxies and assumptions

- **Public data:** external published evidence.
- **Derived public value:** transparently calculated from published values.
- **Proxy:** approximation when the exact facility value is unavailable.
- **Model assumption:** explicit screening choice.
- **Real plant data:** facility-specific measurements/contracts — not used for the representative Castellón case.

A model assumption is not automatically a random guess: it should be explicit, traceable, modifiable and sensitivity-tested.

## 13. Castellón case: what the result means

The representative case uses a **15 GWh/year rounded scale** consistent with public ceramic-sector order of magnitude; it is not “the average ceramic factory.”

The frozen economic optimum is roughly 2.97 MW PV with zero battery. This is legitimate: storage adds value only if shifted-energy savings justify its annualized CAPEX and conversion losses.

The economic optimum already reduces modeled electrical CO₂ by about 30%. At a 40% minimum target, the constraint becomes binding; more PV is required and storage enters the least-cost feasible solution.

Read [`../cases/ceramic_castellon/CASE_STUDY.md`](../cases/ceramic_castellon/CASE_STUDY.md) for the full evidence chain.

## 14. What IEL does not know

IEL does not know the real plant's:

- roof/land geometry;
- electrical single-line diagram;
- network constraints;
- tariff/hedging contract;
- supplier quotations;
- battery degradation/replacement plan;
- financing agreement;
- kiln/dryer gas demand;
- future market prices.

That is why IEL is **pre-feasibility**: it asks whether a scenario justifies more detailed study.

## 15. How to study

1. Read this guide once.
2. Complete [`STUDENT_LAB.md`](STUDENT_LAB.md) without looking at the suggested answers first.
3. Use the Streamlit **Learning Lab**: predict → run → compare → explain.
4. Study [`OPTIMIZATION_GUIDE.md`](OPTIMIZATION_GUIDE.md) for the equations.
5. Read the Castellón case study.
6. Use [`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md) and answer aloud.
