"""OptiDecarb v1.3 industrial-energy learning layer over the validated v1.2 UI."""
from __future__ import annotations

import pandas as pd

from industrial_energy_lab.learning import INDUSTRY_CASES
from industrial_energy_lab.learning.readiness import (
    AI_ENGINEERING_RULES,
    ASSUMPTIONS_LOG_EXAMPLE,
    CAPSTONE,
    CASTELLON_COMMITTEE,
    DATA_QUALITY_CASES,
    DIAGNOSTIC_QUESTIONS,
    FIRST_DATA_REQUEST,
    JOB_READINESS_MATRIX,
    JUNIOR_DELIVERABLES,
    MENTAL_MODELS,
    PRACTICAL_TASKS,
    SITE_VISIT_BASICS,
    SKILLS,
    VALIDATION_TYPES,
    diagnostic_summary,
)
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui import v12_app as base
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION

_BASE_PAGE = base._page
_BASE_ABOUT = base._about
V13_SECTIONS = tuple("Industrial Energy Junior Lab" if section == "Junior Engineer Lab" else section for section in base.SECTIONS)


def _diagnostic(st) -> None:
    st.subheader("Industrial Energy Diagnostic — 10–15 minutes")
    st.caption("No points or badges. The goal is to find which energy skills you should practise first.")
    with st.form("energy_readiness_diagnostic"):
        answers: dict[str, str] = {}
        for q in DIAGNOSTIC_QUESTIONS:
            answers[q.question_id] = st.radio(q.prompt, q.options, index=None, key=f"diag_{q.question_id}")
        submitted = st.form_submit_button("Build my energy learning path")
    if submitted:
        missing = [q.question_id for q in DIAGNOSTIC_QUESTIONS if answers.get(q.question_id) is None]
        if missing:
            st.warning("Answer every question so the recommendation covers the full energy workflow.")
            return
        result = diagnostic_summary(answers)
        st.session_state["energy_readiness_diagnostic"] = result
        c1, c2 = st.columns(2)
        with c1:
            st.success("**Current strengths**\n\n" + (" · ".join(result["strengths"]) or "Start with the energy foundations — that is what this lab is for."))
        with c2:
            st.info("**Practise first**\n\n" + (" → ".join(result["recommended_paths"]) or "Use the Energy Capstone to challenge the full workflow."))
        with st.expander("Why these questions matter"):
            for q in DIAGNOSTIC_QUESTIONS:
                mark = "✓" if answers[q.question_id] == q.correct_option else "→"
                st.markdown(f"**{mark} {q.area}:** {q.why}")
    elif st.session_state.get("energy_readiness_diagnostic"):
        result = st.session_state["energy_readiness_diagnostic"]
        st.info("**Recommended energy path:** " + (" → ".join(result["recommended_paths"]) or "Energy Capstone"))


