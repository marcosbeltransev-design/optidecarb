from pathlib import Path

from industrial_energy_lab.learning.advanced_energy import (
    CARBON_FRONTIER,
    FORMULA_LESSONS,
    INTERVIEW_DEFENCE,
    PREDICTION_LESSONS,
    SCREENING_VS_FEASIBILITY,
    TRACEABILITY_CARDS,
    TRANSFER_CASE,
    prediction_by_id,
)
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION


def test_active_learning_version_does_not_change_model_version():
    assert APP_VERSION == "1.3.1"
    assert OPTIMIZATION_MODEL_VERSION == "0.3.0"


def test_formula_lessons_are_unique_and_energy_specific():
    ids = [x.lesson_id for x in FORMULA_LESSONS]
    assert len(FORMULA_LESSONS) >= 6
    assert len(ids) == len(set(ids))
    joined = " ".join(x.title + x.formula + x.units + x.example for x in FORMULA_LESSONS).lower()
    for token in ("mw", "mwh", "pv", "battery", "co₂", "payback"):
        assert token in joined
    for lesson in FORMULA_LESSONS:
        assert lesson.formula
        assert lesson.units
        assert lesson.intuition
        assert lesson.example
        assert lesson.common_error


def test_prediction_lessons_use_frozen_case_behaviour():
    ids = [x.lesson_id for x in PREDICTION_LESSONS]
    assert len(ids) == len(set(ids))
    assert len(PREDICTION_LESSONS) >= 5
    for lesson in PREDICTION_LESSONS:
        assert lesson.correct in lesson.options
        assert lesson.before and lesson.after and lesson.why and lesson.next_check
        assert prediction_by_id(lesson.lesson_id) == lesson
    carbon = prediction_by_id("carbon_20_to_40")
    assert "2.97" in carbon.before
    assert "4.25" in carbon.after
    assert "2.46" in carbon.after


def test_carbon_frontier_teaches_binding_transition_without_changing_goldens():
    by_target = {x["target_pct"]: x for x in CARBON_FRONTIER}
    assert by_target[20]["binding"] is False
    assert by_target[30]["binding"] is False
    assert by_target[40]["binding"] is True
    assert by_target[20]["battery_mwh"] == 0.0
    assert by_target[40]["battery_mwh"] == 2.46
    assert by_target[40]["pv_mw"] == 4.25
    assert by_target[50]["battery_mwh"] == 6.83
    assert by_target[40]["annualized_cost_eur"] > by_target[30]["annualized_cost_eur"]


def test_traceability_and_project_maturity_content_is_explicit():
    assert len(TRACEABILITY_CARDS) >= 3
    for card in TRACEABILITY_CARDS:
        assert card["knows"]
        assert card["assumes"]
        assert card["does_not_know"]
    assert len(SCREENING_VS_FEASIBILITY) >= 6
    joined = " ".join(" ".join(row) for row in SCREENING_VS_FEASIBILITY).lower()
    for term in ("load", "pv", "capex", "electricity", "export", "decision"):
        assert term in joined


def test_transfer_case_tests_reasoning_beyond_castellon():
    assert "Illustrative" in TRANSFER_CASE["label"]
    assert len(TRANSFER_CASE["questions"]) == len(TRANSFER_CASE["worked"])
    text = " ".join(TRANSFER_CASE["facts"] + TRANSFER_CASE["questions"] + TRANSFER_CASE["worked"]).lower()
    for term in ("load factor", "pv", "gwh", "mw", "hourly"):
        assert term in text


def test_interview_defence_remains_energy_specific():
    assert len(INTERVIEW_DEFENCE) >= 6
    text = " ".join(q + " " + a for q, a in INTERVIEW_DEFENCE).lower()
    for term in ("8,760", "linear", "battery", "co₂", "omie", "mwp"):
        assert term in text


def test_visual_layer_uses_committed_offline_case_files():
    root = Path(__file__).resolve().parents[2]
    assert (root / "cases/ceramic_castellon/data/industrial_load_8760.csv").is_file()
    assert (root / "cases/ceramic_castellon/data/pv_profile_8760.csv").is_file()
