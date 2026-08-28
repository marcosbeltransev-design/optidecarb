from industrial_energy_lab.learning.readiness import (
    CAPSTONE,
    DATA_QUALITY_CASES,
    DIAGNOSTIC_QUESTIONS,
    FIRST_DATA_REQUEST,
    JOB_READINESS_MATRIX,
    MENTAL_MODELS,
    SKILL_GROUPS,
    SKILLS,
    diagnostic_summary,
    validate_readiness_catalog,
)
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION


def test_v13_keeps_validated_engine_version():
    assert APP_VERSION == "1.3.0"
    assert OPTIMIZATION_MODEL_VERSION == "0.3.0"


def test_skill_map_is_industrial_energy_focused():
    validate_readiness_catalog()
    assert 9 <= len(SKILL_GROUPS) <= 12
    assert set(SKILL_GROUPS) <= {s.group for s in SKILLS}
    assert len(SKILLS) >= 18
    joined = " ".join(SKILL_GROUPS).lower()
    for required in ("energy", "load", "pv", "battery", "economics", "decarbonization", "site"):
        assert required in joined
    assert "generic career" not in joined


def test_diagnostic_is_energy_reasoning_based_and_complete():
    assert 10 <= len(DIAGNOSTIC_QUESTIONS) <= 15
    ids = [q.question_id for q in DIAGNOSTIC_QUESTIONS]
    assert len(ids) == len(set(ids))
    joined = " ".join(q.prompt for q in DIAGNOSTIC_QUESTIONS).lower()
    for concept in ("mw", "meter", "pv", "battery", "omie", "co₂"):
        assert concept in joined
    for q in DIAGNOSTIC_QUESTIONS:
        assert q.correct_option in q.options
        assert q.why
        assert q.recommended_path


def test_diagnostic_summary_recommends_energy_practice_without_points():
    answers = {q.question_id: q.correct_option for q in DIAGNOSTIC_QUESTIONS}
    first = DIAGNOSTIC_QUESTIONS[0]
    answers[first.question_id] = next(x for x in first.options if x != first.correct_option)
    result = diagnostic_summary(answers)
    assert first.area in result["practise"]
    assert result["recommended_paths"]


def test_data_quality_lab_has_energy_reasoning_excel_transfer_and_action():
    assert len(DATA_QUALITY_CASES) >= 9
    joined = " ".join(case.situation for case in DATA_QUALITY_CASES).lower()
    for concept in ("load", "meter", "kwh", "mw"):
        assert concept in joined
    for case in DATA_QUALITY_CASES:
        assert case.correct_option in case.options
        assert case.why
        assert case.first_action
        assert case.excel_check
        assert case.professional_lesson


def test_first_data_request_is_site_energy_specific():
    assert len(FIRST_DATA_REQUEST) >= 12
    text = " ".join(item.item + " " + item.why_needed for item in FIRST_DATA_REQUEST).lower()
    for concept in ("electricity", "meter", "tariff", "transformer", "export", "wacc"):
        assert concept in text


def test_capstone_covers_full_energy_screening_workflow():
    assert len(CAPSTONE["questions"]) == len(CAPSTONE["worked_solution"])
    joined = " ".join(CAPSTONE["questions"]).lower()
    for concept in ("energy-data", "average demand", "grid emissions", "pv", "battery", "bill savings", "sensitivity", "recommendation"):
        assert concept in joined


def test_mental_models_and_energy_job_mapping_exist():
    assert len(MENTAL_MODELS) >= 9
    assert len(JOB_READINESS_MATRIX) >= 9
    mapping = " ".join(a + " " + b for a, b in JOB_READINESS_MATRIX).lower()
    for concept in ("electricity", "pv", "battery", "energy", "supplier"):
        assert concept in mapping