def _energy_data_lab(st) -> None:
    st.subheader("Industrial Energy Data & Sanity Checks")
    st.caption("Estimate first, understand the meter boundary, then model. A detailed optimizer cannot rescue bad energy data.")

    st.markdown("### Mental models to reuse everywhere")
    cols = st.columns(3)
    for i, (name, explanation) in enumerate(MENTAL_MODELS):
        with cols[i % 3]:
            st.info(f"**{name}**\n\n{explanation}")

    st.markdown("### Back-of-the-envelope energy checks")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("15 GWh/y → average", "≈ 1.71 MW", help="15,000 MWh / 8,760 h")
    c2.metric("100 kWh in 15 min", "≈ 400 kW", help="100 kWh / 0.25 h")
    c3.metric("3 MWp × 1,500 yield", "≈ 4.5 GWh/y", help="3,000 kWp × 1,500 kWh/kWp")
    c4.metric("4 MWh / 2 MW BESS", "≈ 2 h", help="Nominal duration before usable-SOC and losses")

    st.markdown("### Data Quality Lab — answer before revealing")
    for idx, case in enumerate(DATA_QUALITY_CASES, 1):
        with st.expander(f"{idx}. {case.title}"):
            st.write(case.situation)
            answer = st.radio(case.question, case.options, index=None, key=f"dq_{case.case_id}")
            if st.button("Show energy reasoning", key=f"dq_show_{case.case_id}"):
                if answer is None:
                    st.info("Choose an answer first.")
                else:
                    if answer == case.correct_option:
                        st.success(f"Correct: **{case.correct_option}**")
                    else:
                        st.warning(f"Better answer: **{case.correct_option}**")
                    st.write(f"**Why:** {case.why}")
                    st.write(f"**First action:** {case.first_action}")
                    st.write(f"**What would I check in Excel?** {case.excel_check}")
                    st.info(f"**Energy-engineering lesson:** {case.professional_lesson}")

    st.markdown("### First energy-data request — and why")
    st.dataframe(pd.DataFrame([{"Ask for": x.item, "Why it matters to the energy study": x.why_needed} for x in FIRST_DATA_REQUEST]), hide_index=True, use_container_width=True)

    st.markdown("### Example energy assumptions log")
    st.dataframe(pd.DataFrame(ASSUMPTIONS_LOG_EXAMPLE), hide_index=True, use_container_width=True)


def _energy_economics_lab(st) -> None:
    st.subheader("Electricity Bill & Energy Economics")
    st.caption("Learn what the modelled €/MWh means — and what a real industrial bill may contain beyond it.")

    st.warning("**OMIE is a wholesale energy-price proxy, not the complete industrial electricity bill.**")
    st.markdown(
        "A real site may also have supplier margins/terms, network charges, contracted-power or maximum-demand components, taxes and fixed/indexed/hedged arrangements. "
        "OptiDecarb v0.3.0 intentionally does not model a full tariff."
    )

    st.markdown("### Quick reconciliation exercise")
    st.write("A plant consumes **8,760 MWh/year** and the screening uses **90 €/MWh** for the energy component.")
    answer = st.radio("Rough modelled energy component?", ("€78,840/y", "€788,400/y", "€7.88m/y"), index=None, key="bill_reconcile")
    if st.button("Show bill reasoning"):
        if answer == "€788,400/y":
            st.success("Correct: about **€788k/year** for that energy component.")
        else:
            st.warning("Use MWh × €/MWh: 8,760 × 90 ≈ €788,400/year.")
        st.info("**Junior lesson:** this is not automatically the invoiced annual cost. Reconcile the model boundary with invoices and the contract before presenting savings.")

    st.markdown("### Economic questions an energy engineer should ask")
    for q in (
        "Is the electricity price fixed, indexed, hedged or a simplified proxy?",
        "Which bill components can PV or BESS actually reduce in this study?",
        "Is export permitted and how is exported energy valued?",
        "Which WACC / hurdle rate / project horizon should be used?",
        "Does the recommendation survive plausible changes in electricity price, CAPEX and WACC?",
        "Are CAPEX figures benchmarks or comparable EPC quotations?",
    ):
        st.write(f"- {q}")

    st.markdown("### Sensitivity = decision robustness")
    st.success("Do not ask only: **How much did NPV change?** Ask: **Would I still recommend further study if this assumption were worse?**")


