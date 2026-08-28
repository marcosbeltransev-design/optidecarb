from pathlib import Path

from industrial_energy_lab.explainability.glossary import GLOSSARY, get_term, validate_glossary
from industrial_energy_lab.learning import (
    CHECKLISTS,
    DECISION_STAGES,
    GOOD_JUNIOR_QUESTIONS,
    INDUSTRY_CASES,
    PROFESSIONAL_TERMS,
    ROLE_PERSPECTIVES,
    WORK_PHRASES,
    validate_industry_catalog,
)
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui.services import ROOT
from industrial_energy_lab.ui.v12_app import SECTIONS
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION


def test_v12_version_does_not_change_engine_version():
    assert APP_VERSION == "1.2.0"
    assert OPTIMIZATION_MODEL_VERSION == "0.3.0"


def test_industry_catalog_is_structurally_valid():
    validate_industry_catalog()
    assert len(INDUSTRY_CASES) == 8
    assert len(PROFESSIONAL_TERMS) >= 20
    assert len(ROLE_PERSPECTIVES) == 5
    assert len(DECISION_STAGES) >= 9
    assert len(GOOD_JUNIOR_QUESTIONS) >= 8
    assert len(WORK_PHRASES) >= 8


def test_industry_cases_explain_reasoning_and_next_step():
    ids = [case.case_id for case in INDUSTRY_CASES]
    assert len(ids) == len(set(ids))
    for case in INDUSTRY_CASES:
        assert case.correct_option in case.options
        assert case.why_correct
        assert case.why_incomplete
        assert case.better_answer
        assert case.main_lesson
        assert len(case.checks) >= 2
        assert len(case.data_to_request) >= 2
        assert len(case.other_options_feedback) == len(case.options) - 1


def test_professional_vocabulary_uses_easy_english_plus_context():
    ids = [term.term_id for term in PROFESSIONAL_TERMS]
    assert len(ids) == len(set(ids))
    for term in PROFESSIONAL_TERMS:
        assert term.full_name
        assert term.easy_explanation
        assert term.where_used
        assert term.example_sentence
        assert term.difficulty in {"FOUNDATION", "INTERMEDIATE", "ADVANCED"}
    required = {"epc", "feed", "due_diligence", "ppa", "curtailment", "commissioning", "om", "business_case"}
    assert required <= set(ids)


def test_core_glossary_and_professional_vocabulary_are_complementary():
    validate_glossary()
    for term_id in {"wacc", "npv", "binding", "soc"}:
        term = get_term(term_id)
        assert term.plain_language_definition
        assert term.technical_definition
        assert term.why_it_matters
    professional = {term.term_id: term for term in PROFESSIONAL_TERMS}
    for term_id in {"curtailment", "epc", "feed", "commissioning", "due_diligence", "ppa", "tariff"}:
        term = professional[term_id]
        assert term.easy_explanation
        assert term.where_used
        assert term.example_sentence
    assert professional["commissioning"].spanish_clarification


def test_junior_checklists_cover_required_workflow_moments():
    assert set(CHECKLISTS) == {
        "before_modelling", "before_trusting", "before_management", "before_suppliers", "before_co2_claim"
    }
    assert all(len(items) >= 4 for items in CHECKLISTS.values())


def test_navigation_contains_junior_lab_and_about_without_removing_engine_pages():
    assert "Junior Engineer Lab" in SECTIONS
    assert "About OptiDecarb" in SECTIONS
    for section in ("Inputs", "Baseline", "Optimized system", "Hourly results", "Economics", "Decarbonization", "Sensitivity", "Learning Lab", "Methodology"):
        assert section in SECTIONS


def test_visual_identity_assets_exist_and_are_not_empty():
    required = (
        "optidecarb-logo.svg",
        "optidecarb-icon.svg",
        "optidecarb-hero.svg",
    )
    for name in required:
        path = Path(ROOT) / "assets" / name
        assert path.exists(), name
        assert path.stat().st_size > 100, name


def test_new_learning_docs_exist():
    required = (
        "docs/JUNIOR_ENGINEER_GUIDE.md",
        "docs/INDUSTRY_CASES.md",
        "docs/CV_AND_INTERVIEW_POSITIONING.md",
        "docs/WINDOWS_APP_GUIDE.md",
    )
    for relative in required:
        text = (Path(ROOT) / relative).read_text(encoding="utf-8")
        assert len(text) > 500
