"""Central beginner-friendly glossary for energy, economics and optimization terms."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GlossaryTerm:
    term_id: str
    term: str
    full_name: str
    plain_language_definition: str
    technical_definition: str
    unit_if_applicable: str = "—"
    example: str = ""
    related_terms: tuple[str, ...] = ()
    why_it_matters: str = ""
    common_confusion: str = ""


def _g(i,t,f,p,tech,u="—",ex="",r=(),why="",conf=""):
    return GlossaryTerm(i,t,f,p,tech,u,ex,r,why,conf)

GLOSSARY = {
    "power": _g("power","Power","Power","How fast energy is being used or delivered at an instant.","Rate of energy transfer.","kW / MW","1 MW sustained for 2 hours delivers 2 MWh.",( "energy",),"PV and battery power limits control instantaneous flows.","MW is power, not annual energy."),
    "energy": _g("energy","Energy","Energy","The quantity of electricity used, produced or stored over time.","Power integrated over time.","kWh / MWh","1 MW for 1 hour = 1 MWh.",( "power",),"Annual load, PV production and battery energy are energy quantities.","MWh is not the same as MW."),
    "pv": _g("pv","PV","Photovoltaic","Solar-electric technology that converts sunlight into electricity.","In OptiDecarb, hourly PV energy equals installed PV power times a normalized hourly capacity factor and interval duration.","kW / MW capacity; kWh / MWh energy","3 MW of PV can never mean 3 MWh/year; capacity and production are different.",( "capacity_factor","power","energy"),"PV is the onsite generation technology sized by the optimizer.","PV capacity is power; PV generation is energy."),
    "capacity_factor": _g("capacity_factor","CF","Capacity Factor","How much energy a generator actually produces relative to running at rated power all the time.","Actual generation divided by rated capacity times available hours.","% / dimensionless","A 20% annual CF does not mean a solar panel is 20% efficient.",( "pv","energy"),"It converts PV capacity into an hourly production profile.","Capacity factor is not conversion efficiency."),
    "battery_energy": _g("battery_energy","Battery energy","Battery Energy Capacity","How much electrical energy the battery can store.","Nominal storage capacity used with SOC bounds.","kWh / MWh","A 4 MWh battery contains 2 MWh at 50% SOC before other constraints.",( "battery_power","soc"),"It controls how long energy can be shifted.","Energy capacity does not say how fast the battery can charge/discharge."),
    "battery_power": _g("battery_power","Battery power","Battery Power Capacity","How quickly the battery can charge or discharge.","Maximum AC-side charge/discharge rate.","kW / MW","A 2 MW / 4 MWh battery could theoretically discharge at 2 MW for about 2 hours before SOC/efficiency constraints.",( "battery_energy","soc"),"It limits the instantaneous rate of storage operation.","MW and MWh describe different battery dimensions."),
    "soc": _g("soc","SOC","State of Charge","How much energy is currently stored in the battery.","Stored energy divided by nominal battery energy capacity when expressed as a percentage.","% or kWh/MWh","A 4 MWh battery at 50% SOC stores about 2 MWh.",( "battery_energy","cyclic_soc"),"SOC decides whether the battery can absorb more energy or discharge.","SOC is not battery efficiency."),
    "cyclic_soc": _g("cyclic_soc","Cyclic SOC","Cyclic State of Charge Boundary","A rule forcing the battery to end the model horizon with the same stored-energy condition it started with.","OptiDecarb enforces the annual SOC boundary to prevent artificial free boundary energy.","—","Without this rule, an optimizer could start full for free or finish empty to improve the objective.",( "soc","constraint"),"It makes annual battery economics fairer and reproducible.","It is a modelling boundary condition, not a claim that a real battery resets each year."),
    "capex": _g("capex","CAPEX","Capital Expenditure","Money spent upfront to build or purchase long-lived assets.","Initial investment in PV and battery capacity before annualization.","€","A €2 million PV installation is CAPEX, not €2 million/year.",( "opex","annualized_capex","crf"),"Investment cost is a key sizing driver.","Initial CAPEX and annualized CAPEX are not the same."),
    "opex": _g("opex","OPEX","Operating Expenditure","Recurring cost of operating and maintaining equipment.","Annual operating/maintenance expenditure modeled as a capacity-based yearly cost.","€/year","Annual PV maintenance is OPEX.",( "capex",),"Ignoring OPEX would overstate project value.","OPEX is recurring; CAPEX is upfront."),
    "annualized_capex": _g("annualized_capex","Annualized CAPEX","Annualized Capital Expenditure","The equivalent yearly cost of an upfront investment.","Initial CAPEX multiplied by a capital recovery factor based on lifetime and WACC.","€/year","A €2M asset may correspond to a much smaller annualized cost depending on lifetime and WACC.",( "capex","crf","wacc"),"It lets the optimizer compare investment and yearly grid costs in the same units.","It is not another payment on top of initial CAPEX; it is an equivalent-cost representation used in the objective."),
    "wacc": _g("wacc","WACC","Weighted Average Cost of Capital","The annual return expected by the providers of capital financing a project.","Discount/financing rate used by OptiDecarb in CRF and NPV calculations.","%","Higher WACC raises annualized capital cost and discounts future savings more heavily.",( "crf","npv","annualized_capex"),"It changes the attractiveness of capital-intensive PV and batteries.","WACC is not an electricity price, profit margin or inflation rate."),
    "crf": _g("crf","CRF","Capital Recovery Factor","A factor that converts an upfront investment into an equivalent annual cost.","CRF = r(1+r)^n / ((1+r)^n - 1), where r is WACC and n is lifetime.","1/year","CAPEX × CRF gives equivalent annualized CAPEX.",( "wacc","annualized_capex","capex"),"It puts multi-year assets on an annual cost basis.","CRF is a conversion factor, not a project return."),
    "npv": _g("npv","NPV","Net Present Value","What future project cash flows are worth today after subtracting the initial investment.","Discounted present value of modeled future annual cash flows minus initial CAPEX.","€","NPV > 0 means modeled discounted benefits exceed CAPEX under the chosen assumptions.",( "wacc","capex","payback"),"It incorporates the time value of money.","Positive NPV is not an automatic build recommendation; OptiDecarb is pre-feasibility."),
    "payback": _g("payback","Payback","Simple Payback Period","How many years of constant annual operating savings are needed to recover the initial investment.","Initial CAPEX divided by modeled annual operating cash flow.","years","€2M CAPEX / €250k annual cash flow = 8-year simple payback.",( "npv","capex"),"It is intuitive for screening.","Simple payback ignores the time value of money, unlike NPV."),
    "baseline": _g("baseline","Baseline","Baseline Scenario","The reference case before adding the new investment.","In OptiDecarb the baseline is grid-only electricity supply using the same load and price series.","—","Savings and CO2 reductions are measured relative to baseline.",( "objective_function","abatement_cost"),"A comparison needs a consistent reference.","Baseline is not necessarily business-as-usual forever; it is the defined reference model."),
    "lp": _g("lp","LP","Linear Programming","A mathematical method that chooses the best values for variables while obeying linear rules.","Optimization with a linear objective and linear equality/inequality constraints.","—","OptiDecarb chooses PV MW, battery MWh/MW and hourly dispatch to minimize annualized cost.",( "decision_variable","objective_function","constraint"),"LP makes the sizing problem transparent and efficiently solvable over 8,760 hours.","The solver does not 'predict' the future; it optimizes the stated model."),
    "decision_variable": _g("decision_variable","Decision variable","Decision Variable","A quantity the optimizer is allowed to choose.","An unknown variable solved by the LP.","varies","PV capacity, battery energy/power and hourly dispatch are decision variables.",( "lp","constraint","objective_function"),"They are the decisions whose values define the optimized system.","Inputs such as WACC are parameters, not decision variables."),
    "objective_function": _g("objective_function","Objective","Objective Function","The number the optimizer tries to make as small as possible.","OptiDecarb minimizes annualized PV + battery cost + grid purchases - export revenue.","€/year","Two feasible systems are compared by their objective cost.",( "lp","constraint","baseline"),"It mathematically defines what 'economic optimum' means.","The objective does not include every real-world consideration."),
    "constraint": _g("constraint","Constraint","Optimization Constraint","A rule the optimizer is not allowed to violate.","Linear equality or inequality defining the feasible set.","—","Energy balance, SOC limits, battery power limits and carbon targets are constraints.",( "binding","infeasible","lp"),"Constraints keep optimization physically/logically meaningful.","A cheap solution that violates a constraint is not feasible."),
    "binding": _g("binding","Binding","Binding Constraint","A constraint that is active at the optimum and is directly limiting the solution.","A constraint with approximately zero slack within numerical tolerance.","—","If the economic optimum cuts CO2 by 30.4%, a 20% target is non-binding but a solved 40% target can be binding.",( "constraint","carbon_target","objective_function"),"It shows which requirement is actively shaping the design.","A constraint can exist in the model without being binding."),
    "infeasible": _g("infeasible","Infeasible","Infeasible Optimization Problem","No solution can satisfy all current constraints simultaneously.","The feasible set is empty under the selected inputs/bounds.","—","A very strict carbon target plus tight PV/battery bounds can be infeasible.",( "constraint","binding"),"It distinguishes impossible combinations from a solver crash.","Infeasible does not mean the solver is broken."),
    "self_consumption": _g("self_consumption","Self-consumption","PV Self-Consumption Ratio","The share of generated PV electricity that stays onsite instead of being exported.","PV used onsite divided by total PV generation.","%","If PV generates 100 MWh and 90 MWh stays onsite, self-consumption is 90%.",( "self_sufficiency","pv"),"It shows what happens to PV electricity.","It does not tell how much total site demand is covered onsite."),
    "self_sufficiency": _g("self_sufficiency","Self-sufficiency","Electrical Self-Sufficiency Ratio","The share of site electricity demand covered without grid imports.","(Load - grid import) / load.","%","If a site needs 100 MWh and imports 70 MWh, self-sufficiency is 30%.",( "self_consumption","baseline"),"It measures dependence on grid electricity.","High self-consumption can coexist with modest self-sufficiency."),
    "grid_emission_factor": _g("grid_emission_factor","Grid EF","Grid Emission Factor","The modeled CO2-equivalent intensity assigned to imported grid electricity.","Mass of CO2-equivalent per unit of imported electricity.","kgCO2eq/MWh","108 kgCO2eq/MWh means 1,000 MWh of imports corresponds to about 108 tCO2eq in this accounting method.",( "carbon_target","abatement_cost"),"It converts grid purchases into modeled operational emissions.","It is an accounting factor, not the emissions of each electron at a specific instant."),
    "carbon_target": _g("carbon_target","CO2 target","Carbon Reduction Target","The minimum emissions reduction required relative to baseline.","Scenario emissions <= (1-target) × baseline emissions.","%","40% target means modeled grid-related emissions must be at least 40% below baseline.",( "binding","baseline","abatement_cost"),"It shows how deeper decarbonization can change sizing and cost.","It is not renewable share or self-sufficiency."),
    "abatement_cost": _g("abatement_cost","Abatement cost","CO2 Abatement Cost","The change in annualized cost per tonne of CO2 avoided.","(Scenario annualized cost - baseline annual cost) / avoided tCO2.","€/tCO2","Negative means the modeled emissions reduction also lowers annualized cost; positive means deeper reduction costs more.",( "baseline","carbon_target"),"It links economic and carbon outcomes.","Always interpret it with the model boundary and baseline."),
    "sensitivity": _g("sensitivity","Sensitivity","Sensitivity Analysis","Change one assumption and observe how the optimized result changes.","Deterministic one-at-a-time what-if analysis.","—","Compare optimal PV at 0.8×, 1.0× and 1.2× PV CAPEX.",( "proxy","model_assumption"),"It identifies influential assumptions and robustness.","It is not a forecast, probability model or Monte Carlo simulation."),
    "break_even": _g("break_even","Break-even bracket","Break-Even Region","A tested interval where the preferred solution changes.","Observed range between tested sensitivity points around a transition.","varies","If battery > 0 at 0.74× CAPEX and =0 at 0.76×, the tested break-even lies between them.",( "sensitivity",),"It helps locate economic thresholds.","A coarse sensitivity grid does not justify an exact break-even value."),
    "proxy": _g("proxy","Proxy","Proxy Value","An approximation used when the exact facility-specific value is unavailable or unsuitable.","A surrogate input chosen from related public evidence and explicitly classified as such.","varies","OMIE day-ahead prices are used as a wholesale energy-price proxy, not as a complete industrial electricity bill.",( "derived_value","model_assumption"),"Proxies make transparent screening possible without pretending to have private plant data.","Proxy does not mean measured plant value."),
    "derived_value": _g("derived_value","Derived value","Derived Public Value","A value calculated from published source values rather than quoted directly.","Transparent transformation of one or more published inputs.","varies","OptiDecarb derives a grid emission factor from published generation emissions divided by published electricity generation.",( "proxy","model_assumption"),"It preserves traceability while allowing useful engineering quantities to be built.","It should never be presented as directly published by the source."),
    "model_assumption": _g("model_assumption","Assumption","Model Assumption","An explicit modeling choice used when a unique real-world value is unavailable or the model needs a simplifying parameter.","A documented, changeable parameter tested through validation/sensitivity where relevant.","varies","5% WACC is a screening assumption, not a claim about a specific ceramic company.",( "proxy","sensitivity"),"Explicit assumptions are better than hidden precision.","An assumption is not automatically random or arbitrary; it must be documented and defensible."),
    "prefeasibility": _g("prefeasibility","Pre-feasibility","Pre-Feasibility Screening","An early-stage analysis used to identify promising configurations and important uncertainties.","Screening before detailed engineering, quotations, permitting and financing diligence.","—","OptiDecarb can show whether ~3 MW PV is economically interesting under assumptions, but cannot replace a supplier design or grid study.",( "model_assumption","sensitivity"),"It defines the correct level of confidence in model outputs.","Pre-feasibility is not a final investment recommendation."),
    "hours8760": _g("hours8760","8,760 h","Full-Year Hourly Model","A non-leap year contains 24 × 365 = 8,760 hourly periods.","OptiDecarb optimizes every validated hour rather than using annual averages.","hours/year","A chart may display one week, while the optimization still includes all 8,760 hours.",( "lp","pv","soc"),"Hourly coincidence drives PV value, battery behavior and price exposure.","An annual-average model can hide timing effects."),
    "public_data": _g("public_data","Public data","Public Sector Data","Published aggregate evidence from institutions, sector bodies or official market/system sources.","Externally sourced data with provenance metadata.","varies","ASCER sector energy statistics and Red Eléctrica system totals are public evidence.",( "representative_model","real_plant_data"),"It anchors the representative case in real evidence.","Aggregate public data are not plant-specific measurements."),
    "representative_model": _g("representative_model","Representative model","Representative Case Model","A constructed engineering case calibrated to public evidence and explicit assumptions.","Synthetic hourly profiles and case parameters designed to be plausible at a representative scale, not copied from one facility.","varies","The Castellón case uses a rounded 15 GWh/year scale and deterministic hourly shape.",( "public_data","real_plant_data"),"It enables reproducible screening without private company data.","Representative does not mean average or exact for every plant."),
    "real_plant_data": _g("real_plant_data","Plant data","Real Plant Data","Facility-specific measurements, contracts and engineering details.","Private or measured data tied to one actual site.","varies","A real 15-minute load profile or signed electricity contract would be plant data.",( "public_data","representative_model"),"It would be needed for site-specific investment decisions.","OptiDecarb v1 does not claim to contain it."),
}

REQUIRED_ACRONYMS = ("pv", "soc", "capex", "opex", "wacc", "crf", "npv", "lp", "capacity_factor")


def get_term(term_id: str) -> GlossaryTerm:
    try:
        return GLOSSARY[term_id]
    except KeyError as exc:
        raise KeyError(f"Unknown glossary term_id: {term_id}") from exc


def validate_glossary() -> None:
    ids = set(GLOSSARY)
    for key, term in GLOSSARY.items():
        if key != term.term_id:
            raise ValueError(f"Glossary key/id mismatch: {key}")
        required = (
            term.term, term.full_name, term.plain_language_definition,
            term.technical_definition, term.why_it_matters, term.common_confusion,
        )
        if any(not value.strip() for value in required):
            raise ValueError(f"Glossary term {key} has an empty required field")
        missing = set(term.related_terms) - ids
        if missing:
            raise ValueError(f"Glossary term {key} references unknown terms: {sorted(missing)}")
    for acronym in REQUIRED_ACRONYMS:
        term = get_term(acronym)
        if term.term == term.full_name:
            raise ValueError(f"Acronym {acronym} has no expanded full name")


def term_help(term_id: str) -> str:
    term = get_term(term_id)
    parts = [
        f"**{term.term} — {term.full_name}**",
        term.plain_language_definition,
        f"**Technical definition:** {term.technical_definition}",
    ]
    if term.unit_if_applicable != "—":
        parts.append(f"**Unit:** {term.unit_if_applicable}")
    if term.example:
        parts.append(f"**Example:** {term.example}")
    parts.extend([
        f"**Why it matters:** {term.why_it_matters}",
        f"**Common confusion:** {term.common_confusion}",
    ])
    return "\n\n".join(parts)
