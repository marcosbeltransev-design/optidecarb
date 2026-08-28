"""Central catalog of student questions, guided experiments and common traps."""
from __future__ import annotations
from .models import GuidedExperiment, LearningQuestion

LEARNING_PATH = (
    ("FOUNDATIONS", ("power", "energy", "hours8760")),
    ("ENERGY SYSTEM", ("pv", "capacity_factor", "battery_energy", "battery_power", "soc", "cyclic_soc")),
    ("ECONOMICS", ("capex", "opex", "wacc", "crf", "annualized_capex", "npv", "payback")),
    ("OPTIMIZATION", ("lp", "decision_variable", "objective_function", "constraint", "binding", "infeasible")),
    ("DECARBONIZATION", ("baseline", "grid_emission_factor", "carbon_target", "abatement_cost", "sensitivity")),
    ("REAL APPLICATION", ("public_data", "proxy", "derived_value", "model_assumption", "representative_model", "prefeasibility")),
)

COMMON_TRAPS = (
    ("MW = MWh", "MW is power; MWh is energy. 2 MW for 3 h delivers 6 MWh."),
    ("PV capacity = PV generation", "Capacity is rated power; generation is energy accumulated over time."),
    ("Battery MW = battery MWh", "MW controls charge/discharge rate; MWh controls stored energy."),
    ("CAPEX = annualized CAPEX", "CAPEX is upfront investment; annualized CAPEX is an equivalent yearly representation."),
    ("NPV = annual saving", "NPV discounts a multi-year cash-flow stream; annual saving is a one-year comparison."),
    ("Payback = NPV", "Simple payback ignores time value of money; NPV explicitly discounts future cash flows."),
    ("Self-consumption = self-sufficiency", "Self-consumption follows PV energy; self-sufficiency follows site demand."),
    ("CO₂ target = renewable share", "The target constrains modeled grid-related emissions, not renewable share."),
    ("Optimal = universally best", "Optimal means best for the stated objective, inputs, constraints and model boundary."),
    ("Infeasible = solver error", "Infeasible means no solution satisfies all constraints; solver error is a separate status."),
    ("OMIE price = industrial bill", "OMIE is used as a wholesale energy-price proxy, not a complete industrial tariff."),
    ("Proxy = measured plant value", "A proxy is an approximation used because the exact facility-specific value is unavailable."),
    ("Model assumption = random guess", "A good assumption is explicit, traceable, changeable and stress-tested."),
)

QUESTIONS = (
    LearningQuestion("battery_duration", "A 2 MW / 4 MWh battery discharges at 2 MW. Ignoring efficiency and SOC limits, approximately how long can it run?", ("0.5 h", "1 h", "2 h", "4 h"), "2 h", "Energy / power = time: 4 MWh / 2 MW = 2 h."),
    LearningQuestion("self_consumption", "If PV self-consumption is 100%, must the plant be electrically self-sufficient?", ("Yes", "No"), "No", "100% self-consumption only means all PV generation stays onsite; PV may still cover a small share of total demand."),
    LearningQuestion("capacity_factor", "Does a PV capacity factor of 20% mean the panels convert 20% of sunlight into electricity?", ("Yes", "No"), "No", "Capacity factor compares actual energy with continuous operation at rated power; it is not conversion efficiency."),
    LearningQuestion("wacc", "Ceteris paribus, what does a higher WACC do to annualized CAPEX?", ("Increase", "Stay identical", "Decrease"), "Increase", "Higher WACC raises the capital recovery factor for a fixed lifetime." , "INTERMEDIATE"),
    LearningQuestion("baseline", "What is the baseline used for?", ("A comparison reference", "A forecast of the future", "A supplier quotation"), "A comparison reference", "Savings and CO₂ reduction need a consistent reference scenario."),
    LearningQuestion("binding", "If the economic optimum already reduces CO₂ by 30%, is a 20% minimum target usually binding?", ("Yes", "No"), "No", "The unconstrained optimum already exceeds the requirement, so that target does not restrict the solution." , "INTERMEDIATE"),
    LearningQuestion("infeasible", "What does an infeasible optimization mean?", ("The solver crashed", "No solution satisfies all current constraints", "The project has negative NPV"), "No solution satisfies all current constraints", "Infeasible is a mathematical status distinct from solver error." , "INTERMEDIATE"),
    LearningQuestion("proxy", "How should the OMIE series be interpreted in the Castellón case?", ("Complete industrial electricity bill", "Wholesale energy-price proxy", "Real plant contract"), "Wholesale energy-price proxy", "OptiDecarb does not model supplier margins, demand charges, taxes or a real facility contract."),
    LearningQuestion("derived", "A grid CO₂ factor calculated from published REE emissions and generation is what kind of value?", ("Real plant measurement", "Derived public value", "Random model assumption"), "Derived public value", "The ingredients are published; the final ratio is calculated by the model documentation."),
    LearningQuestion("optimum", "Does 'economic optimum' mean the system is best in every possible sense?", ("Yes", "No"), "No", "It is the minimum of the stated objective within the stated constraints and assumptions." , "INTERMEDIATE"),
    LearningQuestion("pre_feasibility", "What is the right decision question for OptiDecarb?", ("Should we build immediately?", "Does this justify more detailed engineering?"), "Does this justify more detailed engineering?", "OptiDecarb is a screening tool, not detailed design or investment approval."),
    LearningQuestion("unit_co2", "180 kgCO₂/MWh × 1,000 MWh equals?", ("180 kgCO₂", "180 tCO₂", "180,000 tCO₂"), "180 tCO₂", "180,000 kgCO₂ divided by 1,000 kg/t = 180 tCO₂."),
)

