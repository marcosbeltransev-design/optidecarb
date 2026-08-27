# Assumptions — Iterations 1–2

Every value below is an explicit assumption or software-validation choice. None represents a named industrial company.

## A1 — Demo annual demand

- Value: **22,000 MWh/year**.
- Status: **ASSUMPTION**.
- Source: project-defined synthetic validation case.
- Fixed random seed: `20260827`.

The profile combines weekday/weekend factors, a time-of-day factor, mild seasonality and controlled random variation, then is rescaled to the exact annual target.

## A2 — Demo hourly electricity prices

- Status: **ASSUMPTION / SYNTHETIC**.
- Units: EUR/MWh.
- Source: deterministic formula in `scripts/generate_demo_data.py`.

It is not historical e-sios, OMIE or REData data.

## A3 — Demo grid emissions factor

- Value: **180 kgCO2/MWh**.
- Status: **ASSUMPTION / SOFTWARE VALIDATION**.

It must not be cited as a current Spanish grid factor.

## A4 — Cost boundary

Energy cost currently includes hourly commodity energy purchases minus modeled export revenue. It excludes taxes, network/access tariffs, contracted-power charges, reactive energy, penalties and bespoke retail/PPA structures.

## A5 — Time normalization

- engine timeline: UTC;
- exactly 8,760 rows;
- one-hour resolution;
- leap-year and DST normalization occurs before the core.

## A6 — Demo PV profile

- Status: **ASSUMPTION / SYNTHETIC**.
- Variable: hourly capacity factor in `[0,1]`.
- Dataset version: `demo-v1`.

It is intentionally deterministic and is **not** presented as PVGIS data.

## A7 — Golden Case v2 PV and battery sizes

The regression case uses:

- PV capacity: **4,000 kW**;
- battery energy capacity: **4,000 kWh**;
- battery power capacity: **2,000 kW**.

Status: **ASSUMPTION / SOFTWARE VALIDATION**. These are chosen to exercise direct PV use, storage, export and grid imports; they are not optimized or recommended sizes.

## A8 — Golden Case v2 battery efficiencies and SOC

- charge efficiency: **95%**;
- discharge efficiency: **95%**;
- minimum SOC: **10%**;
- maximum SOC: **90%**;
- initial SOC: **10%**.

Status: **ASSUMPTION / SOFTWARE VALIDATION**. No degradation, self-discharge, temperature dependence, auxiliary consumption or cycle-life cost is modeled yet.

## A9 — Export price

- Golden Case v2 value: **45 EUR/MWh**.
- Status: **ASSUMPTION / SYNTHETIC**.

It is not a current Spanish compensation tariff or market forecast.

## A10 — Battery dispatch

Iteration 2 is PV-first and deterministic. The battery charges only from surplus PV and discharges only to serve site load. Grid charging, battery export and price arbitrage are intentionally excluded until optimization is introduced.

## A11 — SOC boundary treatment

Final SOC is not artificially forced equal to initial SOC in the deterministic simulator. Both are reported. For the annual golden case, initial SOC equals minimum SOC to avoid a free initial-energy benefit. A cyclic boundary will be considered explicitly in Iteration 3 optimization.

## A12 — Export emissions

Exports receive **zero CO2 credit** in Iteration 2. Scenario emissions are calculated only from gross grid imports and the explicit emissions factor.

## A13 — Financial calculations

NPV assumes end-of-year annual cash flows and upfront `t=0` CAPEX. Simple payback ignores discounting by definition. Iteration 2 reports operating-energy savings but does not optimize investment sizing.

## A14 — Representative ceramic plant

Not implemented yet. The future Castellón case must state:

> Synthetic representative industrial profile calibrated using publicly available sector information. It does not represent any individual company.
