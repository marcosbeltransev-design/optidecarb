# Methodology — Iterations 1–3

## 1. Scope

OptiDecarb is an electrical **pre-feasibility screening** model. Iteration 1 defines the grid-only baseline, Iteration 2 validates deterministic PV+battery physics for user-defined sizes, and Iteration 3 adds linear techno-economic sizing/dispatch optimization, carbon constraints, deterministic sensitivity, and explainability.

No thermal process, hydrogen, cogeneration, network power flow, tax model, detailed tariff model, degradation model, or investment recommendation is included.

## 2. Time basis and units

The engine uses exactly 8,760 uninterrupted one-hour UTC intervals.

- average power: kW;
- one-hour interval energy: kWh;
- annual energy: MWh;
- electricity price: EUR/MWh;
- emissions factor: kgCO2/MWh;
- annual emissions: tCO2;
- CAPEX: EUR, EUR/kW or EUR/kWh;
- annualized/OPEX values: EUR/year.

Because `Delta t = 1 h`, a kW average over one interval has the same numeric value as kWh in that interval. Code still names energy variables explicitly in kWh to avoid hidden unit conversion.

### DST and leap years

The engine never silently repairs time-series anomalies. Local-time DST and 8,784-hour leap-year datasets must be normalized upstream before entering the core.

## 3. Grid-only baseline

```text
GridImport_t = Load_t
GridExport_t = 0
```

```text
E_load,MWh = sum(Load_t,kWh) / 1000
```

```text
BaselineCost = sum(GridImport_t / 1000 * ImportPrice_t)
```

## 4. PV

```text
PVGeneration_t [kWh] = PVCapacity [kW] * CF_t [-]
```

with:

```text
0 <= CF_t <= 1
PVCapacity >= 0
```

In Iteration 3 `PVCapacity` is a decision variable.

## 5. Battery convention

Charge/discharge are AC-bus energies; SOC is stored energy in kWh.

```text
SOC_t = SOC_(t-1) + eta_c * Charge_t - Discharge_t / eta_d
```

where:

- `Charge_t` is PV energy sent to storage from the AC allocation;
- `Discharge_t` is AC energy delivered from storage to site load.

Losses:

```text
BatteryLoss_t
= Charge_t * (1 - eta_c)
+ Discharge_t * (1/eta_d - 1)
```

Capacity-dependent SOC bounds:

```text
SOC_min_fraction * BatteryEnergy
<= SOC_t <=
SOC_max_fraction * BatteryEnergy
```

Power limits for each one-hour interval:

```text
Charge_t <= BatteryPower
Discharge_t <= BatteryPower
```

## 6. Iteration 2 deterministic dispatch

1. PV serves load.
2. Surplus PV charges the battery.
3. Remaining surplus is exported.
4. Battery serves later deficits.
5. Grid serves the residual deficit.

It is physical validation, not cost optimization.

## 7. Iteration 3 optimization variables

Capacity decisions:

```text
PVCapacity >= 0
BatteryEnergy >= 0
BatteryPower >= 0
```

Hourly LP variables retained explicitly:

```text
PVToLoad_t >= 0
PVToBattery_t >= 0
BatteryDischarge_t >= 0
SOC_t >= 0
```

`GridImport_t` and `PVExport_t` are **exact residual flows**, not independent decision variables:

```text
GridImport_t
= Load_t - PVToLoad_t - BatteryDischarge_t
```

```text
PVExport_t
= CF_t * PVCapacity - PVToLoad_t - PVToBattery_t
```

The equivalent non-negativity constraints are:

```text
PVToLoad_t + BatteryDischarge_t <= Load_t
```

```text
PVToLoad_t + PVToBattery_t <= CF_t * PVCapacity
```

This elimination reduces the annual model from `6n+3` to `4n+3` variables without approximation.

## 8. Battery charging-source policy

The MVP uses:

# PV-CHARGED BATTERY ONLY

`PVToBattery_t` belongs to the PV allocation constraint, so grid electricity cannot directly charge the battery. Battery discharge belongs to the onsite load balance and cannot be exported.

This deliberately excludes grid-to-battery arbitrage in v1.

## 9. Cyclic annual SOC

Iteration 3 prevents free boundary energy by enforcing:

```text
SOC_final = initial_SOC_fraction * BatteryEnergy
```

and the first interval starts from the same fraction of optimized battery capacity. Thus annual optimization cannot improve results by starting full and ending empty.

## 10. Simultaneous flows in the LP

