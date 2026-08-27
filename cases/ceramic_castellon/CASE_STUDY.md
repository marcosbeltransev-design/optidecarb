# Representative Ceramic Plant — Castellón, Spain

**Industrial Energy Lab v1.0 public-data-calibrated case study**

> This representative case is constructed from public sector data and explicit modelling assumptions. It does not reproduce the operations, costs or energy consumption of any individual ceramic company.

> This case evaluates the **electrical subsystem** of a representative ceramic plant. Thermal process energy, kilns, dryers and natural-gas consumption are outside the v1 model scope.

## 1. Executive summary

Industrial Energy Lab (IEL) is a **pre-feasibility** screening tool: it helps identify promising configurations and important assumptions before detailed engineering. The case combines a deterministic 8,760-hour representative industrial electricity load, a Castellón solar profile calibrated to PVGIS-derived public information, a 2025 Spanish wholesale-price proxy calibrated to OMIE, and traceable screening assumptions.

The economic optimum under the frozen case assumptions is approximately **2.97 MW of photovoltaic (PV) capacity and no battery**. It reduces modeled grid imports and grid-related CO₂-equivalent emissions by about **30.4%** while lowering equivalent annualized cost. A minimum **40% CO₂ reduction** becomes binding and causes storage to enter the minimum-cost feasible solution.

This is a screening result, not a construction recommendation.

## 2. Why Castellón ceramics?

ASCER reports that Spanish ceramic-tile production reached **423 million m² in 2025**, with about **1.6 TWh of sector electricity consumption** and photovoltaic self-consumption covering about **12%** of sector electricity. ASCER also identifies Castellón as the dominant geographic cluster. These are **sector data**, not plant measurements.

The case therefore asks a narrow question: how might the **electrical** subsystem of a representative plant-scale case respond to PV, battery economics and explicit carbon constraints?

## 3. Data vocabulary

IEL distinguishes four evidence types:

| Classification | Meaning | Example in this case |
|---|---|---|
| Direct/official or sector data | Published external evidence | OMIE annual/monthly price statistics; ASCER sector energy statistics |
| Derived public value | Calculated transparently from published values | Grid emission factor derived from Red Eléctrica generation and emissions |
| Proxy | Approximation when the exact plant-specific value is unavailable | OMIE-calibrated wholesale energy-price profile; PVGIS-calibrated solar profile |
| Model assumption | Explicit, editable screening choice | 5% WACC; battery cost decomposition; 0 €/MWh export value |

A **proxy** is not a measured plant value. A **model assumption** is not automatically arbitrary: it must be explicit, traceable and sensitivity-tested where important.

Full provenance is stored in `sources.json`.

## 4. Representative plant definition

### Annual scale

The case uses **15,000 MWh/year** (15 GWh/year).

This is **not** described as the average ceramic factory. It is a rounded representative scale selected to be consistent with the order of magnitude implied by published sector electricity consumption and sector structure while avoiding false plant-level precision.

### Hourly shape

No public 8,760-hour load profile of a specific Castellón ceramic factory is used. The hourly load is deterministic and consists of:

- a high continuous base load;
- a modest daytime production uplift;
- an 8% weekend reduction;
- mild seasonality;
- fixed-seed low-amplitude variation.

The shape is then rescaled exactly to 15,000 MWh/year.

### Validation statistics

| Metric | Value |
|---|---:|
| Annual electricity | 15,000 MWh |
| Average demand | 1.712 MW |
| Peak demand | 1.998 MW |
| Load factor | 85.7% |
| P5 demand | 1.511 MW |
| P50 demand | 1.717 MW |
| P95 demand | 1.879 MW |
| Weekday/weekend mean ratio | 1.087 |

**MW** is power: the instantaneous rate of energy use. **MWh** is energy: the quantity used over time. For example, 1 MW sustained for 1 hour equals 1 MWh.

## 5. Solar resource

The case uses Castelló de la Plana as a representative public city location, not a factory coordinate. PVGIS 5.3 is the official solar-methodology reference. Because a raw PVGIS hourly download could not be retrieved in the build sandbox, the committed v1 dataset is a **deterministic PVGIS-calibrated representative profile**, not raw PVGIS hourly data.

