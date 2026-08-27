# Industrial Energy Lab — Interview Guide

Use the **Short answer** first. Expand only when the interviewer asks.

## What problem does Industrial Energy Lab solve?
**Short answer:** It screens industrial electrical-decarbonization options by jointly sizing PV and batteries over 8,760 hourly periods and comparing cost, NPV, emissions and sensitivity.

**Deeper answer:** It is deliberately pre-feasibility, not detailed engineering. The engine uses physical energy balances, annualized economics and a linear optimizer.

**IEL example:** The Castellón representative case selects ~2.97 MW PV and no battery in the unconstrained economic optimum.

## Why 8,760 hours?
**Short answer:** Timing matters for load, PV, prices and storage.

**Deeper answer:** Annual averages lose coincidence and battery state dynamics. 8,760 = 24 × 365.

**IEL example:** The UI may plot one week, but the optimizer still solves the full year.

## Why linear programming?
**Short answer:** The v1 equations and objective can be expressed linearly, so LP is transparent, efficient and reproducible.

**Deeper answer:** Capacity and dispatch variables are continuous; energy balances, SOC and bounds are linear. This avoids unnecessary MILP complexity.

**IEL example:** HiGHS solves the sparse annual problem through SciPy `linprog`.

## What are decision variables?
**Short answer:** Quantities the solver is allowed to choose.

**Deeper answer:** PV capacity, battery energy capacity, battery power capacity and hourly dispatch.

**IEL example:** WACC is an input parameter; PV capacity is a decision variable.

## What is the objective function?
**Short answer:** The quantity the optimizer minimizes.

**Deeper answer:** IEL minimizes annualized PV/battery cost + OPEX + grid purchases - export revenue.

**IEL example:** NPV is calculated afterwards rather than mixed into the LP objective.

## What is a constraint?
**Short answer:** A mathematical rule the solution cannot violate.

**IEL example:** SOC bounds, battery power, energy balance, PV availability and optional carbon targets.

## Why cyclic SOC?
**Short answer:** To prevent free energy at the beginning or end of the annual model.

**Deeper answer:** The battery ends with the same SOC condition it started, so the optimizer cannot start full for free or empty it at year-end for artificial benefit.

## Why can optimal battery be zero?
**Short answer:** Because the optimizer installs a technology only if its benefit exceeds its annualized cost under the assumptions.

**IEL example:** In the Castellón economic optimum battery remains zero even at ±20% battery CAPEX sensitivity.

## Why PV-only battery charging?
**Short answer:** It keeps v1 focused on PV self-consumption and avoids grid-arbitrage complexity.

**Deeper answer:** It is an explicit model boundary, not a statement that real batteries cannot charge from the grid.

## What is WACC?
**Short answer:** Weighted Average Cost of Capital, the financing/discount rate used for annualization and NPV.

**IEL example:** Raising WACC from 4% to 6% reduces optimal PV in the representative case.

## What is CRF?
**Short answer:** Capital Recovery Factor converts upfront CAPEX into equivalent annual cost.

**Formula:** `r(1+r)^n / ((1+r)^n - 1)`.

## Why annualized cost?
**Short answer:** It puts multi-year asset investment and yearly grid/OPEX costs in the same €/year unit for optimization.

## What is NPV?
**Short answer:** Net Present Value is discounted future project cash flow minus initial CAPEX.

**IEL caution:** Positive NPV is a screening result, not automatic investment approval.

## NPV vs payback?
**Short answer:** NPV accounts for the time value of money; simple payback does not.

## Self-consumption vs self-sufficiency?
**Short answer:** Self-consumption asks what share of PV stays onsite; self-sufficiency asks what share of site demand avoids the grid.

**IEL example:** ~94.9% PV self-consumption and ~30.4% self-sufficiency can coexist.

## What is a binding carbon constraint?
**Short answer:** A carbon requirement that is active at the optimized limit and therefore shapes the design.

**IEL example:** The economic optimum already cuts ~30.4%, so 20% is non-binding; 40% is binding and storage enters.

## What is an infeasible scenario?
**Short answer:** No combination within current bounds satisfies all constraints. It is not a solver crash.

## What is abatement cost?
**Short answer:** Change in annualized cost per tonne of CO₂ avoided relative to baseline.

**IEL example:** Negative at the economic optimum; positive by the frozen 50% carbon point.

## What is sensitivity analysis?
**Short answer:** Change one assumption and re-solve to see how the optimum changes.

**IEL caution:** It is not a forecast or probability model.

## Where did the ceramic data come from?
**Short answer:** Public sector/system sources plus explicit calibrated proxies and assumptions.

**Deeper answer:** ASCER for sector context, OMIE for 2025 wholesale-price calibration, PVGIS methodology for solar, Red Eléctrica for grid data, IDAE/IRENA for cost reasonableness.

## What is a proxy?
**Short answer:** A transparent approximation used when the exact plant-specific value is unavailable.

**IEL example:** The OMIE-calibrated hourly series is a wholesale energy-price proxy, not an industrial bill.

## Why isn't OMIE the industrial electricity bill?
**Short answer:** Industrial bills/contracts can include hedging, network charges, power terms, taxes, supplier margins and other components outside the wholesale day-ahead energy price.

## Why is this only electrical decarbonization?
**Short answer:** v1 intentionally models electricity + PV + battery + grid. Ceramic kilns/dryers and natural-gas thermal demand are excluded.

## What would you improve in v2?
**Short answer:** Only after v1, I would evaluate thermal-process modeling, richer tariff/contracts, degradation/replacements and possibly more advanced optimization — but only where data and use cases justify the complexity.
