# Methodology — Iteration 1

## 1. Scope

Iteration 1 models the electrical **baseline only**. There is no PV generation, battery, export, optimization, or industrial thermal demand in the calculation engine yet. This is deliberate: subsequent iterations must build on a validated baseline rather than mixing physical and economic changes at once.

## 2. Time basis

The engine uses one-hour intervals. Input datasets are normalized to an uninterrupted UTC index with exactly 8,760 rows.

For each interval `t`:

- `load_kw[t]` = average electrical power during the hour [kW];
- interval energy = `load_kw[t] * 1 h` [kWh].

Annual consumption is therefore:

```text
E_load,MWh = sum_t(load_kw[t]) / 1000
```

### DST and leap-year policy

The engine itself does not silently repair daylight-saving-time or leap-year anomalies. Inputs with 8,784 rows, duplicate timestamps, missing timestamps, or non-hourly spacing fail validation. A future adapter/pre-processing layer may normalize those datasets explicitly while preserving provenance.

## 3. Grid-only energy balance

For Iteration 1:

```text
GridImport_t = Load_t
GridExport_t = 0
```

Thus the per-hour conservation residual is:

```text
residual_t = GridImport_t - Load_t = 0
```

The baseline energy-balance function checks this invariant.

## 4. Electricity cost

Hourly electricity commodity cost is:

```text
Cost_t [EUR] = Load_t [kW] / 1000 * Price_t [EUR/MWh]
```

Annual energy cost is:

```text
Cost_annual = sum_t(Cost_t)
```

This Iteration 1 value excludes network tariffs, taxes, demand charges and other contract-specific items. Those omissions are documented rather than hidden.

## 5. Grid-related emissions

Given annual grid import `E_grid [MWh]` and an explicit factor `EF [kgCO2/MWh]`:

```text
CO2_grid [tCO2] = E_grid * EF / 1000
```

For future scenario comparison:

```text
DeltaCO2 = CO2_base - CO2_new
ReductionFraction = DeltaCO2 / CO2_base
```

If `CO2_base = 0`, the implementation returns a zero reduction fraction to avoid undefined division.

## 6. Abatement cost sign convention

```text
AbatementCost [EUR/tCO2] = DeltaCost [EUR] / DeltaCO2 [tCO2]
```

where `DeltaCost = Cost_new - Cost_base` in future scenario analysis.

- positive result: emissions reduction costs additional money;
- negative result: the lower-emission option also saves money;
- no result when `DeltaCO2 <= 0`.

## 7. Net present value

The project convention is:

```text
NPV = -CAPEX + sum_{n=1..N}(CF_n / (1+r)^n)
```

- upfront CAPEX occurs at `t=0`;
- positive annual cash flow is a project benefit/saving;
- positive NPV means discounted benefits exceed the upfront CAPEX under the supplied assumptions.

A manual closed-form-equivalent numerical example is included in unit tests.

## 8. Capital recovery factor

For `r != 0`:

```text
CRF = r(1+r)^N / ((1+r)^N - 1)
AnnualizedCAPEX = CAPEX * CRF
```

For `r = 0`:

```text
CRF = 1/N
```

## 9. Simple payback

```text
SimplePayback [years] = CAPEX / AnnualNetSavings
```

No payback is returned when annual net savings are zero or negative.

## 10. Validation strategy

Iteration 1 tests cover:

- exact hourly baseline energy conservation;
- no negative demand;
- no missing/duplicate/non-hourly timestamps;
- exact 8,760-row requirement;
- manual NPV comparison;
- simple emissions calculation;
- end-to-end demo baseline;
- stable golden regression outputs.

Future PV/battery tests will add SOC bounds, efficiency losses, generation caps and dispatch invariants.
