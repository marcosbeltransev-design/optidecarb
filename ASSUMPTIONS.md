# Assumptions — Iteration 1

Every value below is an explicit assumption or software-validation choice. None is intended to represent a named industrial company.

## A1 — Demo annual demand

- Value: **22,000 MWh/year**.
- Status: **ASSUMPTION**.
- Purpose: stable, human-readable regression target for a generic industrial electrical profile.
- Source: project-defined synthetic test case.

The profile combines weekday/weekend factors, a small time-of-day factor, mild seasonality and controlled random variation. It is rescaled so annual demand is exactly the target. Fixed seed: `20260827`.

## A2 — Demo hourly electricity prices

- Status: **ASSUMPTION / SYNTHETIC**.
- Units: EUR/MWh.
- Source: deterministic formula in `scripts/generate_demo_data.py`.

The profile is intentionally not historical e·sios/OMIE/REData data. It exists to test hourly cost calculations reproducibly.

## A3 — Demo grid emissions factor

- Value: **180 kgCO2/MWh**.
- Status: **ASSUMPTION / SYNTHETIC SOFTWARE-VALIDATION VALUE**.
- Source: project-defined test input.

This must not be cited as a current Spanish electricity-system emissions factor. A sourced factor or time series can be introduced later through a versioned data adapter/snapshot workflow.

## A4 — Cost boundary

Iteration 1 annual electricity cost includes hourly commodity energy only. It excludes:

- taxes;
- network/access tariffs;
- contracted-power charges;
- reactive energy charges;
- penalties;
- capacity-market or service fees;
- bespoke PPA/retail contract structure.

These exclusions make the current result a screening baseline, not an invoice reconstruction.

## A5 — Time normalization

- Engine index: UTC.
- Rows: exactly 8,760.
- Resolution: 1 hour.
- Leap years: must be normalized outside the engine before calculation.
- DST: no duplicated or missing local-clock hour is accepted inside the engine.

## A6 — Demo PV profile

A normalized synthetic `capacity_factor` profile is included only to freeze the offline data contract ahead of Iteration 2. It is **not yet used by an energy model** and must not be presented as a PVGIS result.

## A7 — Financial calculations

NPV assumes end-of-year annual cash flows and an upfront `t=0` CAPEX. Simple payback ignores discounting by definition. Financial assumptions for PV/battery investments are deferred until those technologies exist.

## A8 — Representative ceramic plant

Not implemented in Iteration 1. The future Castellón case must state:

> Synthetic representative industrial profile calibrated using publicly available sector information. It does not represent any individual company.
