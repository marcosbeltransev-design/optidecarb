# Optimization Guide — OptiDecarb

This guide explains the Iteration 3 model for an engineering reader who is learning optimization. It is intentionally shorter and more intuitive than `METHODOLOGY.md`.

## 1. What is linear programming?

A linear program (LP) chooses values for **decision variables** while respecting **constraints** and minimizing or maximizing an **objective function**.

OptiDecarb asks:

> Which PV size, battery size and hourly operating schedule give the lowest equivalent annual cost while obeying energy physics and optional CO2 requirements?

All equations in v0.3 are linear, so no binary or nonlinear solver is required.

## 2. Decision variables

A variable is something the solver is allowed to choose.

### Capacity variables

- `PVCapacity [kW]`
- `BatteryEnergy [kWh]`
- `BatteryPower [kW]`

### Hourly operating variables

- PV sent directly to load;
- PV sent to battery;
- battery discharge to load;
- battery SOC.

Grid import and PV export are calculated as residuals once those variables are known.

## 3. Parameters

Parameters are fixed inputs, not decisions. Examples:

- hourly load;
- hourly PV capacity factor;
- hourly purchase price;
- export price;
- CAPEX/OPEX;
- WACC;
- efficiency;
- site capacity bounds;
- carbon target.

Changing a parameter can change the optimal solution. Sensitivity analysis deliberately studies this.

## 4. Constraints

Constraints describe what is physically or logically allowed.

Examples:

```text
PV used onsite + PV sent to battery <= available PV
```

```text
PV used onsite + battery discharge <= site load
```

```text
SOC_min <= SOC <= SOC_max
```

```text
charge <= battery power
```

```text
discharge <= battery power
```

A solution that violates one constraint is not feasible, even if it would be cheap.

## 5. Objective function

The optimizer minimizes:

```text
annualized PV cost
+ annualized battery cost
+ grid purchase cost
- export revenue
```

This is the model's definition of “economic optimum.”

NPV is calculated afterwards. Keeping the annualized objective separate from NPV prevents mixing two different economic frameworks inside the same optimization expression.

## 6. Why annualize CAPEX?

A PV system has a large upfront cost but operates for many years. The capital recovery factor (CRF) converts that upfront investment into an equivalent annual cost using lifetime and WACC.

This lets the LP compare, in the same units (`EUR/year`):

- annualized PV investment;
- annualized battery investment;
- yearly OPEX;
- yearly grid purchases;
- yearly export income.

## 7. What is the economic optimum?

It is the cheapest solution among all physically feasible solutions when no extra CO2 target is imposed.

In synthetic Golden Case v3 it is approximately:

```text
PV = 4.09 MW
Battery = 0
CO2 reduction = 33.4%
```

The battery being zero is a valid engineering result: under those assumptions, the value of shifting additional PV is smaller than annualized storage cost.

## 8. What is a carbon constraint?

A 40% target means:

```text
scenario emissions <= 60% of baseline emissions
```

It does **not** tell the optimizer how to achieve the reduction. It only shrinks the feasible set. The optimizer must then find the cheapest solution inside that smaller set.

In Golden Case v3:

- 30% is already met by the economic optimum, so it changes nothing;
- 40% is stricter than the economic optimum, so PV grows and battery storage enters.

## 9. What does “binding” mean?

A constraint is binding when the optimum sits directly on its limit.

Example:

```text
required reduction = 40.0%
optimized reduction = 40.0%
```

The carbon constraint is binding: relaxing or tightening it can change the optimum.

If the optimizer naturally achieves 33.4% and the minimum target is only 20%, the 20% constraint is non-binding.

## 10. What does “infeasible” mean?

Infeasible does **not** mean the solver crashed.

It means no combination of allowed capacities and hourly dispatch can satisfy all constraints.

For example, an extremely deep CO2 target may be impossible if:

- PV capacity is capped;
- battery capacity is capped;
- no other generation technology exists;
- exports receive no offset credit;
- grid imports are still needed at night.

## 11. Why can a carbon target increase battery size?

A stricter target can force more PV. At some point, extra midday PV cannot all be used directly by the load. Storage can shift part of that surplus to later hours and reduce additional grid imports.

This does **not** mean “battery always reduces cost.” In Golden Case v3 the pure economic optimum has no battery; storage enters only when the 40% carbon requirement changes the problem.

## 12. Self-consumption vs self-sufficiency

These are different:

```text
Self-consumption = PV kept onsite / PV generated
```

```text
Self-sufficiency = load not supplied by grid / total load
```

A very large PV plant can have low self-consumption because it exports heavily while still achieving high self-sufficiency.

## 13. Abatement cost

```text
Abatement cost
= (scenario annualized cost - baseline annual cost)
  / avoided tCO2
```

Negative means the modeled lower-emission system is also cheaper than the grid-only baseline.

Positive means additional annualized cost is paid to avoid emissions.

It should never be interpreted without checking the underlying baseline, system boundary and assumptions.

## 14. Reading the frontier

The cost-decarbonization frontier solves several minimum-reduction targets.

Golden Case v3 shows:

```text
0–30%: same economic optimum
40%: PV + battery increase
50%: substantially more PV + battery
```

This reveals a key engineering idea: **the cost of deeper decarbonization is not necessarily linear**.

## 15. Sensitivity analysis

Sensitivity changes one assumption at a time.

Examples from the synthetic case:

- electricity +20% -> more PV and storage becomes attractive;
- WACC 4% -> more PV than at 6%;
- PV CAPEX +20% -> less optimal PV;
- changing only a constant grid-emissions factor -> same economic design if no carbon target exists.

Sensitivity is not a probability model. It answers “what if this assumption changes?”, not “how likely is this future?”

## 16. Why HiGHS?

HiGHS is an open-source mathematical optimization solver suitable for LPs. The v0.3 implementation calls it through SciPy's `linprog` interface because that backend is available and testable offline in the current environment.

The engineering equations are kept independent of the UI and external data sources, so the solver remains a replaceable implementation detail rather than the product architecture itself.

## 17. What the `?` help control does

The v1 Streamlit interface attaches help controls to important inputs and metric cards. Content comes from the central metric/glossary registries and active-case provenance.

For a metric such as WACC, the user will be able to see:

- what WACC means;
- its unit;
- why it matters;
- how it enters CRF/NPV;
- why increasing it can reduce optimal capital-intensive investment;
- important caveats.

The UI will not maintain a separate copy of these explanations.
