# Optimization Guide — OptiDecarb

This guide explains the Iteration 3 model for an engineering reader who is learning optimization. It is intentionally shorter and more intuitive than `METHODOLOGY.md`.

## Plain-English map first

Before the equations, keep this picture in mind:

- **Decision variables** = values the optimizer is allowed to choose.
- **Constraints** = rules it is not allowed to break.
- **Objective function** = the number it tries to make as small as possible.
- **Optimal** = best inside the stated model, not automatically best for a real factory.
- **Binding constraint** = a limit that is actively forcing the solution to change.
- **Infeasible** = the current rules cannot all be satisfied at the same time.

This vocabulary is professional, but the idea is simple: **choose the cheapest allowed solution**.

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

Parameters are fixed inputs, not decisions. Examples include hourly load, PV capacity factor, electricity price, export price, CAPEX/OPEX, WACC, efficiency, site bounds and carbon target.

Changing a parameter can change the optimal solution. Sensitivity analysis deliberately studies this.

## 4. Constraints

Constraints describe what is physically or logically allowed.

Examples:

```text
PV used onsite + PV sent to battery <= available PV
PV used onsite + battery discharge <= site load
SOC_min <= SOC <= SOC_max
charge <= battery power
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

NPV is calculated afterwards. Keeping the annualized objective separate from NPV prevents mixing two different economic frameworks inside the same optimization expression.

## 6. Why annualize CAPEX?

A PV system has a large upfront cost but operates for many years. The capital recovery factor (CRF) converts that upfront investment into an equivalent annual cost using lifetime and WACC.

This lets the LP compare annualized investment, OPEX, grid purchases and export income in the same `EUR/year` unit.

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

It does **not** tell the optimizer how to achieve the reduction. It only shrinks the feasible set.

## 9. What does “binding” mean?

A constraint is binding when the optimum sits directly on its limit. If the optimizer naturally achieves 33.4% reduction and the minimum target is only 20%, the 20% constraint is non-binding.

## 10. What does “infeasible” mean?

Infeasible does **not** mean the solver crashed. It means no combination of allowed capacities and hourly dispatch can satisfy all constraints.

## 11. Why can a carbon target increase battery size?

A stricter target can force more PV. At some point, extra midday PV cannot all be used directly by the load. Storage can shift part of that surplus to later hours and reduce additional grid imports.

## 12. Self-consumption vs self-sufficiency

```text
Self-consumption = PV kept onsite / PV generated
Self-sufficiency = load not supplied by grid / total load
```

## 13. Abatement cost

```text
Abatement cost
= (scenario annualized cost - baseline annual cost)
  / avoided tCO2
```

Negative means the modeled lower-emission system is also cheaper than the grid-only baseline. Positive means additional annualized cost is paid to avoid emissions.

## 14. Reading the frontier

The cost-decarbonization frontier solves several minimum-reduction targets. A key engineering idea is that **the cost of deeper decarbonization is not necessarily linear**.

## 15. Sensitivity analysis

Sensitivity changes one assumption at a time. It is not a probability model; it answers “what if this assumption changes?”

## 16. Why HiGHS?

HiGHS is an open-source mathematical optimization solver suitable for LPs. The v0.3 implementation calls it through SciPy's `linprog` interface because that backend is available and testable offline.

## 17. What the `?` help control does

The Streamlit interface attaches help controls to important inputs and metric cards using centralized definitions and active-case provenance. The UI does not maintain a separate copy of engineering equations.
