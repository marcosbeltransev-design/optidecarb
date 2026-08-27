# Methodology — Iterations 1–2

## 1. Scope

Iteration 1 freezes the grid-only electrical baseline. Iteration 2 adds an offline, deterministic 8,760-hour simulation of PV, battery storage and grid exchange for **user-defined** capacities. There is still no mathematical sizing optimization; that is reserved for Iteration 3.

## 2. Time basis and units

The engine uses uninterrupted one-hour UTC intervals and exactly 8,760 rows.

- average power: kW;
- interval energy: kWh;
- annual energy: MWh;
- prices: EUR/MWh;
- emissions factor: kgCO2/MWh;
- annual emissions: tCO2.

For a one-hour interval, a `load_kw` value has the same numeric value as interval energy in kWh.

### DST and leap years

The core does not silently repair local-time DST or leap-year anomalies. An adapter/pre-processing layer must normalize them before the engine. Inputs with 8,784 rows, duplicate timestamps, missing hours or non-hourly spacing fail validation.

## 3. Grid-only baseline

For every hour:

```text
GridImport_t = Load_t
GridExport_t = 0
```

Annual consumption:

```text
E_load,MWh = sum_t(Load_t,kWh) / 1000
```

## 4. PV model

PV uses installed AC-equivalent capacity and an offline normalized hourly capacity factor:

```text
PV_t [kWh] = P_PV [kW] * CF_t [-] * Delta_t [h]
```

For the current one-hour model:

```text
Delta_t = 1 h
0 <= CF_t <= 1
```

The demo PV profile is synthetic and is not presented as PVGIS output.

## 5. Battery convention

Battery state of charge is stored as **energy in kWh**. Charge and discharge variables are defined at the site's AC bus:

- `battery_charge_kwh`: AC energy entering the battery charger;
- `battery_discharge_kwh`: AC energy delivered from the battery to site load;
- `SOC_kWh`: stored electrochemical-energy state used by the simplified model.

Charging:

```text
SOC_(t+1) = SOC_t + eta_c * E_charge,t
```

Discharging:

```text
SOC_(t+1) = SOC_t - E_discharge,t / eta_d
```

Combined:

```text
SOC_(t+1) = SOC_t + eta_c * E_charge,t - E_discharge,t / eta_d
```

Losses are explicit:

```text
ChargeLoss_t = E_charge,t * (1 - eta_c)
DischargeLoss_t = E_discharge,t * (1/eta_d - 1)
BatteryLoss_t = ChargeLoss_t + DischargeLoss_t
```

Bounds:

```text
SOC_min <= SOC_t <= SOC_max
0 <= E_charge,t <= P_battery * Delta_t
0 <= E_discharge,t <= P_battery * Delta_t
```

## 6. Deterministic dispatch policy

Iteration 2 deliberately uses a transparent greedy rule, not economic optimization:

1. PV serves site load directly.
2. Surplus PV charges the battery within power and SOC limits.
3. Remaining PV surplus is exported.
4. During a deficit, the battery discharges to site load within power and SOC limits.
5. The grid supplies the remaining deficit.

The battery cannot charge from the grid and cannot export to the grid in Iteration 2. There is no time-of-use arbitrage logic. Consequently, `GridExport_t = PVExport_t` in this iteration, while both concepts remain explicit for future optimization layers.

## 7. Hourly energy balances

Load balance:

```text
Load_t = PV_to_load_t + Battery_discharge_t + Grid_import_t
```

PV balance:

```text
PV_t = PV_to_load_t + PV_to_battery_t + PV_export_t
```

Because all battery losses and SOC changes are explicit, the complete system balance is:

```text
PV_t + GridImport_t + SOC_start,t
=
Load_t + GridExport_t + BatteryLoss_t + SOC_end,t
```

The implementation checks these invariants to tight numerical tolerance.

## 8. Simultaneous-flow policy

Under the deterministic Iteration 2 dispatch:

```text
BatteryCharge_t * BatteryDischarge_t = 0
GridImport_t * GridExport_t = 0
```

No binary variables are needed because this is algorithmic dispatch, not an LP.

## 9. Initial and final SOC policy

Iteration 2 does **not** force `SOC_final = SOC_initial`. The initial SOC is an explicit user input and final SOC is reported, together with net stored-energy change.

For annual economic regression, the golden case starts at minimum SOC, preventing a free initial-energy windfall. The optimizer in Iteration 3 will explicitly evaluate a cyclic end condition to prevent boundary exploitation.

## 10. Annual metrics

PV self-consumption is defined at the AC bus as PV that is not exported:

```text
PV_self_consumed = PV_generation - Grid_export
SelfConsumptionRatio = PV_self_consumed / PV_generation
```

If PV generation is zero, the ratio is defined as zero.

Self-sufficiency is the fraction of site demand not supplied by grid imports:

```text
SelfSufficiencyRatio = (Load - Grid_import) / Load
```

If load is zero, the ratio is defined as zero.

## 11. Electricity economics

Grid import cost:

```text
PurchaseCost = sum_t(GridImport_t [MWh] * ImportPrice_t [EUR/MWh])
```

Export revenue:

```text
ExportRevenue = sum_t(GridExport_t [MWh] * ExportPrice_t [EUR/MWh])
```

Net grid-energy cost:

```text
NetGridEnergyCost = PurchaseCost - ExportRevenue
```

Iteration 2 operating saving:

```text
AnnualOperatingSaving = BaselineEnergyCost - NetGridEnergyCost
```

This is an operating-energy comparison only; it is **not** an investment recommendation and does not yet decide optimal PV/battery CAPEX.

## 12. Grid-related emissions

```text
CO2_grid [tCO2] = GridImport [MWh] * EF [kgCO2/MWh] / 1000
```

Iteration 2 gives **no CO2 credit for exported energy**. This avoids silently assuming displaced-grid emissions before an explicit methodology is chosen.

## 13. Financial primitives retained from Iteration 1

NPV:

```text
NPV = -CAPEX + sum_(n=1..N)(CF_n / (1+r)^n)
```

Capital recovery factor for `r != 0`:

```text
CRF = r(1+r)^N / ((1+r)^N - 1)
AnnualizedCAPEX = CAPEX * CRF
```

Simple payback:

```text
SimplePayback = CAPEX / AnnualNetSavings
```

## 14. Validation strategy

Tests cover:

- frozen grid-only Golden Case v1;
- PV capacity-factor bounds and scaling;
- manual battery efficiency examples;
- SOC and battery power limits;
- exact three-hour hand-checkable dispatch;
- hourly load, PV and full-system energy conservation;
- no simultaneous charge/discharge;
- no simultaneous import/export;
- zero PV, zero battery and zero-system cases;
- zero PV + zero battery reproducing the Iteration 1 baseline;
- 8,760-hour scenario economics and emissions;
- frozen Golden Case v2.