No binary variables are introduced.

### Import/export

Input validation requires:

```text
ExportPrice_t < ImportPrice_t
```

for every hour. Under the linear objective, simultaneous import/export cannot improve cost because redirecting one kWh of exported PV to onsite load avoids a higher purchase price.

### Charge/discharge

Battery conversion efficiencies are <=1, direct PV-to-load is more efficient than cycling, and a tiny positive throughput tie-break cost removes numerically degenerate cycling without materially changing economics.

Regression tests verify no material simultaneous charge/discharge or import/export in solved cases.

## 11. Model/site bounds

Configurable upper bounds are not universal engineering facts:

```text
PVCapacity <= MaxPV
BatteryEnergy <= MaxBatteryEnergy
BatteryPower <= MaxBatteryPower
```

They represent screening/site limits, prevent nonsensical unbounded sizing, and allow feasibility analysis.

## 12. Annualized objective

PV CRF:

```text
CRF_pv = r(1+r)^Npv / ((1+r)^Npv - 1)
```

Battery uses its own lifetime and therefore its own CRF.

Annual technology costs:

```text
AnnualPV
= PVCapacity * (PV_CAPEX_per_kW * CRF_pv + PV_OPEX_per_kW_year)
```

```text
AnnualBattery
= BatteryEnergy * (BatteryEnergyCAPEX * CRF_bat + BatteryEnergyOPEX)
+ BatteryPower * (BatteryPowerCAPEX * CRF_bat + BatteryPowerOPEX)
```

Grid economics:

```text
PurchaseCost
= sum(GridImport_t / 1000 * ImportPrice_t)
```

```text
ExportRevenue
= sum(PVExport_t / 1000 * ExportPrice_t)
```

Objective:

```text
min TotalAnnualizedCost
= AnnualPV
+ AnnualBattery
+ PurchaseCost
- ExportRevenue
```

NPV is **not** mixed into the LP objective.

## 13. Project NPV and simple payback post-processing

Initial CAPEX:

```text
InitialCAPEX
= PVCapacity * PV_CAPEX
+ BatteryEnergy * BatteryEnergyCAPEX
+ BatteryPower * BatteryPowerCAPEX
```

Simplified annual project cash flow:

```text
AnnualProjectCashFlow
= BaselineGridCost
- ScenarioNetGridCost
- PV_OPEX
- Battery_OPEX
```

```text
NPV
= -InitialCAPEX
+ sum(AnnualProjectCashFlow / (1+r)^year)
```

```text
SimplePayback
= InitialCAPEX / AnnualProjectCashFlow
```

The v0.3 NPV model deliberately excludes replacements, degradation, salvage value, taxes, depreciation and financing structure beyond WACC. Project life is not allowed to exceed the shortest modeled technology lifetime in this simplified no-replacement calculation.

## 14. Emissions

No export credit:

```text
ScenarioCO2 [tCO2]
= GridImport [MWh] * GridEF [kgCO2/MWh] / 1000
```

```text
DeltaCO2 = BaselineCO2 - ScenarioCO2
```

```text
ReductionFraction = DeltaCO2 / BaselineCO2
```

## 15. Carbon constraint

For target `r`:

```text
ScenarioCO2 <= (1-r) * BaselineCO2
```

or equivalently, required avoided grid imports must be at least `r` times baseline grid-related emissions.

`r=0` reproduces the pure economic optimum.

A target is reported as **binding** when optimized emissions lie at the allowed maximum within numerical tolerance. A looser target already satisfied by the unconstrained optimum is non-binding.

## 16. Solver states

The solver layer translates HiGHS outcomes to:

- `optimal`;
- `infeasible`;
- `unbounded`;
- `solver_error`.

An infeasible target is not treated as a software failure.

## 17. Abatement cost

```text
DeltaCost
= ScenarioAnnualizedCost - BaselineAnnualCost
```

```text
AbatementCost [EUR/tCO2]
= DeltaCost / DeltaCO2
```

- negative: modeled CO2 is reduced while equivalent annual cost also falls;
- positive: modeled reduction carries additional equivalent annual cost;
- undefined if no positive CO2 reduction occurs.

## 18. Cost-decarbonization frontier

The default targets are:

```text
0%, 10%, 20%, 30%, 40%, 50%
```

The unconstrained economic optimum is solved once. Any lower target already satisfied by it uses the same exact optimum; only stricter targets require additional solves.

The frontier reports capacity, cost, grid exchange, emissions, abatement cost, feasibility and whether the carbon constraint binds.