The profile is calibrated to approximately **1,616.8 kWh/kWp/year** and monthly production values documented in `sources.json`, using 14% system losses and a fixed system orientation assumption.

**PV — Photovoltaic** capacity is measured in kW/MW; PV generation is energy measured in kWh/MWh. These must not be confused.

## 6. Electricity prices

OMIE reports a 2025 Spanish day-ahead annual average of **65.28 €/MWh**. IEL preserves the documented monthly means and constructs deterministic intra-month hourly variation.

This series is explicitly a:

**WHOLESALE ENERGY-PRICE PROXY**

It is **not** a real industrial electricity bill. A real industrial contract can include hedging, supplier margins, network charges, contracted-power terms, taxes and other components outside v1.

The case uses **0 €/MWh export value** as a conservative model assumption. It is not presented as a universal Spanish export tariff.

## 7. Grid emissions

Red Eléctrica reports **272,201 GWh** of Spanish national generation and **29.5 million tCO₂eq** of generation emissions for 2025. IEL derives:

```text
29.5e6 tCO2eq / 272.201e6 MWh
= 0.108375 tCO2eq/MWh
= 108.375 kgCO2eq/MWh
```

This is therefore a **derived public value**, not a factor quoted directly from the source.

IEL uses:

```text
Grid-related CO2 = grid imports × grid emission factor
```

and gives no export CO₂ credit in v1.

## 8. Economic assumptions

**CAPEX — Capital Expenditure** is upfront investment. **OPEX — Operating Expenditure** is recurring annual operating cost.

| Input | Case value | Classification |
|---|---:|---|
| PV CAPEX | 700 €/kW | Screening assumption inside IDAE range, cross-checked with IRENA |
| PV OPEX | 7 €/kW-year | Rounded European proxy |
| Battery energy CAPEX | 240 €/kWh | Model decomposition |
| Battery power CAPEX | 120 €/kW | Model decomposition |
| WACC | 5% | Model assumption |
| PV life | 25 years | Model assumption / screening convention |
| Battery life | 15 years | Model assumption / screening convention |
| Project NPV horizon | 15 years | Model assumption |

**WACC — Weighted Average Cost of Capital** is the financing/discount rate used in annualization and NPV. Higher WACC makes capital-intensive solutions less attractive, all else equal.

The **CRF — Capital Recovery Factor** converts upfront CAPEX into an equivalent annual cost:

```text
CRF = r(1+r)^n / ((1+r)^n - 1)
```

This lets the optimizer compare capital investment, OPEX and grid purchases in the same unit: €/year.

## 9. Baseline

The **baseline** is the grid-only reference used for comparison.

| Metric | Result |
|---|---:|
| Annual load | 15,000 MWh/year |
| Modeled energy component cost | €983,366/year |
| Grid-related emissions | 1,625.6 tCO₂eq/year |

The baseline cost is only the modeled hourly energy component under the OMIE-calibrated proxy. It is not a complete industrial bill.

## 10. Economic optimum

IEL uses **LP — Linear Programming**. The optimizer chooses decision variables such as PV capacity, battery energy/power and hourly dispatch while obeying constraints such as energy balance, PV availability, battery power, **SOC — State of Charge** limits and optional carbon targets.

The **objective function** is total annualized cost.

| Metric | Economic optimum |
|---|---:|
| PV capacity | 2.972 MW |
| Battery energy | 0 MWh |
| Battery power | 0 MW |
| PV generation | 4,804 MWh/year |
| PV self-consumption | 94.9% |
| Electrical self-sufficiency | 30.4% |
| Grid imports | 10,441 MWh/year |
| Grid export | 245 MWh/year |
| Initial CAPEX | €2.080 million |
| Annualized system cost | €880,203/year |
| Equivalent annual improvement vs baseline | €103,163/year |
| Simplified NPV | +€522,604 |
| Simple payback | 8.30 years |
| CO₂ reduction | 30.4% |
| Abatement cost | -€208.8/tCO₂ |

### Why is the optimal battery zero?

Zero storage is a valid result. Under the frozen economic assumptions, the additional annualized battery cost and conversion losses are not offset by enough extra value from shifting PV. Battery-CAPEX sensitivity at 0.8×, 1.0× and 1.2× keeps the economic optimum at zero storage.