def _energy_project_lab(st) -> None:
    st.subheader("Energy Project & Site Work")
    st.caption("This is the bridge from desktop screening to a real industrial PV/BESS project.")

    st.markdown("### What might I actually do as a junior energy engineer?")
    for task in PRACTICAL_TASKS:
        with st.expander(task.title):
            st.write(task.brief)
            st.write(f"**Expected output:** {task.expected_output}")
            st.write("**Good process:** " + " → ".join(task.good_process))
            st.info(task.main_lesson)

    st.markdown("### Energy deliverables")
    for name, purpose in JUNIOR_DELIVERABLES:
        st.markdown(f"- **{name}:** {purpose}")

    st.markdown("### Energy-project risk register")
    risk_rows = [
        {"Energy/project risk": "Real tariff differs from price proxy", "Why it matters": "PV/BESS savings may change", "Mitigation": "Validate invoices/contract", "Typical owner": "Energy + Finance"},
        {"Energy/project risk": "Roof/land cannot host modelled PV", "Why it matters": "MWp optimum may be physically impossible", "Mitigation": "Site survey / layout / structural check", "Typical owner": "Engineering"},
        {"Energy/project risk": "Export is restricted", "Why it matters": "Large PV surplus may have lower or zero value", "Mitigation": "Confirm grid/contract conditions", "Typical owner": "Energy / Grid"},
        {"Energy/project risk": "EPC CAPEX exceeds benchmark", "Why it matters": "NPV/payback deteriorate", "Mitigation": "Request comparable budget quotations", "Typical owner": "Procurement + Engineering"},
        {"Energy/project risk": "Production cannot accept installation outage", "Why it matters": "Connection/commissioning plan may change", "Mitigation": "Agree shutdown windows with operations", "Typical owner": "Operations + Project"},
    ]
    st.dataframe(pd.DataFrame(risk_rows), hide_index=True, use_container_width=True)

    st.markdown("### Industrial energy site visit — what to look for")
    st.warning("Awareness only: follow site safety rules and do not inspect live electrical equipment beyond your authorization and competence.")
    for item in SITE_VISIT_BASICS:
        st.write(f"- {item}")

    st.markdown("### What does 'validated' mean in an energy project?")
    for name, meaning in VALIDATION_TYPES:
        st.markdown(f"- **{name}:** {meaning}")

    st.markdown("### After commissioning: did the energy project actually perform?")
    st.info("Real teams compare measured generation/consumption with expectations and investigate deviations. Measurement & Verification (M&V) is the professional idea behind proving savings against a credible baseline. OptiDecarb introduces the concept but does not implement a full M&V engine.")


def _supplier_lab(st) -> None:
    st.subheader("PV & BESS Suppliers, Quotations & Datasheets")
    st.caption("Headline €/kWp or €/kWh is not comparable until technical scope, connection and guarantees are aligned.")

    quote = pd.DataFrame([
        {"": "PV Supplier A", "PV price": "610 €/kWp", "Grid connection": "Excluded", "O&M": "1 year", "Performance guarantee": "Not stated", "Commissioning": "Included"},
        {"": "PV Supplier B", "PV price": "665 €/kWp", "Grid connection": "Included to LV board", "O&M": "3 years", "Performance guarantee": "Stated", "Commissioning": "Included"},
    ])
    st.dataframe(quote, hide_index=True, use_container_width=True)
    choice = st.radio("Which PV supplier is better from this table alone?", ("Supplier A", "Supplier B", "Not enough information yet"), index=None, key="quote_choice")
    if st.button("review PV quotation reasoning".title()):
        if choice == "Not enough information yet":
            st.success("Good: **not enough information yet.**")
        else:
            st.warning("The current technical/commercial scope is not sufficient to choose responsibly.")
        st.write("Put both offers on the same design basis: DC/AC sizing, modules/inverters, structure, electrical works, grid connection, engineering, commissioning, yield assumptions, warranties, O&M, exclusions and payment terms.")

    st.markdown("### Battery datasheet — questions that matter")
    st.markdown("**2 MW / 4 MWh** ≈ two-hour nominal duration. Also ask for usable vs nominal MWh, charge/discharge efficiency, round-trip efficiency, SOC window, cycle/calendar warranty, degradation/augmentation, PCS/EMS scope, fire protection, grid connection and availability guarantee.")

    st.markdown("### Supplier claim challenge")
    st.error('Supplier: **“Our BESS reduces the electricity bill by 40%.”**')
    with st.expander("Questions before believing the claim"):
        for q in (
            "40% of which bill components?",
            "Compared with which baseline year and tariff?",
            "What MW and MWh rating, usable capacity and efficiency were assumed?",
            "Can the battery charge from grid, PV, or both?",
            "What price profile and dispatch strategy were used?",
            "What degradation, warranty, availability and replacement assumptions were used?",
            "Does the result include CAPEX, O&M and connection costs?",
        ):
            st.write(f"- {q}")

    st.markdown("### Existing PV/BESS mini-cases")
    for i, case in enumerate(INDUSTRY_CASES[2:5], 1):
        base._render_case(st, case, i)


