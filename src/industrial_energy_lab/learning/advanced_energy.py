"""Deterministic advanced learning content for OptiDecarb.

This module contains educational constants and pure helpers only. It deliberately
uses frozen, already-validated OptiDecarb case results and does not change the
engineering model or perform network calls.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormulaLesson:
    lesson_id: str
    title: str
    formula: str
    units: str
    intuition: str
    example: str
    common_error: str


@dataclass(frozen=True)
class PredictionLesson:
    lesson_id: str
    change: str
    question: str
    options: tuple[str, ...]
    correct: str
    before: str
    after: str
    why: str
    next_check: str


FORMULA_LESSONS = (
    FormulaLesson(
        "average_demand",
        "Average electrical demand",
        "Average MW = annual MWh / annual hours",
        "MWh / h = MW",
        "Annual energy becomes much easier to judge when translated into an average power level.",
        "15,000 MWh / 8,760 h ≈ 1.71 MW.",
        "Comparing annual MWh directly with a peak MW value without converting the units.",
    ),
    FormulaLesson(
        "load_factor",
        "Load factor",
        "Load factor = average demand / peak demand",
        "MW / MW = dimensionless",
        "It tells you how continuously the site uses its available peak demand.",
        "1.71 MW / 2.00 MW ≈ 85.7%.",
        "Treating load factor as an efficiency or a percentage of energy saved.",
    ),
    FormulaLesson(
        "pv_generation",
        "Approximate PV annual generation",
        "PV MWh ≈ MWp × 1,000 × yield kWh/kWp / 1,000",
        "MWp × kWh/kWp = MWh",
        "PV capacity becomes annual energy through the local solar yield.",
        "3 MWp × 1,500 kWh/kWp ≈ 4,500 MWh/year.",
        "Confusing MWp capacity with MWh annual production.",
    ),
    FormulaLesson(
        "battery_duration",
        "Battery nominal duration",
        "Duration h ≈ battery MWh / battery MW",
        "MWh / MW = h",
        "MW tells you how fast the battery can move energy; MWh tells you how much it stores.",
        "4 MWh / 2 MW = 2 h before usable-SOC and efficiency limits.",
        "Saying a 4 MWh battery can provide 4 MW for four hours.",
    ),
    FormulaLesson(
        "emissions",
        "Grid-related electrical emissions",
        "tCO₂ = grid MWh × tCO₂/MWh",
        "MWh × tCO₂/MWh = tCO₂",
        "The result is only as broad as the electricity boundary and emission factor used.",
        "10,000 MWh × 0.108 tCO₂/MWh ≈ 1,080 tCO₂.",
        "Calling an electrical-emissions result total factory decarbonization.",
    ),
    FormulaLesson(
        "simple_payback",
        "Simple payback",
        "Payback years ≈ initial CAPEX / annual saving",
        "€ / (€/year) = years",
        "It is a quick screening metric, not a complete discounted cash-flow result.",
        "€2.0m / €0.20m per year ≈ 10 years.",
        "Using payback as the only investment metric or confusing it with NPV.",
    ),
)


PREDICTION_LESSONS = (
    PredictionLesson(
        "electricity_price_up",
        "Electricity price +20%",
        "Before looking at the result, what direction do you expect for optimal PV capacity?",
        ("Increase", "Decrease", "Stay approximately unchanged"),
        "Increase",
        "2.972 MWp",
        "3.193 MWp",
        "More expensive grid electricity makes onsite PV generation more valuable under the current assumptions.",
        "Check whether the conclusion survives a real plant tariff rather than only the wholesale-price proxy.",
    ),
    PredictionLesson(
        "pv_capex_up",
        "PV CAPEX +20%",
        "What direction do you expect for optimal PV capacity?",
        ("Increase", "Decrease", "Stay approximately unchanged"),
        "Decrease",
        "2.972 MWp",
        "2.788 MWp",
        "Higher PV investment cost weakens the value of additional PV capacity.",
        "A budget EPC quotation would improve this assumption more than adding extra decimal precision to the model.",
    ),
    PredictionLesson(
        "wacc_up",
        "WACC 5% → 6%",
        "What direction do you expect for optimal PV capacity?",
        ("Increase", "Decrease", "Stay approximately unchanged"),
        "Decrease",
        "2.972 MWp",
        "2.870 MWp",
        "A higher cost of capital penalizes upfront CAPEX more strongly when annualized and discounted.",
        "Confirm the finance hurdle rate used for the real investment decision.",
    ),
    PredictionLesson(
        "carbon_20_to_40",
        "Minimum electrical CO₂ target 20% → 40%",
        "What qualitative change do you expect?",
        ("No system change", "More PV and storage may appear", "PV disappears"),
        "More PV and storage may appear",
        "20%: 2.97 MWp PV, 0 MWh BESS",
        "40%: ~4.25 MWp PV, ~2.46 MWh BESS",
        "The economic optimum already achieves about 30.4% electrical CO₂ reduction, so 20% is non-binding while 40% forces a different solution.",
        "Check whether the CO₂ boundary and grid factor match the company's actual target definition.",
    ),
    PredictionLesson(
        "battery_capex_down",
        "Battery CAPEX -20%",
        "Does a 20% cheaper battery automatically enter the economic optimum?",
        ("Yes", "No"),
        "No",
        "0 MWh BESS",
        "0 MWh BESS",
        "Under the frozen Castellón assumptions, the reduction is not enough to make storage economic in the unconstrained optimum.",
        "Do not generalize this result to resilience, demand charges or grid services that are outside Model v0.3.0.",
    ),
)


CARBON_FRONTIER = (
    {"target_pct": 0, "pv_mw": 2.972, "battery_mwh": 0.00, "battery_mw": 0.00, "annualized_cost_eur": 880203, "binding": False},
    {"target_pct": 20, "pv_mw": 2.972, "battery_mwh": 0.00, "battery_mw": 0.00, "annualized_cost_eur": 880203, "binding": False},
    {"target_pct": 30, "pv_mw": 2.972, "battery_mwh": 0.00, "battery_mw": 0.00, "annualized_cost_eur": 880203, "binding": False},
    {"target_pct": 40, "pv_mw": 4.25, "battery_mwh": 2.46, "battery_mw": 0.57, "annualized_cost_eur": 927346, "binding": True},
    {"target_pct": 50, "pv_mw": 5.34, "battery_mwh": 6.83, "battery_mw": 1.45, "annualized_cost_eur": 1007628, "binding": True},
)


TRACEABILITY_CARDS = (
    {
        "result": "~2.97 MWp economic PV optimum",
        "knows": "The supplied 8,760-hour load, PV profile and explicit optimization constraints.",
        "assumes": "PV CAPEX, electricity-price proxy, export value, WACC and project horizon.",
        "does_not_know": "Real roof/land layout, structural limits, exact grid connection, final EPC price or plant-specific tariff.",
    },
    {
        "result": "~30.4% electrical CO₂ reduction",
        "knows": "Grid imports in the modeled electrical balance and the stated grid-emission factor.",
        "assumes": "A constant electricity emission factor and no export CO₂ credit.",
        "does_not_know": "Kiln/dryer gas, process emissions, future hourly grid factors or the company's full Scope 1–3 accounting boundary.",
    },
    {
        "result": "Battery = 0 in the economic optimum",
        "knows": "PV-only charging, battery efficiency, modeled CAPEX/OPEX and hourly electrical balance.",
        "assumes": "The modelled storage services and economic parameters represent the decision being screened.",
        "does_not_know": "Resilience value, demand charges, ancillary services, backup requirements or services outside Model v0.3.0.",
    },
)


SCREENING_VS_FEASIBILITY = (
    ("Load data", "Representative / validated interval profile", "Site meter exports reconciled with invoices and production context"),
    ("PV resource", "PVGIS-calibrated representative profile", "Site layout, shading, orientation and detailed yield assessment"),
    ("CAPEX", "Public benchmark / screening assumption", "Comparable EPC budget or firm quotations"),
    ("Electricity price", "Wholesale energy-price proxy", "Actual tariff, contract, network/capacity terms and taxes where relevant"),
    ("PV size", "Mathematical screening optimum", "Buildable configurations constrained by roof/land, grid and equipment choices"),
    ("Export", "Explicit modelling assumption", "Confirmed contractual / grid export conditions"),
    ("Decision", "Whether deeper study is justified", "Whether the project is mature enough for investment approval"),
)


TRANSFER_CASE = {
    "title": "Transfer case — lower-load-factor industrial site",
    "label": "Illustrative teaching case — not a measured company",
    "facts": (
        "Annual electricity consumption: 8.76 GWh/year",
        "Average demand: 1.00 MW",
        "Peak demand: 2.40 MW",
        "PV capacity limit from available area: 1.50 MWp",
        "Indicative PV yield: 1,500 kWh/kWp/year",
        "Energy-price screening assumption: 110 €/MWh",
        "Export value: 20 €/MWh",
    ),
    "questions": (
        "What is the approximate load factor?",
        "How much annual PV energy could 1.5 MWp produce before coincidence/export effects?",
        "Compared with Castellón, what does the much lower load factor make you want to inspect in the hourly profile?",
        "Would you trust an annual-energy-only PV sizing conclusion here? Why?",
    ),
    "worked": (
        "Load factor ≈ 1.00 / 2.40 = 41.7%.",
        "1.5 MWp × 1,500 kWh/kWp ≈ 2.25 GWh/year before coincidence/export effects.",
        "A lower load factor suggests stronger variation between low and high demand, so chronology and daytime coincidence matter even more.",
        "No. Annual totals do not reveal whether PV generation coincides with demand, so exports and onsite value could differ materially.",
    ),
}


INTERVIEW_DEFENCE = (
    ("Why 8,760 hours?", "Because PV coincidence, prices and battery SOC depend on timing; annual totals hide those interactions."),
    ("Why linear programming?", "The v0.3.0 objective and constraints are formulated linearly, allowing a transparent continuous capacity/dispatch optimization."),
    ("Why is battery zero?", "Under the current economic assumptions and services represented, storage does not reduce annualized cost enough to justify its CAPEX."),
    ("Why is 20% CO₂ non-binding but 40% binding?", "The economic optimum already reduces electrical CO₂ by about 30.4%; 20% adds no restriction, while 40% forces a different system."),
    ("Why call OMIE a proxy?", "It represents a wholesale energy-price component, not the complete plant-specific industrial electricity bill."),
    ("Why say around 3 MWp instead of 2.972 MWp?", "The solver is numerically precise, but screening-stage site, tariff and CAPEX inputs do not justify false engineering precision."),
)


def prediction_by_id(lesson_id: str) -> PredictionLesson:
    """Return one deterministic prediction lesson by ID."""
    return next(item for item in PREDICTION_LESSONS if item.lesson_id == lesson_id)
