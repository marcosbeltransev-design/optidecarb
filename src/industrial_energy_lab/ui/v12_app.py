"""OptiDecarb v1.2 presentation layer built on the validated v1.1 UI."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from industrial_energy_lab.learning import CHECKLISTS, DECISION_STAGES, GOOD_JUNIOR_QUESTIONS, INDUSTRY_CASES, PROFESSIONAL_TERMS, ROLE_PERSPECTIVES, WORK_PHRASES
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui import streamlit_app as base
from industrial_energy_lab.ui.services import ROOT, default_parameters
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION

ASSETS = Path(ROOT) / "assets"
ICON_PATH = ASSETS / "optidecarb-icon.svg"
LOGO_PATH = ASSETS / "optidecarb-logo.svg"
HERO_PATH = ASSETS / "optidecarb-hero.svg"
SECTIONS = (
    "Overview", "Inputs", "Baseline", "Optimized system", "Hourly results", "Economics",
    "Decarbonization", "Sensitivity", "Learning Lab", "Junior Engineer Lab", "Methodology", "About OptiDecarb",
)

SECTION_GUIDANCE = {
    "Overview": ("Start with the decision", "Use the model to understand direction and order of magnitude. Do not treat a screening result as a construction design."),
    "Inputs": ("Good models start with good questions", "Check where each number comes from, its unit, period and whether it is measured, derived or assumed."),
    "Baseline": ("Know what you are comparing against", "Savings and CO₂ reductions only make sense if the baseline is clearly defined and internally consistent."),
    "Optimized system": ("Optimal does not mean build-ready", "The mathematical optimum answers the stated model. A company would still check space, grid limits, tariff and supplier quotations."),
    "Hourly results": ("Timing matters", "PV, load and battery behaviour depend on when energy is produced and consumed, not only on annual totals."),
    "Economics": ("A positive metric is not an approval", "NPV and payback are useful screening indicators, but finance will also challenge assumptions, risks and downside cases."),
    "Decarbonization": ("Targets can change the solution", "A target only affects the design when it becomes binding. Always explain the emissions baseline and factor used."),
    "Sensitivity": ("Challenge the answer", "Change one important assumption at a time and ask whether the recommendation still holds."),
    "Learning Lab": ("Predict before you run", "Try to explain the direction first. The goal is not to memorise the answer but to understand why it changes."),
    "Methodology": ("Know the model boundary", "Good engineering includes knowing what the model does not know and what must be validated later."),
}

def _inject_styles(st):
    st.markdown("""<style>
    .od-card{border:1px solid #d7e5f2;border-radius:14px;padding:1rem;background:#f8fbfe;margin:.4rem 0 1rem}
    .od-tip{border-left:5px solid #1f7ad1;padding:.7rem 1rem;background:#f3f8fd;border-radius:8px;margin:.5rem 0 1rem}
    .od-watch{border-left:5px solid #e5a100;padding:.7rem 1rem;background:#fffaf0;border-radius:8px;margin:.5rem 0 1rem}
    </style>""", unsafe_allow_html=True)

def _industry_on(st): return bool(st.session_state.get("industry_mode", True))

def _guidance(st, section):
    if not _industry_on(st) or section not in SECTION_GUIDANCE: return
    title, text = SECTION_GUIDANCE[section]
    st.markdown(f'<div class="od-tip"><b>🏭 In industry — {title}</b><br>{text}</div>', unsafe_allow_html=True)

def _friendly_error(st, result):
    status = getattr(result, "status", "solver_error")
    if status == "infeasible":
        title, what, why = "No feasible solution", "The current limits and constraints cannot all be satisfied together.", "This usually means the requested target is too strict for the allowed PV/battery bounds, not that the solver is broken."
    elif status == "unbounded":
        title, what, why = "The optimization has no finite economic limit", "The stated economics allow the objective to keep improving without a valid bound.", "Review prices, export assumptions and capacity limits."
    else:
        title, what, why = "The solver did not return a usable solution", "The optimization stopped without an interpretable optimum.", "Check inputs first; if they look valid, inspect the technical solver message."
    st.error(f"**{title}.** {what}")
    st.info(f"**Why it matters:** {why}\n\n**What to check next:** inputs, units, model bounds and active constraints.")
    with st.expander("Technical detail"):
        st.code(getattr(result, "solver_message", "No solver message available."))

def _result_context(st, result):
    if not _industry_on(st) or getattr(result, "status", None) != "optimal": return
    pv = (result.pv_capacity_kw or 0)/1000
    batt = (result.battery_energy_capacity_kwh or 0)/1000
    st.subheader("From model result to professional judgement")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("**Can I use this? — YES, for screening.**\n\nIt shows direction, scale and the assumptions that drive the result.")
    with c2:
        st.warning("**Ready for investment approval? — NO.**\n\nStill validate the real tariff, site layout, export/grid limits, quotations and detailed engineering.")
    with c3:
        st.info(f"**Avoid false precision.**\n\nModel output: **{pv:.3f} MWp**. In a meeting, say **around {pv:.1f} MWp under the current assumptions**.")
    if batt < 1e-6:
        st.markdown('<div class="od-watch"><b>⚠ Junior wording</b><br>Do not say “batteries are not economical”. Say: <b>“Under the current assumptions, battery storage is not selected in the economic optimum.”</b></div>', unsafe_allow_html=True)
    with st.expander("📋 What would a company do next?"):
        st.markdown("1. Confirm roof / land availability.\n2. Check grid connection and export limits.\n3. Validate the electricity contract / tariff.\n4. Request comparable EPC quotations.\n5. Review operational and maintenance constraints.\n6. Move to a more detailed feasibility study if the screening remains attractive.")

def _render_case(st, case, idx):
    with st.expander(f"Case {idx}: {case.title}"):
        st.write(case.situation)
        for x in case.available_information: st.write(f"- {x}")
        answer = st.radio(case.question, case.options, key=f"case_{case.case_id}")
        if st.button("Show reasoning", key=f"show_{case.case_id}"):
            if answer == case.correct_option: st.success(f"**Correct:** {case.correct_option}")
            else: st.warning(f"**Better answer:** {case.correct_option}")
            st.write(f"**Why:** {case.why_correct}")
            st.write(f"**Why a quick junior answer may be incomplete:** {case.why_incomplete}")
            st.info(f"**Better professional answer:** {case.better_answer}")
            st.write("**What to check:** " + "; ".join(case.checks))
            st.write("**What data to ask for:** " + "; ".join(case.data_to_request))
            st.success(f"**Main lesson:** {case.main_lesson}")

def _junior_lab(st):
    st.header("Junior Engineer Lab")
    st.caption("Real-world practice for early-career engineers — clear English, professional vocabulary and explicit reasoning.")
    st.image(str(HERO_PATH), use_container_width=True)
    tabs = st.tabs(["Imperfect data", "Client & supplier", "Departments", "Vocabulary", "Communication", "Project maturity"])
    with tabs[0]:
        st.subheader("Quick sanity checks before modelling")
        st.markdown("**Example:** 15,000 MWh/year ÷ 8,760 h = **1.71 MW average load**. If someone reports a **0.9 MW peak**, the data are inconsistent because average load cannot be higher than peak load.")
        st.markdown("Check: MW vs MWh · average vs peak · 8,760 timestamps · missing/duplicate hours · negative load · PV at night · SOC above capacity · self-consumption above 100% · CO₂ units.")
        for i, case in enumerate(INDUSTRY_CASES[:2], 1): _render_case(st, case, i)
        with st.expander("Before modelling checklist"):
            for x in CHECKLISTS["before_modelling"]: st.checkbox(x, key=f"bm_{x}")
    with tabs[1]:
        st.subheader("Understand the request before accepting the solution")
        st.info('Client: “We want 5 MW of solar.” A useful junior asks: **Why 5 MW? What is the load? Is there space? Can we export? What is the business objective?**')
        st.warning('Supplier: “Our battery saves 40%.” Ask: **40% of which cost, against what baseline, under which tariff, with what MW/MWh, efficiency, degradation, dispatch, warranty and CAPEX?**')
        for i, case in enumerate(INDUSTRY_CASES[2:5], 3): _render_case(st, case, i)
    with tabs[2]:
        for role in ROLE_PERSPECTIVES:
            with st.expander(role.label):
                for q in role.questions: st.write(f"- {q}")
                st.caption(role.junior_lesson)
    with tabs[3]:
        st.caption("Learn the professional word, but understand the simple idea first.")
        for term in PROFESSIONAL_TERMS:
            with st.expander(f"{term.term} — {term.full_name}"):
                st.write(f"**In simple terms:** {term.easy_explanation}")
                st.write(f"**Where you may see it:** {term.where_used}")
                st.write(f"**Example:** {term.example_sentence}")
                if term.spanish_clarification: st.caption(f"ES: {term.spanish_clarification}")
    with tabs[4]:
        st.subheader("Technical output → useful message")
        st.error('Too technical: “The LP identifies a 2.972 MW optimum through marginal cost minimization.”')
        st.success('Better: “Under the current assumptions, around 3 MWp of PV appears economically attractive. Before an investment decision, we should validate site constraints, tariff conditions and supplier quotations.”')
        st.subheader("Useful phrases at work")
        for phrase in WORK_PHRASES: st.write(f"- {phrase}")
        st.caption("Good engineering is also knowing when to say: we do not yet have enough information to conclude that.")
        for i, case in enumerate(INDUSTRY_CASES[5:], 6): _render_case(st, case, i)
    with tabs[5]:
        st.subheader("From curiosity to operation")
        st.dataframe(pd.DataFrame([{"stage": x.stage, "in simple terms": x.easy_explanation, "reasonable output": x.reasonable_output} for x in DECISION_STAGES]), use_container_width=True, hide_index=True)
        st.info("OptiDecarb is a **screening / pre-feasibility learning tool**. It is not detailed engineering or investment approval.")

def _about(st):
    st.header("About OptiDecarb")
    st.image(str(LOGO_PATH), width=520)
    st.markdown("**OptiDecarb combines an 8,760-hour engineering model with a learning environment for industrial energy decisions.**")
    st.markdown("It models the electrical subsystem: load, PV, battery, grid exchange, economics and explicit CO₂ constraints. It does **not** model kiln/dryer heat, natural gas, detailed tariffs, site layout, permitting or construction design.")
    st.subheader("Why it exists")
    st.write("The goal is not to make a student sound experienced. It is to help a student ask better questions, check data, challenge assumptions, understand uncertainty and communicate a defensible next step.")
    st.subheader("AI-assisted development")
    st.info("OptiDecarb was developed using AI-assisted software development. The project focuses on defining the engineering problem, challenging assumptions, validating model behaviour, tracing public data, interpreting results and using the development process itself as a learning tool. It is not presented as manually coding every line without assistance.")
    st.caption(f"App v{APP_VERSION} · Model v{OPTIMIZATION_MODEL_VERSION} · public-data representative case, not a real factory")

def _overview_wrapper(st):
    base._overview(st)
    result = st.session_state.get("economic_result") or st.session_state.get("last_result")
    if result is not None: _result_context(st, result)

def _page(st, section):
    if section == "Junior Engineer Lab": return _junior_lab(st)
    if section == "About OptiDecarb": return _about(st)
    _guidance(st, section)
    pages = {"Overview": _overview_wrapper, "Inputs": base._inputs, "Baseline": base._baseline, "Optimized system": base._optimized, "Hourly results": base._hourly, "Economics": base._economics, "Decarbonization": base._decarbonization, "Sensitivity": base._sensitivity, "Learning Lab": base._learning_lab, "Methodology": base._methodology}
    pages[section](st)
    if section in {"Optimized system", "Economics", "Decarbonization"}:
        result = st.session_state.get("last_result") or st.session_state.get("economic_result")
        if result is not None: _result_context(st, result)

def main():
    import streamlit as st
    st.set_page_config(page_title="OptiDecarb", page_icon=str(ICON_PATH), layout="wide")
    _inject_styles(st)
    base._result_error = _friendly_error
    base._state_defaults(st)
    if "industry_mode" not in st.session_state: st.session_state.industry_mode = True
    try: st.logo(str(LOGO_PATH), icon_image=str(ICON_PATH), size="large")
    except Exception: pass
    with st.sidebar:
        st.header("OptiDecarb")
        st.session_state.learning_mode = st.toggle("Learning mode", value=bool(st.session_state.get("learning_mode", True)), help="Show extra explanations and worked examples. Engineering calculations are unchanged.")
        st.session_state.industry_mode = st.toggle("Industry mode", value=bool(st.session_state.get("industry_mode", True)), help="Show real-work context, junior checks and next-step guidance.")
        options = list(base.CASE_LABELS)
        selected = st.selectbox("Case", options, index=options.index(st.session_state.case_id), format_func=lambda value: base.CASE_LABELS[value])
        if selected != st.session_state.case_id:
            st.session_state.case_id = selected; st.session_state.params = default_parameters(selected); st.session_state.custom_load = None; base._invalidate_results(st); st.rerun()
        section = st.radio("Navigate", SECTIONS, index=0)
        st.divider(); active = base._bundle(st)
        st.caption(f"App v{APP_VERSION}"); st.caption(f"Model v{OPTIMIZATION_MODEL_VERSION}"); st.caption(f"Dataset {active.dataset_version}"); st.caption(f"Case {active.case_version}")
    base._render_header(st, section)
    if section == "Overview": st.image(str(HERO_PATH), use_container_width=True)
    _page(st, section)

if __name__ == "__main__": main()