def _communication_lab(st) -> None:
    st.subheader("Communicating an Energy Recommendation")
    st.caption("Communication stays inside the engineering problem: load, PV/BESS, economics, CO₂, uncertainty and next technical step.")

    st.markdown("### Five-line energy note")
    st.code("""Context: We completed an initial PV screening for the industrial site.\nFinding: Around 3 MWp appears economically attractive under current assumptions.\nAssumption: Electricity price is still a wholesale energy-price proxy.\nEnergy/project risk: Real tariff, export limits and available site area may change the business case.\nNext step: Validate interval data, tariff/site constraints and comparable EPC quotations.""")

    st.markdown("### Email requesting missing energy data")
    st.code("""Subject: Electricity data needed for the PV screening\n\nHi [Name],\n\nThanks for the information shared so far. Could you please send the interval electricity file, latest invoices/contract and any available information on the main meter, transformer and export conditions? These items are needed to validate the load profile and can materially change PV sizing and savings.\n\nBest regards,""")

    st.markdown("### Manager challenge")
    st.text_area("Your manager asks: “Why should I trust your ~3 MWp recommendation?” Write 2–4 sentences before opening the example.", key="manager_challenge")
    with st.expander("Example energy-engineering answer"):
        st.write("It is a reproducible 8,760-hour screening result with an explicit load/PV profile and documented economic assumptions. I trust it as an order-of-magnitude and direction for further study, not as a final design. Before a stronger recommendation I would validate the real tariff, site area, grid/export limits and EPC pricing.")

    st.markdown("### A useful 'I need to check that' answer")
    st.info("“I have not confirmed the export conditions yet. That matters because surplus PV value can change the optimal size and savings. I would validate the grid/contract position before presenting the economics as site-specific.”")

    st.markdown("### Say it out loud")
    st.write("Try a **30-second explanation** of load factor, WACC, battery = 0, the 40% binding CO₂ target, or the Castellón recommendation. Then give a **2-minute version** with one calculation, one assumption and one limitation.")


def _ai_validation_lab(st) -> None:
    st.subheader("AI & Validation for Energy Analysis")
    st.caption("AI can accelerate energy analysis, but units, sources, balances and site facts still need engineering verification.")
    c1, c2 = st.columns(2)
    with c1:
        st.success("**Useful AI habits in energy work**")
        for x in AI_ENGINEERING_RULES["use_well"]:
            st.write(f"- {x}")
    with c2:
        st.warning("**Do not outsource energy judgement**")
        for x in AI_ENGINEERING_RULES["avoid"]:
            st.write(f"- {x}")

    st.markdown("### Verification exercise")
    st.error("**Plausible but wrong:** “A 2 MW / 4 MWh BESS can supply 2 MW for four hours because it stores 4 MWh.”")
    with st.expander("Check it before trusting it"):
        st.write("Duration = energy / power = 4 MWh / 2 MW = **2 hours**, before efficiency and usable-SOC limits. A confident AI answer is not a substitute for dimensional analysis.")

    st.markdown("### Four validation questions for any AI-generated energy answer")
    for q in (
        "Do the units close?",
        "Is the order of magnitude plausible for this industrial site?",
        "Can I trace the price / emission factor / technical assumption to a credible source?",
        "Does the statement respect the model boundary and known site constraints?",
    ):
        st.write(f"- {q}")