## 19. Deterministic sensitivity

One parameter is changed at a time while all others remain fixed. Default multipliers are:

```text
0.8, 0.9, 1.0, 1.1, 1.2
```

Variables:

- electricity-price multiplier;
- PV-CAPEX multiplier;
- battery-CAPEX multiplier;
- WACC;
- grid-emission-factor multiplier;
- carbon target.

A constant emission-factor change without a carbon constraint does not enter the economic objective, so it changes absolute tCO2 values but not the cost-optimal design or percentage reduction. The implementation derives those rows without redundant LP solves.

### On-demand execution policy

Interactive use runs **one sensitivity family at a time**. This is a deliberate product and performance decision: a user selects electricity price, PV CAPEX, battery CAPEX, WACC, emission factor, or carbon target, then only that family is solved. The lower-level multi-family routine remains available for scripted analysis, but the Streamlit UI must not calculate every family on each rerun.

## 20. Explainability layer

The metric registry is a single structured source for future UI help controls. Each metric contains:

```text
metric_id
label
short_description
unit
why_it_matters
calculation
interpretation
relationships
caveats
```

Rule-based insights compare actual results only. They can state observed facts such as:

- battery optimum is zero;
- carbon constraint is binding;
- PV/battery capacity increases between targets;
- annualized cost rises between solved scenarios;
- abatement cost is negative or positive.

They do not use generative AI to invent causal explanations.

## 21. Solver implementation choice

The LP is solved using HiGHS via SciPy `linprog` in v0.3. Unconstrained economic problems use HiGHS dual simplex; explicit carbon-constrained problems use HiGHS interior-point because it was more stable for the annual regression case in the available runtime.

Pyomo + HiGHS remains architecturally possible, but adding an untested dependency layer would not improve the current validated LP. The physical/economic formulation is solver-independent and isolated in `optimization/`.

## 22. Validation strategy

Tests cover all previous iterations plus:

- hand-computable no-investment optimum;
- hand-computable PV optimum;
- cheap-storage entry;
- manually known carbon-constrained optimum;
- infeasible target distinction;
- cyclic SOC;
- energy conservation;
- no material simultaneous flows;
- input validation and anti-arbitrage price ordering;
- metric registry completeness and relationship validity;
- deterministic result insights;
- frontier reuse of non-binding economic optimum;
- break-even transition logic;
- Golden Case v3 economic optimum;
- Golden Case v3 binding 40% carbon case.


## 23. Streamlit presentation boundary

Iteration 4 does not change the mathematical model. The UI calls the same validated baseline and optimization services used by tests. Input widgets collect explicit assumptions; a form submit triggers a solve; charts and cards render returned values.

The interface deliberately distinguishes:

- **model assumption** — a user-editable or synthetic validation input;
- **dataset value** — a value read from a versioned offline snapshot;
- **calculated result** — an output produced by the engine.

Important inputs and outputs receive educational help from the centralized metric registry. The help describes what a quantity is, its units, why it matters, its calculation, interpretation, relationships and material caveats. The UI does not use generative AI to explain results.


---

# v1.0 representative-case methodology

The optimization equations remain model version **0.3.0**. The v1.0 application adds a public-data-calibrated case layer without changing the mathematical model.

## Evidence classes

Case inputs explicitly distinguish published sector/official data, derived public values, proxies and model assumptions. The complete transformation/provenance chain is stored in `cases/ceramic_castellon/sources.json`.

## Representative load

The Castellón case uses a 15,000 MWh/year rounded representative scale. The deterministic hourly shape is a modelling assumption and is rescaled exactly to the annual total. It is not a measured factory profile.

## Price proxy

The hourly price series is calibrated to 2025 OMIE day-ahead statistics and is treated only as a wholesale energy-price proxy. It excludes network charges, taxes, contracted-power terms, supplier margins and hedging.

## Solar profile

PVGIS 5.3 is the official methodology reference. The committed v1 series is a deterministic profile calibrated to documented PVGIS-derived Castelló monthly yield values, not raw PVGIS hourly data.

## Grid-emission factor

The case factor is transparently derived from Red Eléctrica 2025 national generation emissions divided by national electricity generation. It remains constant over all 8,760 hours; exports receive no carbon credit.

## Interpretation boundary

The ceramic case models only the electrical subsystem. No claim is made about total ceramic-process decarbonization because kilns, dryers, natural-gas consumption and other thermal processes are outside v1.
