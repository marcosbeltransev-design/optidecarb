"""Industrial-energy learning architecture for OptiDecarb v1.3.

This module contains deterministic educational content only. It deliberately
keeps the scope on industrial electricity, PV, batteries, techno-economics,
carbon, project development and the judgement expected from an early-career
energy engineer. It contains no solver logic and no network access.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Skill:
    skill_id: str
    group: str
    name: str
    understand: str
    do: str
    explain: str
    common_mistake: str
    practice: str


@dataclass(frozen=True)
class DiagnosticQuestion:
    question_id: str
    area: str
    prompt: str
    options: tuple[str, ...]
    correct_option: str
    why: str
    recommended_path: str


@dataclass(frozen=True)
class DataQualityCase:
    case_id: str
    title: str
    situation: str
    question: str
    options: tuple[str, ...]
    correct_option: str
    why: str
    first_action: str
    excel_check: str
    professional_lesson: str


@dataclass(frozen=True)
class DataRequestItem:
    item: str
    why_needed: str


@dataclass(frozen=True)
class PracticalTask:
    task_id: str
    title: str
    brief: str
    expected_output: str
    good_process: tuple[str, ...]
    main_lesson: str


SKILL_GROUPS = (
    "ENERGY FUNDAMENTALS",
    "INDUSTRIAL ENERGY DATA",
    "LOAD & METERING",
    "PV & BATTERY",
    "ENERGY MODELLING",
    "ENERGY ECONOMICS & TARIFFS",
    "OPTIMIZATION & SENSITIVITY",
    "DECARBONIZATION",
    "ENERGY PROJECT DEVELOPMENT",
    "SITE & OPERATIONS",
    "ENERGY SUPPLIERS & COMMUNICATION",
)

SKILLS = (
    Skill("units", "ENERGY FUNDAMENTALS", "Power, energy and units", "Understand kW/MW, kWh/MWh/GWh, €/MWh and tCO₂/MWh.", "Convert units and perform dimensional checks before modelling.", "Explain why MW and MWh answer different questions.", "Using the correct formula with the wrong unit.", "Energy Data Lab"),
    Skill("orders", "ENERGY FUNDAMENTALS", "Orders of magnitude", "Understand the typical scale of industrial load, PV generation and storage duration.", "Estimate average MW, PV annual MWh and battery hours before using a detailed model.", "Explain whether a number is plausible before discussing decimals.", "Trusting a precise output without a rough independent estimate.", "Energy Data Lab"),
    Skill("quality", "INDUSTRIAL ENERGY DATA", "Interval-data quality", "Understand missing intervals, duplicates, timezones, leap years, spikes, flatlines and locale problems.", "Find energy-data issues and decide whether to correct, question or document them.", "Explain why chronology matters for 8,760-hour modelling and battery SOC.", "Silently repairing data just to make the model run.", "Energy Data Lab"),
    Skill("excel", "INDUSTRIAL ENERGY DATA", "Fast checks in Excel", "Know practical checks using filters, MAX/MIN, COUNT, pivots, conditional formatting and charts.", "Explore a new energy file quickly before writing code.", "Describe how you would reproduce a sanity check in Excel.", "Assuming every professional check must start in Python.", "Energy Data Lab"),
    Skill("load", "LOAD & METERING", "Industrial load profile", "Understand annual consumption, average demand, peak demand, load factor and operating patterns.", "Spot inconsistent consumption/peak values and identify weekday, weekend and shutdown behaviour.", "Explain why annual MWh alone are not enough for PV or BESS sizing.", "Treating annual consumption as a complete description of demand.", "Energy Data Lab"),
    Skill("metering", "LOAD & METERING", "Meter boundary and interval meaning", "Understand import, export, net load, submeters and interval energy versus average power.", "Ask where a measurement comes from and what physical boundary it represents.", "Explain why 100 kWh in 15 minutes corresponds to 400 kW average power during that interval.", "Mixing interval energy with instantaneous/average power.", "Energy Data Lab + Site"),
    Skill("pv", "PV & BATTERY", "PV sizing intuition", "Understand MWp, yield, coincidence, self-consumption, exports and diminishing marginal value.", "Estimate annual PV generation and challenge whether a proposed size fits load and site constraints.", "Explain why more PV can increase exports and reduce the value of each extra MWp.", "Equating PV capacity with annual generation or assuming bigger is always better.", "PV/BESS Project Lab"),
    Skill("battery", "PV & BATTERY", "Battery power, energy and value", "Understand MW, MWh, duration, SOC, efficiency and the services represented in the model.", "Calculate duration and explain why storage may be absent economically but appear under stricter carbon constraints.", "Explain why a 2 MW / 4 MWh battery is about a two-hour battery before usable-SOC and losses.", "Saying battery = 0 means batteries are useless.", "PV/BESS Project Lab"),
    Skill("balance", "ENERGY MODELLING", "Hourly energy balance", "Understand how load, PV, battery and grid must balance every hour.", "Perform a hand check of a small dispatch and trace every MWh.", "Explain how annual totals can hide important timing effects.", "Trusting charts without checking conservation of energy.", "Learning Lab + Hourly Results"),
    Skill("assumptions", "ENERGY MODELLING", "Assumptions and traceability", "Distinguish measured data, official data, proxy, benchmark and model assumption.", "Maintain an energy assumptions log with source, confidence, impact and validation action.", "Trace a result back to its energy inputs and assumptions.", "Hiding assumptions inside code or spreadsheets.", "Energy Project Lab"),
    Skill("bill", "ENERGY ECONOMICS & TARIFFS", "Electricity-price and bill reality", "Understand that a wholesale price proxy is not a complete industrial electricity bill.", "Separate the modelled energy component from tariff, capacity, network, tax and supplier-contract effects.", "Explain why OMIE can be useful for screening without being the plant's real bill.", "Using OMIE as if it were the full electricity invoice.", "Energy Economics Lab"),
    Skill("economics", "ENERGY ECONOMICS & TARIFFS", "Techno-economics", "Understand CAPEX, OPEX, annual saving, WACC, CRF, NPV and payback.", "Build a simple energy business case and challenge it with sensitivity.", "Explain why a positive NPV supports further study but is not investment approval.", "Using payback as the only economic metric.", "Economics + Energy Project Lab"),
    Skill("optimization", "OPTIMIZATION & SENSITIVITY", "Optimization reasoning", "Understand objective, decision variables, constraints and binding limits.", "Check whether an optimum is shaped by a bound and explain why a carbon target changes the system.", "Explain the result without saying only 'the solver says so'.", "Treating the mathematical optimum as a build-ready design.", "Optimization + Decarbonization"),
    Skill("sensitivity", "OPTIMIZATION & SENSITIVITY", "Decision robustness", "Understand sensitivity as a way to test whether a recommendation survives plausible input changes.", "Identify key drivers such as electricity price, PV CAPEX and WACC.", "Explain the difference between a robust direction and a fragile result.", "Showing a sensitivity chart without asking what decision it changes.", "Sensitivity"),
    Skill("carbon", "DECARBONIZATION", "Electrical carbon boundary", "Understand baseline emissions, grid factors, CO₂ targets and the electricity-only boundary.", "Check CO₂ units and distinguish electrical reduction from total plant decarbonization.", "Explain why a 40% target can become binding while 20% is not.", "Claiming total industrial decarbonization from an electricity-only model.", "Decarbonization"),
    Skill("project", "ENERGY PROJECT DEVELOPMENT", "From screening to energy project", "Know screening, pre-feasibility, feasibility, site survey, EPC quotation, detailed engineering and commissioning.", "Match the confidence of an energy recommendation to the maturity of the project.", "Explain what should happen after a promising PV/BESS screening.", "Jumping from model result to construction decision.", "Energy Project Lab"),
    Skill("site", "SITE & OPERATIONS", "Energy site awareness", "Understand why meters, transformers, switchboards, SLDs, production schedules, access and shutdown windows matter.", "Prepare focused energy questions for a site visit without overstepping safety/competence limits.", "Explain which site facts could invalidate a desktop screening.", "Assuming the optimization model knows physical integration constraints.", "Site & Operations"),
    Skill("supplier", "ENERGY SUPPLIERS & COMMUNICATION", "PV/BESS quotation review", "Understand scope, exclusions, guarantees, MW/MWh, usable capacity, EPC and connection assumptions.", "Compare supplier offers on a common technical/commercial basis and ask for missing evidence.", "Explain why the lowest €/kWp or €/kWh is not automatically the best offer.", "Comparing headline prices without matching scope.", "Supplier Lab"),
    Skill("communication", "ENERGY SUPPLIERS & COMMUNICATION", "Energy recommendation communication", "Know how to explain the same energy result to engineering, operations, finance and management.", "Write a concise energy note and a 30-second recommendation with assumptions and next step.", "State what the model says, what it does not know and what should be checked next.", "Using complex language instead of clear engineering reasoning.", "Communication + Capstone"),
)

DIAGNOSTIC_QUESTIONS = (
    DiagnosticQuestion("d_units", "Foundations", "A 2 MW industrial load runs at that level for 3 hours. How much energy is used?", ("6 MWh", "6 MW", "0.67 MWh"), "6 MWh", "Power × time gives energy: 2 MW × 3 h = 6 MWh.", "Energy Data Lab"),
    DiagnosticQuestion("d_interval", "Metering", "A 15-minute meter interval records 100 kWh. What was the average power during that interval?", ("25 kW", "100 kW", "400 kW"), "400 kW", "0.25 h × 400 kW = 100 kWh. Interval energy and average power are not the same quantity.", "Energy Data Lab"),
    DiagnosticQuestion("d_peak", "Load", "A site reports 15 GWh/year and a 0.9 MW peak. What should you do first?", ("Accept it", "Check the data because average load is already about 1.71 MW", "Increase PV capacity"), "Check the data because average load is already about 1.71 MW", "15,000 MWh / 8,760 h ≈ 1.71 MW average load, which cannot exceed the true peak for the same boundary and period.", "Energy Data Lab"),
    DiagnosticQuestion("d_rows", "Data", "A non-leap hourly load file contains 8,759 timestamps. Best first action?", ("Duplicate the last row", "Find the missing interval and understand why it is missing", "Ignore one hour"), "Find the missing interval and understand why it is missing", "Chronology affects annual energy, PV coincidence, prices and battery SOC. Silent repair hides the data problem.", "Energy Data Lab"),
    DiagnosticQuestion("d_pv", "PV", "A 3 MWp PV system has an indicative yield of 1,500 kWh/kWp/year. Rough annual generation?", ("4.5 GWh", "2.0 GWh", "45 GWh"), "4.5 GWh", "3,000 kWp × 1,500 kWh/kWp = 4,500,000 kWh = 4.5 GWh.", "PV/BESS Project Lab"),
    DiagnosticQuestion("d_battery", "Battery", "A battery is rated 2 MW / 4 MWh. Approximate nominal duration at full power?", ("0.5 h", "2 h", "8 h"), "2 h", "Duration ≈ energy / power = 4 MWh / 2 MW = 2 h before usable-SOC and efficiency limits.", "PV/BESS Project Lab"),
    DiagnosticQuestion("d_omie", "Economics", "OptiDecarb uses an OMIE-calibrated electricity price. What should you call it?", ("The plant's full electricity bill", "A wholesale energy-price proxy", "The network tariff"), "A wholesale energy-price proxy", "It is useful for screening the energy component but does not represent all supplier, network, capacity and tax terms of a real industrial bill.", "Energy Economics Lab"),
    DiagnosticQuestion("d_npv", "Economics", "NPV is positive in the screening. Best conclusion?", ("Build immediately", "The project may justify deeper site-specific study", "NPV is irrelevant"), "The project may justify deeper site-specific study", "NPV is conditional on assumptions and project maturity; it is evidence, not approval.", "Energy Economics Lab"),
    DiagnosticQuestion("d_binding", "Optimization", "The economic optimum already reduces electrical CO₂ by ~30%. Is a 20% minimum target binding?", ("Yes", "No", "Always infeasible"), "No", "The unconstrained economic solution already satisfies the weaker target.", "Optimization & Decarbonization"),
    DiagnosticQuestion("d_supplier", "Supplier", "A battery supplier claims 40% bill savings. Best first question?", ("Can you make it 50%?", "40% of which bill components, against what baseline and tariff?", "Which battery colour is available?"), "40% of which bill components, against what baseline and tariff?", "A saving percentage is not testable until baseline, tariff scope and operating assumptions are defined.", "Supplier Lab"),
    DiagnosticQuestion("d_precision", "Communication", "The optimizer returns 2.972384 MWp. Best professional wording at screening stage?", ("Install exactly 2.972384 MWp", "Around 3 MWp under the current assumptions", "The number is meaningless"), "Around 3 MWp under the current assumptions", "Model precision is not the same as site/design precision.", "Communication + Capstone"),
    DiagnosticQuestion("d_export", "Judgement", "You do not know whether PV export is allowed or compensated at the site. Best action?", ("Assume yes silently", "State the gap, explain why it matters and confirm it before a stronger recommendation", "Set export to zero for every project"), "State the gap, explain why it matters and confirm it before a stronger recommendation", "Export rules can materially change PV economics. Good energy engineering makes the uncertainty visible and proposes the next check.", "Energy Project Lab"),
)

DATA_QUALITY_CASES = (
    DataQualityCase("missing_hour", "8,759 hours", "A non-leap year load file has 8,759 hourly rows.", "What is the first professional action?", ("Duplicate one row", "Locate the missing timestamp", "Ignore it"), "Locate the missing timestamp", "A missing hour can affect annual consumption and time-dependent PV/BESS dispatch.", "Compare the timestamp sequence with the expected calendar and ask how the export was created.", "Use row count, sort timestamps, and compare expected versus actual intervals.", "Do not invent energy data just to satisfy the model contract."),
    DataQualityCase("duplicate", "Duplicate meter timestamp", "Two rows have the same timestamp but different kW values.", "What should you do?", ("Add them automatically", "Investigate meter/export logic before deciding", "Delete the larger value"), "Investigate meter/export logic before deciding", "The rows may represent a duplicate export, different meters or a timezone issue.", "Check meter ID, source system and timezone before aggregation.", "Use COUNTIF/conditional formatting and filter duplicate timestamps.", "Understand the metering boundary before correcting energy data."),
    DataQualityCase("leap_year", "8,784-hour leap year", "The 8,760-hour model receives 8,784 hourly values.", "Best response?", ("Delete any 24 rows", "Choose a modelling year and transform load, price and PV consistently", "Ignore the extra day in only the load file"), "Choose a modelling year and transform load, price and PV consistently", "Load, price and PV timelines must stay aligned.", "Define the study period and handle 29 February consistently across every series.", "Check row count, year and 29 February explicitly.", "Calendar alignment is part of the energy model, not data housekeeping."),
    DataQualityCase("negative_load", "Negative consumption readings", "The site-consumption meter contains negative values but is documented as import-only demand.", "What next?", ("Take absolute values", "Check sign convention and meter boundary", "Replace all negatives with zero"), "Check sign convention and meter boundary", "Negative values could indicate export, net metering or bad data.", "Confirm whether the signal is gross consumption, net grid flow or another meter.", "Filter values <0 and compare with meter documentation and nearby intervals.", "A surprising sign often reveals a boundary problem."),
    DataQualityCase("spike", "18 MW spike on a 2 MW site", "Typical demand is 1.5–2.0 MW but one hour shows 18 MW.", "Best first action?", ("Delete it", "Check physical plausibility and trace the raw reading", "Use 18 MW as the design peak"), "Check physical plausibility and trace the raw reading", "It could be a unit/scaling error, sensor issue or a real but unusual event.", "Compare transformer/equipment capacity, adjacent readings and the raw meter export.", "Sort descending, plot the series and inspect neighbouring intervals.", "Outliers require electrical/operational context before editing."),
    DataQualityCase("flatline", "Flatlined load signal", "Demand is exactly 1.700 MW for 36 consecutive hours although the process usually varies.", "What does this suggest?", ("Perfectly stable production", "Possible sensor/data freeze that needs checking", "Higher PV yield"), "Possible sensor/data freeze that needs checking", "Long exact repeats can indicate stale telemetry or fill-forward processing.", "Compare raw telemetry, missing-value treatment and operating logs.", "Use frequency checks and a line chart to spot repeated blocks.", "Clean-looking load data can still be wrong."),
    DataQualityCase("mixed_units", "kW and MW mixed", "One source file contains values around 1,700 and another around 1.7 under the same load column name.", "Likely risk?", ("Mixed units", "Battery degradation", "CO₂ target"), "Mixed units", "A factor of 1,000 often indicates kW versus MW.", "Confirm metadata and convert explicitly before combining files.", "Compare median/max by source and keep a unit column during import.", "Unit metadata belongs with the energy data."),
    DataQualityCase("interval_energy", "kWh interval treated as kW", "A 15-minute export contains 100 kWh per row but someone plots the values as 100 kW demand.", "What is wrong?", ("Nothing", "Energy per interval was confused with average power", "PV efficiency is too low"), "Energy per interval was confused with average power", "100 kWh over 0.25 h corresponds to 400 kW average power for that interval.", "Confirm whether each column is interval energy or demand power before aggregation.", "Check the source-unit label and calculate kW = kWh / 0.25 h for 15-minute data.", "Interval length is essential when converting energy to power."),
    DataQualityCase("decimal_separator", "European decimal separator", "A CSV imports `1,75` as text instead of 1.75 MW.", "Best action?", ("Ignore text rows", "Use the correct locale/decimal setting and verify totals", "Replace commas blindly"), "Use the correct locale/decimal setting and verify totals", "Locale can turn measurements into text and corrupt aggregation.", "Import using the documented locale and reconcile totals/max values with the source.", "Use Excel/Power Query locale settings instead of ad-hoc replacements.", "Energy-data ingestion should be reproducible."),
)

MENTAL_MODELS = (
    ("UNITS FIRST", "Check whether the energy, power, price and CO₂ units can physically combine."),
    ("ESTIMATE FIRST", "Calculate a rough MW, MWh, € or tCO₂ answer before running the full model."),
    ("FOLLOW THE ENERGY", "Ask where each MWh comes from and where it goes."),
    ("KNOW THE METER BOUNDARY", "A number is meaningless until you know what meter or system boundary it represents."),
    ("WHAT IS THE BASELINE?", "Savings and CO₂ reductions require a clear reference case."),
    ("FOLLOW THE MONEY", "Separate energy price, tariff effects, CAPEX, OPEX, savings and discounting."),
    ("WHAT IS NOT MODELLED?", "List site, tariff, operational or technical constraints absent from the screening."),
    ("WHAT WOULD CHANGE MY DECISION?", "Use sensitivity to identify the inputs that can change the recommendation."),
    ("IS THE RESULT NEAR A BOUND?", "A capacity or carbon limit may be shaping the optimizer's answer."),
    ("IS THE PRECISION REAL?", "Report only the precision supported by the data and project maturity."),
)

FIRST_DATA_REQUEST = (
    DataRequestItem("12–24 months of interval electricity data", "To understand hourly/quarter-hourly demand, peaks, operating patterns, seasonality and data gaps."),
    DataRequestItem("Meter description and units", "To know whether the series is kW, kWh, gross consumption, net grid import/export or a submeter."),
    DataRequestItem("Recent electricity invoices", "To reconcile annual MWh, maximum demand and modelled energy costs with what the site actually pays."),
    DataRequestItem("Electricity contract / tariff", "To understand fixed/indexed energy pricing and cost components not captured by a wholesale proxy."),
    DataRequestItem("Contracted power / maximum-demand terms", "To identify capacity-related costs and constraints outside the current energy-only objective."),
    DataRequestItem("Production calendar and shutdowns", "To explain load patterns and avoid treating planned outages as bad data."),
    DataRequestItem("Site location", "To choose a relevant solar resource and understand local project context."),
    DataRequestItem("Available roof / land and obvious shading constraints", "To test whether an attractive MWp value is physically plausible."),
    DataRequestItem("Existing PV / generation and how it is metered", "To establish the real baseline and avoid double-counting generation."),
    DataRequestItem("Transformer / connection information and single-line diagram if available", "To understand electrical integration and possible import/export limits."),
    DataRequestItem("Export permission / compensation", "Because export availability and value can materially change PV sizing and economics."),
    DataRequestItem("Corporate WACC / hurdle rate / project horizon", "To use company investment assumptions instead of inventing finance inputs."),
    DataRequestItem("Electrical CO₂ objective and reporting boundary", "To distinguish a cost-driven screening from a minimum electrical-decarbonization target."),
)

ASSUMPTIONS_LOG_EXAMPLE = (
    {"assumption": "Electricity energy price", "value": "OMIE-calibrated", "type": "Wholesale proxy", "confidence": "Medium", "impact": "High", "validate_with": "Real contract and invoices"},
    {"assumption": "PV CAPEX", "value": "700 €/kWp", "type": "Public benchmark", "confidence": "Medium", "impact": "High", "validate_with": "Comparable EPC quotations"},
    {"assumption": "PV yield", "value": "~1,617 kWh/kWp/y", "type": "PVGIS-calibrated profile", "confidence": "Medium/High for screening", "impact": "High", "validate_with": "Site layout / detailed yield study"},
    {"assumption": "WACC", "value": "5%", "type": "Model assumption", "confidence": "Low until confirmed", "impact": "Medium", "validate_with": "Finance / investment policy"},
    {"assumption": "Annual plant load", "value": "15,000 MWh", "type": "Representative case assumption", "confidence": "Case-specific", "impact": "High", "validate_with": "Real plant meter data"},
)

JUNIOR_DELIVERABLES = (
    ("Energy-data quality note", "What was wrong with the interval data, how it affects the analysis and what needs confirmation."),
    ("Energy assumptions log", "Price, PV yield, CAPEX, WACC, CO₂ factor and site assumptions with source and validation plan."),
    ("Energy-balance calculation note", "A traceable baseline or PV/BESS calculation that another engineer can reproduce."),
    ("PV/BESS supplier comparison", "Comparable technical scope, MW/MWh, price, guarantees, exclusions and open questions."),
    ("Five-line energy memo", "Site context, energy finding, key assumption, risk and next step."),
    ("One-slide energy business case", "PV/BESS scale, CAPEX, savings/NPV, CO₂, main uncertainty and next action."),
    ("Energy-project risk register", "Tariff, yield, grid/export, site, CAPEX and operational risks with mitigation."),
)

SITE_VISIT_BASICS = (
    "Confirm the electrical metering boundary and where the main meter / relevant submeters are.",
    "Ask for annual/interval demand, peak demand and whether the meter values are import, export or net flow.",
    "Ask about transformers, main switchboards and whether a current single-line diagram (SLD) is available.",
    "Observe roof/land availability, access, obvious shading and possible PV equipment locations.",
    "Confirm existing PV, inverters or other electrical generation and how they are metered.",
    "Understand production hours, planned shutdowns, critical loads and planned capacity expansions.",
    "Ask about export limits, grid studies and connection constraints relevant to PV/BESS.",
    "Discuss maintenance ownership, equipment access and feasible outage windows for installation.",
    "Follow site safety procedures; do not open live electrical equipment or inspect beyond your authorization/competence.",
)

VALIDATION_TYPES = (
    ("Energy-data validation", "Do timestamps, units, meter boundary and load values make sense?"),
    ("Energy-balance validation", "Does load = PV + battery + grid (with the model's defined flows) each hour?"),
    ("Benchmark validation", "Are PV yield, CAPEX, load factor and emissions in a plausible range?"),
    ("Economic validation", "Do modelled cost components reconcile with the intended tariff/price boundary?"),
    ("Code/regression validation", "Does the software reproduce frozen engineering cases after changes?"),
    ("Real-site validation", "Do actual site, contract, grid, supplier and operational constraints support the screening assumptions?"),
)

AI_ENGINEERING_RULES = {
    "use_well": (
        "Use AI to explain energy concepts, generate checks and propose alternative calculations.",
        "Use AI to help write analysis code/tests, then verify units, balances and frozen engineering cases.",
        "Ask AI for a first supplier-question list, then adapt it to the actual PV/BESS scope.",
        "Trace important prices, emission factors and technical claims back to credible sources.",
    ),
    "avoid": (
        "Do not paste confidential plant load, invoices or supplier information without authorization.",
        "Do not treat an AI estimate of PV yield, CAPEX or savings as engineering evidence.",
        "Do not accept a plausible energy answer without checking units and order of magnitude.",
        "Do not claim knowledge of a tariff, grid constraint or site condition that has not been verified.",
    ),
}

PRACTICAL_TASKS = (
    PracticalTask("task_data_30", "30-minute industrial load-data check", "You receive one year of hourly plant electricity data before a PV screening meeting.", "A short list of critical energy-data issues, usable fields and questions for the meter/data owner.", ("Check interval count/timestamps", "Confirm kW vs kWh and meter boundary", "Calculate annual MWh, average and peak MW", "Plot load and inspect outliers", "Write open questions"), "A structured energy-data check should come before optimization."),
    PracticalTask("task_baseline", "Build a five-minute electrical baseline", "Your manager asks for the scale of the site before the detailed model is ready.", "Annual MWh, average MW, peak MW, load factor, approximate energy cost and grid CO₂.", ("Check units", "Calculate average demand", "Compare average with peak", "Apply the stated €/MWh and tCO₂/MWh factors", "Label what the cost does not include"), "A quick baseline gives context and catches impossible inputs."),
    PracticalTask("task_supplier", "Prepare five PV/BESS supplier questions", "A supplier sends a headline €/kWp or €/kWh price with limited scope detail.", "Five questions that could materially change the technical or economic comparison.", ("Check MW/MWh and scope", "Check EPC/grid connection", "Check yield/efficiency assumptions", "Check guarantees/warranty", "Check exclusions and commercial basis"), "Comparable scope matters more than headline price."),
    PracticalTask("task_sensitivity", "Identify the key economic driver", "The PV screening looks attractive, but three assumptions are uncertain.", "A short sensitivity plan for electricity price, PV CAPEX and WACC, with a prediction before each run.", ("Choose plausible changes", "Predict direction", "Run one variable at a time", "Compare decision, not just numbers"), "Sensitivity should test whether the energy recommendation is robust."),
    PracticalTask("task_note", "Write a five-line energy recommendation", "The screening is preliminary but management wants an update.", "Context + energy finding + key assumption + energy/project risk + next validation step.", ("Use approximate sizing", "State the main missing site/tariff input", "Avoid build-ready wording", "Recommend one concrete next action"), "Clear energy communication is part of the engineering analysis."),
)

JOB_READINESS_MATRIX = (
    ("Check an industrial electricity dataset", "Energy Data Lab"),
    ("Calculate a quick electrical baseline", "Energy Data Lab + Baseline"),
    ("Estimate PV generation from MWp and yield", "PV/BESS Project Lab"),
    ("Explain battery MW/MWh and duration", "PV/BESS Project Lab"),
    ("Reconcile price proxy versus real electricity bill", "Energy Economics Lab"),
    ("Build and challenge a PV/BESS business case", "Economics + Sensitivity"),
    ("Review a PV/BESS supplier claim", "Supplier Lab"),
    ("Prepare questions for an energy site visit", "Energy Project & Site"),
    ("Defend an energy recommendation with assumptions and limits", "Capstone"),
    ("Explain an energy result in clear professional English", "Communication + Capstone"),
)

CAPSTONE = {
    "title": "Industrial PV + BESS screening",
    "context": "You are asked for a first electrical-decarbonization screening for an unnamed industrial site. The information is intentionally incomplete because real early-stage projects rarely start with perfect data.",
    "facts": (
        "Hourly load file: 8,759 rows for a non-leap year",
        "Reported annual grid electricity: approximately 8,760 MWh/year",
        "Reported peak demand: 1.8 MW",
        "Indicative energy price: 90 €/MWh (energy component only)",
        "PV yield assumption: 1,500 kWh/kWp/year",
        "PV CAPEX benchmark: 750 €/kWp",
        "Proposed PV concept: 3 MWp",
        "Proposed battery concept: 2 MW / 4 MWh",
        "Export value assumption: 35 €/MWh, but export permission is not confirmed",
        "Grid factor: 0.15 tCO₂/MWh",
    ),
    "questions": (
        "What energy-data problem must be resolved before calling the hourly profile validated?",
        "What is the rough average demand, and is it consistent with the 1.8 MW peak?",
        "What is the approximate grid energy cost using the supplied energy-price component?",
        "What are baseline grid emissions using the supplied factor?",
        "What rough annual PV generation would 3 MWp produce before hourly coincidence/export effects?",
        "What does 2 MW / 4 MWh tell you about the battery before efficiencies and usable SOC?",
        "Why can you not claim reliable bill savings from annual PV generation and the 90 €/MWh number alone?",
        "Name four energy/site data items you would request next.",
        "What three assumptions would you test first in sensitivity?",
        "Write a short recommendation for your manager: build now, stop, or continue to a site-specific study? Justify it.",
    ),
    "worked_solution": (
        "8,759 rows means at least one interval is missing or the calendar is inconsistent. Locate the gap and understand the export process before a full hourly PV/BESS dispatch.",
        "8,760 MWh / 8,760 h ≈ 1.0 MW average demand. That is below the 1.8 MW peak, so the basic order of magnitude is plausible.",
        "8,760 MWh × 90 €/MWh ≈ €788,400/year for the stated energy component only; it is not the complete industrial bill.",
        "8,760 MWh × 0.15 tCO₂/MWh ≈ 1,314 tCO₂/year for the defined electrical grid-import boundary.",
        "3,000 kWp × 1,500 kWh/kWp ≈ 4.5 GWh/year gross PV generation before hourly self-consumption/export effects.",
        "4 MWh / 2 MW ≈ 2 hours nominal duration before usable-SOC, efficiency, degradation and dispatch constraints.",
        "Savings depend on hourly load/PV coincidence, export permission/value, real tariff structure, supplier terms and other bill components. Annual generation × one price is only a rough first check.",
        "Request the complete interval data + meter definition, real invoices/contract, roof/land/site constraints, and transformer/grid/export information. Supplier quotations come after the basis is clearer.",
        "Test at least electricity-price basis, PV CAPEX and WACC; export value/permission is also a major scenario because it is currently uncertain.",
        "Recommend a corrected dataset and site-specific pre-feasibility study. The opportunity is large enough to investigate, but the current information is not investment-ready and should not be presented as a build decision.",
    ),
}

CASTELLON_COMMITTEE = (
    ("CFO", "Why should we spend roughly €2 million on PV?", "The current screening indicates a positive economic case under explicit assumptions, but I would validate the real tariff, site constraints and comparable EPC quotations before requesting investment approval."),
    ("Plant Operations", "Will PV or the battery affect production?", "The current model does not represent installation outages or every electrical integration constraint. I would confirm connection points, shutdown windows, critical-load requirements and maintenance access with the plant team."),
    ("Energy Manager", "Why is the battery zero in the economic optimum?", "Under the current prices, PV surplus and battery costs/losses, storage does not add enough economic value. That conclusion is conditional: storage appears when the CO₂ constraint becomes stricter."),
    ("Sustainability", "How credible is the ~30% CO₂ reduction?", "It is traceable for the modelled electrical boundary using grid imports and a documented grid factor. It is not a claim about total ceramic-process emissions or natural-gas use."),
    ("Management", "Do you recommend we build exactly 2.972 MWp?", "No. I would communicate the result as around 3 MWp under the current assumptions and recommend a site-specific study to test practical layouts, tariff, grid/export limits and supplier pricing."),
)


def diagnostic_summary(answers: Mapping[str, str]) -> dict[str, tuple[str, ...]]:
    """Return energy-learning strengths and practice areas without scoring."""
    by_area: dict[str, list[bool]] = {}
    for question in DIAGNOSTIC_QUESTIONS:
        if question.question_id not in answers:
            continue
        by_area.setdefault(question.area, []).append(answers[question.question_id] == question.correct_option)
    strengths: list[str] = []
    practise: list[str] = []
    paths: list[str] = []
    for area, results in by_area.items():
        if results and all(results):
            strengths.append(area)
        else:
            practise.append(area)
            for q in DIAGNOSTIC_QUESTIONS:
                if q.area == area and q.recommended_path not in paths:
                    paths.append(q.recommended_path)
    return {"strengths": tuple(strengths), "practise": tuple(practise), "recommended_paths": tuple(paths)}


def validate_readiness_catalog() -> None:
    if tuple(dict.fromkeys(SKILL_GROUPS)) != SKILL_GROUPS:
        raise ValueError("Duplicate skill group")
    skill_ids = [x.skill_id for x in SKILLS]
    if len(skill_ids) != len(set(skill_ids)):
        raise ValueError("Duplicate skill id")
    if {x.group for x in SKILLS} - set(SKILL_GROUPS):
        raise ValueError("Unknown skill group")
    qids = [x.question_id for x in DIAGNOSTIC_QUESTIONS]
    if len(qids) != len(set(qids)):
        raise ValueError("Duplicate diagnostic id")
    for q in DIAGNOSTIC_QUESTIONS:
        if q.correct_option not in q.options or not q.why or not q.recommended_path:
            raise ValueError(q.question_id)
    case_ids = [x.case_id for x in DATA_QUALITY_CASES]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate data-quality case id")
    for case in DATA_QUALITY_CASES:
        if case.correct_option not in case.options or not all((case.why, case.first_action, case.excel_check, case.professional_lesson)):
            raise ValueError(case.case_id)
    if len(FIRST_DATA_REQUEST) < 10:
        raise ValueError("First data request too short")
    if len(CAPSTONE["questions"]) != len(CAPSTONE["worked_solution"]):
        raise ValueError("Capstone question/solution mismatch")