def _capstone(st) -> None:
    st.subheader("Energy Capstone — Industrial PV + BESS Screening")
    st.write(CAPSTONE["context"])
    for fact in CAPSTONE["facts"]:
        st.write(f"- {fact}")
    st.markdown("### Your task")
    for i, question in enumerate(CAPSTONE["questions"], 1):
        st.write(f"**{i}. {question}**")
    st.text_area("Write your energy recommendation before opening the worked solution", key="capstone_answer", height=160)
    with st.expander("Worked solution — open only after trying"):
        for i, answer in enumerate(CAPSTONE["worked_solution"], 1):
            st.markdown(f"** {i}.** {answer}")

    st.markdown("### Castellón energy investment committee")
    st.caption("Answer each question aloud before opening the suggested response.")
    for role, question, answer in CASTELLON_COMMITTEE:
        with st.expander(f"{role}: {question}"):
            st.write(answer)


def _skill_map(st) -> None:
    st.subheader("Industrial Energy Skill Map")
    st.caption("OptiDecarb is deliberately not a generic career course. Every skill below connects to industrial electricity, PV/BESS, economics, carbon or energy-project decisions.")
    df = pd.DataFrame([{"Energy area": s.group, "Skill": s.name, "I should be able to do": s.do, "Practice": s.practice} for s in SKILLS])
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.markdown("### Typical junior energy task → where to practise")
    st.dataframe(pd.DataFrame(JOB_READINESS_MATRIX, columns=["Junior energy task", "OptiDecarb practice"]), hide_index=True, use_container_width=True)

    st.info("OptiDecarb can teach energy-data reasoning, modelling, PV/BESS economics, supplier questions and energy-project judgement. It cannot replace real site experience, industrial safety, detailed electrical design, real procurement negotiations or commissioning responsibility.")


def _junior_lab_v13(st) -> None:
    st.header("Industrial Energy Junior Lab")
    st.caption("Practise the energy work you could face as an intern or junior engineer: data → baseline → PV/BESS → economics → site → supplier → recommendation.")
    st.image(str(base.HERO_PATH), use_container_width=True)
    tabs = st.tabs([
        "Start / Diagnostic",
        "Energy data",
        "Economics & tariffs",
        "Project & site",
        "PV/BESS suppliers",
        "Communication",
        "AI & validation",
        "Energy Capstone",
        "Skill map",
    ])
    with tabs[0]: _diagnostic(st)
    with tabs[1]: _energy_data_lab(st)
    with tabs[2]: _energy_economics_lab(st)
    with tabs[3]: _energy_project_lab(st)
    with tabs[4]: _supplier_lab(st)
    with tabs[5]: _communication_lab(st)
    with tabs[6]: _ai_validation_lab(st)
    with tabs[7]: _capstone(st)
    with tabs[8]: _skill_map(st)


def _about_v13(st) -> None:
    _BASE_ABOUT(st)
    st.subheader("v1.3 — Industrial Energy Learning Architecture")
    st.write("The learning layer is intentionally focused on industrial electricity: load and metering, data quality, PV/BESS, electricity economics, optimization, carbon, site/project constraints, supplier review and energy recommendations. General career content is kept only when it directly supports an energy-engineering task. The mathematical model remains v0.3.0.")


def _v13_page_router(st, section: str) -> None:
    if section == "Industrial Energy Junior Lab":
        return _junior_lab_v13(st)
    if section == "About OptiDecarb":
        return _about_v13(st)
    return _BASE_PAGE(st, section)


def main() -> None:
    """Run the validated v1.2 UI shell with the energy-focused v1.3 learning layer."""
    base.SECTIONS = V13_SECTIONS
    base._page = _v13_page_router
    base.main()


if __name__ == "__main__":
    main()
