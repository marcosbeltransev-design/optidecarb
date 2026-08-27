# Industrial Energy Lab — From Zero to Understanding the Model

This guide assumes you know basic engineering mathematics but not energy optimization terminology.

## 1. Power and energy

**Power** is a rate. It answers “how fast?”. Units: kW or MW.

**Energy** is a quantity accumulated over time. Units: kWh or MWh.

```text
1 MW for 1 hour = 1 MWh
```

A 2 MW / 4 MWh battery can theoretically deliver 2 MW for about 2 hours before SOC, efficiency and operating limits are considered.

## 2. Industrial load

An hourly load profile tells IEL how much electricity the site needs in each hour. A non-leap year has:

```text
24 × 365 = 8,760 hours
```

Why not use one annual average? Because PV, prices and batteries depend on **timing**. The value of 1 MWh of solar electricity is different if the plant needs electricity at the same time or must export it.

## 3. PV — Photovoltaic

PV capacity is power (kW/MW). PV generation is energy (kWh/MWh).

IEL uses:

```text
PV generation[t] = PV capacity × capacity factor[t] × interval
```

**CF — Capacity Factor** describes output relative to continuous rated-power operation. It is not solar-panel efficiency.

## 4. Battery

A battery has two separate sizes:

- **energy capacity [MWh]** — how much can be stored;
- **power capacity [MW]** — how fast it can charge/discharge.

**SOC — State of Charge** is stored energy at a given time.

IEL models charge/discharge efficiency and uses a **cyclic SOC** boundary: the optimized year ends at the same SOC condition it started. This prevents free energy from model boundaries.

## 5. Grid

After PV and battery dispatch, remaining demand is imported from the grid. Surplus PV can be exported.

In the v1 optimization battery charging is restricted to PV allocation. IEL does not model grid-to-battery arbitrage.

## 6. Economics

**CAPEX — Capital Expenditure**: upfront investment.

**OPEX — Operating Expenditure**: recurring annual operating cost.

### WACC

**WACC — Weighted Average Cost of Capital** is the financing/discount rate used to value capital. Higher WACC generally makes capital-intensive options less attractive.

### CRF

**CRF — Capital Recovery Factor** converts upfront CAPEX into equivalent annual cost:

```text
CRF = r(1+r)^n / ((1+r)^n - 1)
Annualized CAPEX = CAPEX × CRF
```

Annualized CAPEX is not a second investment. It is an accounting representation that lets the optimizer compare investment with €/year grid and OPEX costs.

### NPV and payback

**NPV — Net Present Value** discounts future project cash flows to today and subtracts initial CAPEX.

- NPV > 0: positive modeled value under assumptions;
- NPV < 0: negative modeled value under assumptions.

A positive NPV is not automatically a build decision.

**Simple payback** = initial CAPEX / annual operating cash flow. It is intuitive but ignores the time value of money.

## 7. Optimization

**LP — Linear Programming** chooses decision variables while obeying constraints.

Decision variables include:

- PV capacity;
- battery energy capacity;
- battery power capacity;
- hourly PV/battery dispatch.

A **constraint** is a rule the optimizer cannot break: energy balance, SOC limits, power limits, PV availability or carbon target.

The **objective function** IEL minimizes is equivalent annualized system cost.

“Economic optimum” means lowest modeled annualized cost **within the defined model**. It does not mean best engineering design in every sense.

### Binding and infeasible

A **binding constraint** is active at the solution and limits it.

**Infeasible** means no solution satisfies all constraints simultaneously. It does not mean the solver crashed.

## 8. Carbon

IEL uses a grid-emission factor:

```text
CO2 = grid imports × grid emission factor
```

A 40% carbon target means modeled grid-related emissions must be at least 40% below baseline.

### Abatement cost

```text
Abatement cost
= (scenario annualized cost - baseline annual cost)
  / avoided tCO2
```

- negative: the modeled emissions reduction also saves annualized cost;
- positive: deeper reduction costs additional €/tCO₂.

## 9. Self-consumption vs self-sufficiency

These are easy to confuse.

**Self-consumption** asks: “What happens to my PV electricity?”

```text
PV kept onsite / PV generated
```

**Self-sufficiency** asks: “How much of my demand do I cover without the grid?”

```text
(load - grid import) / load
```

Example: PV generates 100 MWh, 95 MWh stays onsite, and annual load is 300 MWh. Self-consumption is 95%, while self-sufficiency is only about 32%.

## 10. Sensitivity

Sensitivity changes one assumption and resolves the model. It helps answer:

- What if electricity becomes more expensive?
- What if PV CAPEX is 20% lower?
- What if WACC is higher?
- When might storage enter the optimum?

It is not a forecast, Monte Carlo simulation or statement of probability.

## 11. Public data, proxy, derived value and assumption

These labels keep the case honest.

- **Public data:** published external evidence.
- **Derived value:** transparently calculated from published values.
- **Proxy:** approximation used when the exact plant value is unavailable.
- **Model assumption:** explicit screening choice.

A proxy is not plant data. An assumption is not automatically arbitrary.

## 12. Castellón ceramic case

The representative case uses public sector evidence and explicit assumptions, but no company-specific operating data.

The frozen case has 15 GWh/year load, approximately 2.97 MW optimal PV and no economic-optimum battery. At a binding 40% CO₂ target, more PV and storage enter.

Study `cases/ceramic_castellon/CASE_STUDY.md` for the full evidence chain.

## 13. What pre-feasibility means

IEL is for early-stage screening:

- compare configurations;
- understand important assumptions;
- identify promising ranges;
- examine carbon-cost trade-offs.

It does not replace supplier quotations, electrical/structural studies, permitting, detailed tariff/contracts, financing diligence or final investment approval.