GUIDED_EXPERIMENTS = (
    GuidedExperiment("electricity_price_up", "Electricity price +20%", ("pv", "objective_function"), "What happens to cost-optimal PV when grid electricity becomes 20% more expensive?", "import_price_multiplier", 1.0, 1.2, ("Increase", "Stay similar", "Decrease"), "Higher avoided grid cost can increase the value of onsite PV under the tested assumptions."),
    GuidedExperiment("pv_capex_up", "PV CAPEX +20%", ("capex", "pv"), "Does more expensive PV change the cost-optimal PV capacity?", "pv_capex_eur_per_kw", None, 1.2, ("Increase", "Stay similar", "Decrease"), "Higher PV CAPEX generally makes marginal PV capacity less attractive, ceteris paribus."),
    GuidedExperiment("wacc_up", "WACC 5% → 6%", ("wacc", "crf", "annualized_capex"), "How does a higher financing rate affect capital-intensive sizing?", "wacc", 0.05, 0.06, ("More investment", "Similar", "Less investment"), "WACC changes CRF, which changes annualized CAPEX inside the objective."),
    GuidedExperiment("carbon_20_to_40", "Carbon target 20% → 40%", ("carbon_target", "binding"), "Which target starts to change the Castellón design?", "carbon_target", 0.20, 0.40, ("20%", "40%", "Neither"), "A target becomes binding only when it is stricter than what the economic optimum already achieves."),
    GuidedExperiment("battery_capex_down", "Battery CAPEX −20%", ("battery_energy", "capex"), "Does a 20% battery-cost reduction necessarily make storage optimal?", "battery_capex_multiplier", 1.0, 0.8, ("Yes", "Not necessarily"), "Cheaper storage can help, but it still needs enough operating value to exceed annualized cost and losses."),
    GuidedExperiment("pv_oversizing", "PV oversizing", ("self_consumption", "self_sufficiency", "pv"), "What happens when PV is deliberately increased above the economic optimum?", "fixed_pv_multiplier", 1.0, 1.5, ("Exports can rise", "Exports must fall"), "Additional PV can reduce imports but increasingly spill into exports, lowering marginal onsite value.", False),
)

CASTELLON_WALKTHROUGH = (
    ("1. Where does 15 GWh come from?", "It is a rounded representative scale chosen to be consistent with the order of magnitude implied by public ceramic-sector data. It is not a measured average factory."),
    ("2. How was the hourly load created?", "The annual scale is combined with a deterministic representative industrial shape. Annual scale and hourly shape are separate modelling choices."),
    ("3. Where does solar data come from?", "The profile is deterministic and calibrated to PVGIS solar-resource values for a representative Castelló location; it is not a raw hourly PVGIS download."),
    ("4. Why is OMIE a proxy?", "OMIE represents wholesale market energy. A real industrial bill can also include contract structure, supplier margin, taxes, network charges and demand terms."),
    ("5. What is baseline?", "Grid-only electricity supply for the same load and price series. It is the reference for savings and electrical CO₂ reductions."),
    ("6. Why roughly 3 MW PV?", "Under the current assumptions, the marginal avoided grid purchases justify PV up to the point where additional annualized PV cost and lower-valued exports reduce further economic benefit."),
    ("7. Why zero battery?", "Storage can shift PV surplus to later demand, but in the economic optimum its additional value is lower than its annualized cost plus losses under the tested assumptions."),
    ("8. Why does battery enter at 40% CO₂?", "The economic optimum already reduces electrical CO₂ by about 30%. A 40% minimum becomes binding, requiring deeper import reduction; more PV creates more surplus and storage becomes part of the least-cost feasible solution."),
    ("9. Why does 50% cost more?", "Deeper reductions shrink the feasible space and require more capital-intensive measures. The extra avoided CO₂ eventually has a positive marginal annualized cost."),
    ("10. What should we not conclude?", "OptiDecarb does not prove that a real ceramic plant should install these exact capacities. Thermal processes, real contracts, site geometry and detailed engineering remain outside this screening model."),
)

CONCEPT_DEPENDENCIES = (
    "POWER + ENERGY → LOAD / PV / BATTERY → HOURLY BALANCE → ECONOMICS → OPTIMIZATION → CARBON + SENSITIVITY",
    "WACC → CRF → ANNUALIZED CAPEX → OBJECTIVE FUNCTION → OPTIMAL SIZING",
)

TERM_DIFFICULTY = {
    **{k: "FOUNDATION" for k in (
        "power", "energy", "pv", "battery_energy", "battery_power", "baseline",
        "self_consumption", "self_sufficiency", "hours8760", "proxy", "public_data",
        "representative_model", "real_plant_data", "prefeasibility",
    )},
    **{k: "INTERMEDIATE" for k in (
        "capacity_factor", "soc", "cyclic_soc", "capex", "opex", "annualized_capex",
        "wacc", "crf", "npv", "payback", "decision_variable", "objective_function",
        "constraint", "binding", "infeasible", "grid_emission_factor", "carbon_target",
        "abatement_cost", "sensitivity", "break_even", "derived_value", "model_assumption",
    )},
    "lp": "ADVANCED",
}