This does **not** prove that batteries are uneconomic for real ceramic plants; it means they are not selected in this representative v1 case under the stated model boundary and assumptions.

### Self-consumption vs self-sufficiency

These answer different questions:

```text
Self-consumption = PV kept onsite / PV generated
Self-sufficiency = load not supplied by grid / total load
```

The economic optimum has about **94.9% self-consumption** but only **30.4% self-sufficiency**. Most PV stays onsite, yet the site still imports a large share of annual electricity.

## 11. Carbon frontier

A **carbon target** is a minimum modeled CO₂ reduction relative to baseline. It is not renewable share and not self-sufficiency.

| Minimum CO₂ reduction | PV MW | Battery MWh | Battery MW | Annualized cost €/y | Abatement €/tCO₂ | Binding? |
|---:|---:|---:|---:|---:|---:|:---:|
| 0% | 2.97 | 0.00 | 0.00 | 880,203 | -208.8 | No |
| 10% | 2.97 | 0.00 | 0.00 | 880,203 | -208.8 | No |
| 20% | 2.97 | 0.00 | 0.00 | 880,203 | -208.8 | No |
| 30% | 2.97 | 0.00 | 0.00 | 880,203 | -208.8 | No |
| 40% | 4.25 | 2.46 | 0.57 | 927,346 | -86.2 | Yes |
| 50% | 5.34 | 6.83 | 1.45 | 1,007,628 | +29.8 | Yes |

A **binding constraint** is a requirement that actively limits the solution. Because the economic optimum already reduces emissions by ~30.4%, targets up to 30% do not change it. At 40%, the carbon constraint becomes binding and both PV and battery capacity increase.

**Abatement cost** is:

```text
(Scenario annualized cost - baseline annual cost) / avoided tCO2
```

Negative means the modeled lower-emission system is also cheaper than baseline. Positive means deeper modeled reduction requires extra annualized cost.

## 12. Sensitivity

Sensitivity analysis changes one assumption at a time. It is a deterministic **what-if** analysis, not a forecast or probability model.

Selected solved points:

- electricity price 0.8× → PV 2.71 MW;
- electricity price 1.2× → PV 3.19 MW;
- PV CAPEX 0.8× → PV 3.21 MW;
- PV CAPEX 1.2× → PV 2.79 MW;
- WACC 4% → PV 3.09 MW;
- WACC 6% → PV 2.87 MW;
- battery CAPEX 0.8× to 1.2× → economic-optimum battery remains zero.

These results are consistent with the expected screening relationships: higher electricity prices increase the value of onsite generation, while higher PV CAPEX or WACC reduce the attractiveness of capital-intensive PV.

## 13. What the case teaches

1. **Optimization is conditional.** “Optimal” means lowest modeled objective under the stated assumptions and constraints, not universally best.
2. **Battery = 0 can be the correct answer.** A technology should not be forced into a result.
3. **Self-consumption and self-sufficiency are different.** One describes PV use; the other describes grid dependence.
4. **Deeper carbon targets can change technology choice.** Storage appears when the 40% target becomes binding.
5. **Annualized CAPEX is not initial CAPEX.** Annualization converts investment into an equivalent €/year burden.
6. **Public data, proxies and assumptions must be distinguished.** Transparency matters more than false precision.

## 14. Limitations

- electrical subsystem only; thermal energy dominates important ceramic processes but is outside v1;
- representative 15 GWh/year load scale, not measured plant data;
- deterministic load shape, not a factory schedule;
- PVGIS-calibrated representative profile, not raw committed PVGIS hourly output;
- OMIE-calibrated wholesale-price proxy, not a complete industrial tariff;
- constant annual grid-emission factor;
- no taxes, demand charges, PPA/hedging structure or supplier contract;
- no battery degradation/replacement, PV degradation, salvage value or tax treatment;
- PV-only battery charging; no grid arbitrage;
- pre-feasibility economics only.

## 15. What this case does not prove

It does not prove that a real ceramic factory should install 2.97 MW PV, that batteries are uneconomic, or that a 40% reduction target will always require storage. Those conclusions would require facility-specific load data, site constraints, actual commercial terms and detailed engineering.

The defensible claim is narrower: **under a transparent, public-data-calibrated representative electrical case, IEL produces reproducible and interpretable pre-feasibility results.**
