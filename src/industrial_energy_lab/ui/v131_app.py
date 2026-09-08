"""OptiDecarb v1.3.1 active-learning layer.

This patch release enriches the v1.3 industrial-energy curriculum with visual,
predict-before-reveal learning. It does not alter engineering equations.
"""
from __future__ import annotations

from industrial_energy_lab.ui import advanced_learning as adv
from industrial_energy_lab.ui import v13_app as base

_BASE_DATA = base._energy_data_lab
_BASE_ECONOMICS = base._energy_economics_lab
_BASE_PROJECT = base._energy_project_lab
_BASE_CAPSTONE = base._capstone
_BASE_SKILL_MAP = base._skill_map
_BASE_ABOUT = base._about_v13


def _energy_data_lab(st) -> None:
    st.subheader("Industrial Energy Data — visual practice")
    st.caption("Read the profile, check units, then investigate data quality. The sequence is intentional.")
    tabs = st.tabs(["Profile reading", "Formula & units", "Data forensics"])
    with tabs[0]:
        adv.render_case_data_visuals(st)
    with tabs[1]:
        adv.render_formula_lab(st)
    with tabs[2]:
        _BASE_DATA(st)


def _model_intuition_lab(st) -> None:
    st.subheader("Model Intuition — predict before the solver tells you")
    st.caption("Use engineering direction and rough calculations first; use the optimizer to test that reasoning second.")
    adv.learning_loop(st)
    sections = st.tabs(["Sensitivity predictions", "One-day balance", "CO₂ constraint", "Model boundaries"])
    with sections[0]:
        adv.render_prediction_lab(st)
    with sections[1]:
        adv.render_one_day_energy_story(st)
    with sections[2]:
        adv.render_carbon_frontier(st)
    with sections[3]:
        adv.render_traceability(st)


def _energy_project_lab(st) -> None:
    _BASE_PROJECT(st)
    st.divider()
    adv.render_screening_vs_feasibility(st)


def _capstone(st) -> None:
    _BASE_CAPSTONE(st)
    st.divider()
    adv.render_transfer_case(st)


def _skill_map(st) -> None:
    _BASE_SKILL_MAP(st)
    st.divider()
    adv.render_interview_defence(st)


def _junior_lab_v131(st) -> None:
    st.header("Industrial Energy Junior Lab")
    st.caption("Learn by estimating, predicting, calculating, checking and explaining industrial-energy decisions.")
    adv.inject_learning_theme(st)
    adv.learning_loop(st)
    st.image(str(base.base.HERO_PATH), use_container_width=True)
    tabs = st.tabs([
        "Start / Diagnostic",
        "Energy data",
        "Model intuition",
        "Economics & tariffs",
        "Project & site",
        "PV/BESS suppliers",
        "Communication",
        "AI & validation",
        "Energy Capstone",
        "Skill map",
    ])
    with tabs[0]:
        base._diagnostic(st)
    with tabs[1]:
        _energy_data_lab(st)
    with tabs[2]:
        _model_intuition_lab(st)
    with tabs[3]:
        _BASE_ECONOMICS(st)
    with tabs[4]:
        _energy_project_lab(st)
    with tabs[5]:
        base._supplier_lab(st)
    with tabs[6]:
        base._communication_lab(st)
    with tabs[7]:
        base._ai_validation_lab(st)
    with tabs[8]:
        _capstone(st)
    with tabs[9]:
        _skill_map(st)
    st.divider()
    adv.render_session_review(st)


def _about_v131(st) -> None:
    _BASE_ABOUT(st)
    st.subheader("v1.3.1 — Active Industrial Energy Learning")
    st.write(
        "This patch strengthens how OptiDecarb teaches the existing energy model: real Castellón load-profile reading, formula/unit intuition, predict-before-reveal sensitivity, hourly balance reconstruction, visual binding-constraint reasoning, model-boundary traceability and one unseen transfer case. Optimization Model v0.3.0 is unchanged."
    )


def main() -> None:
    """Run the validated v1.3 shell with the v1.3.1 active-learning layer."""
    base._junior_lab_v13 = _junior_lab_v131
    base._about_v13 = _about_v131
    base.main()


if __name__ == "__main__":
    main()
