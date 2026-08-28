# Industry Cases — Junior Engineer Practice

These mini-cases are designed to train judgement, not memory. Try to answer each one before reading the suggested response.

## 1. Impossible peak demand

**Situation:** Annual electricity use is 15 GWh/year. Reported peak demand is 0.9 MW.

**Check:** `15,000 MWh / 8,760 h ≈ 1.71 MW average load`.

**Better response:** The data are inconsistent if they describe the same boundary and period. Confirm the meter, time period and units before modelling.

**Main lesson:** A simple sanity check can be more valuable than a complex model built on bad inputs.

## 2. Missing hourly data

**Situation:** A non-leap-year CSV contains 8,759 rows.

**Weak response:** Duplicate the last hour and continue.

**Better response:** Identify the missing timestamp, understand the source problem, check timezone / duplicates and document any treatment.

**Main lesson:** Time-series quality is part of engineering because chronology affects load, PV, prices and battery SOC.

## 3. Supplier promises 40% savings

**Situation:** “Our battery can reduce your electricity cost by 40%.”

**Better questions:** 40% of which cost? What baseline? What tariff? What battery MW/MWh? What efficiency, degradation, dispatch, CAPEX, O&M and warranty?

**Main lesson:** A percentage is not testable until the baseline and assumptions are defined.

## 4. Battery is zero

**Situation:** The economic optimum selects no battery.

**Bad conclusion:** “Batteries are useless in industry.”

**Better conclusion:** Under the current assumptions, storage is not cost-optimal in this case. Different economics, tariff structures, operating needs or carbon constraints may change that conclusion.

**Main lesson:** Use conditional language and do not generalize one case to an entire technology.

## 5. PV optimum reaches the model limit

**Situation:** Optimal PV equals the maximum capacity allowed by the input bound.

**Better response:** Check whether the bound represents a real physical limit or is artificially restricting the solution. If justified, test a higher bound.

**Main lesson:** A result on a model bound may be telling you more about the bound than about the unconstrained optimum.

## 6. Positive NPV, high uncertainty

**Situation:** NPV is positive, but the model uses a wholesale-price proxy and public CAPEX benchmarks.

**Bad conclusion:** “Approve the investment.”

**Better conclusion:** The result supports further study. Replace proxies with real tariff, site and supplier information and test downside cases before an investment decision.

**Main lesson:** Economic attractiveness and decision readiness are different questions.

## 7. 40% carbon target becomes binding

**Situation:** The economic optimum already reduces electrical CO₂ by about 30%. A 20% target changes nothing. A 40% target changes the design and storage enters.

**Why:** The 20% requirement is already satisfied. At 40%, the carbon constraint becomes binding and forces the optimizer to reduce emissions further.

**Main lesson:** Identify which constraint is actively shaping the design.

## 8. Manager wants an answer today

**Situation:** Real interval data and supplier quotations are not available yet.

**Weak responses:** “I cannot say anything” or “Here is the final answer.”

**Better response:** Prepare a clearly labelled screening using explicit assumptions. State what is known, what is estimated and what must be validated next.

**Main lesson:** Speed and engineering honesty can coexist.

## Questions to reuse in any case

- Where did this number come from?
- Is it measured, derived, a proxy or an assumption?
- What period and unit does it use?
- What is missing?
- Does the result make physical sense?
- Is the result close to a model limit?
- Which assumption matters most?
- What would make the conclusion invalid?
- What should we ask for next?
