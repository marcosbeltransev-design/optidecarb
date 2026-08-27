# Assumptions — Iterations 1–3

Every value below is either a software-validation assumption or an explicit model convention. None represents a named industrial company.

## A1 — Demo annual demand

- Value: **22,000 MWh/year**.
- Classification: **ASSUMPTION / SOFTWARE VALIDATION**.
- Source: deterministic project generator.
- Fixed random seed: `20260827`.

## A2 — Demo hourly electricity prices

- Units: EUR/MWh.
- Classification: **ASSUMPTION / SYNTHETIC**.
- Source: deterministic formula in `scripts/generate_demo_data.py`.

Not historical e-sios, OMIE or REData data.

## A3 — Demo grid emissions factor

- Value: **180 kgCO2/MWh**.
- Classification: **ASSUMPTION / SOFTWARE VALIDATION**.
- Source: synthetic model-validation choice.

It must not be cited as a current Spanish grid factor.

## A4 — Cost boundary

Current grid economics include hourly energy purchases minus PV-export revenue. They exclude taxes, network/access tariffs, contracted-power charges, reactive energy, penalties and bespoke PPA/retail structures.

## A5 — Time normalization

- engine timeline: UTC;
- 8,760 rows;
- one-hour intervals;
- DST/leap-year normalization occurs upstream.

## A6 — Demo PV profile

- Classification: **ASSUMPTION / SYNTHETIC**.
- Variable: capacity factor `[0,1]`.
- Dataset version: `demo-v1`.
- Source: deterministic project generator, not PVGIS.

## A7 — Golden Case v2 fixed capacities

- PV: 4,000 kW;
- battery energy: 4,000 kWh;
- battery power: 2,000 kW.

Chosen only to exercise the physical simulator.

## A8 — Battery efficiencies and SOC convention

Golden v2 and v3 validation defaults:

- charge efficiency: 95%;
- discharge efficiency: 95%;
- min SOC: 10%;
- max SOC: 90%;
- initial SOC fraction: 10%.

No degradation, self-discharge, thermal dependence, auxiliaries or cycle-life cost is included.

## A9 — Export prices

- Golden v2 physical simulation: **45 EUR/MWh**.
- Golden v3 optimization: **20 EUR/MWh**.

Both are **synthetic assumptions**, not current Spanish tariffs or forecasts. Golden v3 uses the lower value deliberately so additional PV eventually faces declining onsite economic value.

## A10 — Battery operating boundary

In v0.3 the optimized battery charges only from the PV allocation and discharges only to onsite load. Grid charging and battery export are excluded.

## A11 — SOC boundary

Iteration 2 reports actual final SOC. Iteration 3 optimization enforces a cyclic annual SOC at the same configured initial fraction of optimized capacity.

## A12 — Export emissions

Exports receive **no CO2 credit**. Operational emissions are attributed only to gross grid imports using the explicit grid factor.

## A13 — Financial primitives

NPV assumes upfront `t=0` CAPEX and equal end-of-year operating cash flows. Simple payback ignores discounting by definition.

## A14 — Golden Case v3 PV economics

From `data/demo/optimization_assumptions.json`:

| Parameter | Value | Unit | Classification | Source |
|---|---:|---|---|---|
| PV CAPEX | 1,600 | EUR/kW | ASSUMPTION | Synthetic validation choice |
| PV OPEX | 10 | EUR/kW-year | ASSUMPTION | Synthetic validation choice |
| PV life | 25 | years | ASSUMPTION | Synthetic validation choice |

These values are selected to create a useful validation case; they are not a market benchmark.

## A15 — Golden Case v3 battery economics

| Parameter | Value | Unit | Classification | Source |
|---|---:|---|---|---|
| Energy CAPEX | 150 | EUR/kWh | ASSUMPTION | Synthetic validation choice |
| Power CAPEX | 100 | EUR/kW | ASSUMPTION | Synthetic validation choice |
| Energy OPEX | 2 | EUR/kWh-year | ASSUMPTION | Synthetic validation choice |
| Power OPEX | 1 | EUR/kW-year | ASSUMPTION | Synthetic validation choice |
| Battery life | 15 | years | ASSUMPTION | Synthetic validation choice |

## A16 — WACC and project life

- WACC: **5%**;
- simplified NPV project life: **15 years**.

Classification: **ASSUMPTION / SOFTWARE VALIDATION**. This is not a company-specific financing recommendation.

## A17 — Model/site bounds

Golden v3:

- max PV: 12,000 kW;
- max battery energy: 12,000 kWh;
- max battery power: 6,000 kW.

Classification: **MODEL BOUNDS**, not physical universal limits. They stand in for site/decision-space constraints and support feasibility testing.

## A18 — LP anti-arbitrage convention

For every hour:

```text
ExportPrice < ImportPrice
```

is required. This is a model-validity condition for the continuous LP formulation, not a statement about every possible commercial contract.

## A19 — Throughput tie-break

A numerically tiny positive cost is added to battery charge/discharge variables only to remove degenerate simultaneous cycling. It is many orders of magnitude below material economic terms and is excluded from reported annualized economics.

## A20 — Simplified NPV limitations

The v0.3 post-processing NPV excludes:

- battery/PV replacement;
- degradation;
- residual/salvage value;
- taxes and depreciation;
- inflation/escalation;
- debt/equity cash-flow structure.

For that reason the configured project life cannot exceed the shortest modeled technology lifetime.

## A21 — Sensitivity interpretation

Sensitivity is deterministic one-at-a-time analysis, not uncertainty probability. A result at `0.8x CAPEX` means only that the tested assumption was multiplied by 0.8 while all other inputs stayed fixed.

The targeted battery-CAPEX scan in the synthetic Golden v3 case observed positive storage at `0.74x` and zero storage at `0.76x`. This is an **observed grid transition**, not a universal or exact commercial break-even price.

## A22 — Representative ceramic plant

Not implemented yet. Iteration 5 must state:

> Synthetic representative industrial profile calibrated using publicly available sector information. It does not represent any individual company.


## A9. Iteration 4 interface assumptions

- The Streamlit default inputs are loaded from `data/demo/optimization_assumptions.json`; they remain **SYNTHETIC SOFTWARE-VALIDATION ASSUMPTIONS**.
- Custom load uploads must match the current 8,760-hour UTC demo timeline because Iteration 4 keeps the versioned PV and price snapshots fixed. This is an explicit alignment rule, not a universal limitation of the engine.
- Sensitivity is run one family at a time and only after user request. This is a product/performance policy, not a change to the underlying equations.
- UI number formatting intentionally rounds for readability; engine calculations and regression tests retain full numerical precision.
