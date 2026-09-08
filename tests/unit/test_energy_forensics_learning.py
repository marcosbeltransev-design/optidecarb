from industrial_energy_lab.learning.energy_forensics import (
    DATA_CONFIDENCE_LADDER,
    FORENSIC_CASES,
    TRACE_CHAINS,
    VALIDATION_PRIORITIES,
    forensic_case,
)
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui import v132_app
from industrial_energy_lab.utils.version import OPTIMIZATION_MODEL_VERSION


def test_forensics_release_preserves_engine():
    assert APP_VERSION == "1.3.2"
    assert OPTIMIZATION_MODEL_VERSION == "0.3.0"
    assert callable(v132_app.main)


def test_forensic_cases_are_unique_and_decision_oriented():
    ids = [case.case_id for case in FORENSIC_CASES]
    assert len(FORENSIC_CASES) >= 5
    assert len(ids) == len(set(ids))
    for case in FORENSIC_CASES:
        assert len(case.x) == len(case.y)
        assert case.correct in case.options
        assert case.why
        assert case.first_action
        assert case.professional_decision
        assert forensic_case(case.case_id) == case
    joined = " ".join(
        " ".join((case.title, case.context, case.y_label, case.why, *case.options))
        for case in FORENSIC_CASES
    ).lower()
    for concept in ("missing", "duplicate", "flatline", "unit", "export"):
        assert concept in joined


def test_trace_chains_connect_evidence_to_decisions():
    assert len(TRACE_CHAINS) >= 4
    for chain in TRACE_CHAINS:
        assert chain["title"]
        assert len(chain["steps"]) == 5
        assert all(label and explanation for label, explanation in chain["steps"])
    joined = " ".join(label + " " + text for chain in TRACE_CHAINS for label, text in chain["steps"]).lower()
    for concept in ("15,000", "pvgis", "omie", "red eléctrica", "40%"):
        assert concept in joined


def test_validation_priorities_use_frozen_sensitivity_results_without_overclaiming():
    by_name = {item["assumption"]: item for item in VALIDATION_PRIORITIES}
    assert by_name["Electricity-price level"]["pv_before_mw"] == 2.972
    assert by_name["Electricity-price level"]["pv_after_mw"] == 3.193
    assert by_name["PV CAPEX"]["pv_after_mw"] == 2.788
    assert by_name["WACC"]["pv_after_mw"] == 2.870
    assert by_name["Battery CAPEX"]["pv_after_mw"] == 2.972
    assert all(item["next_data"] and item["why"] for item in VALIDATION_PRIORITIES)


def test_data_confidence_ladder_labels_assumptions_and_proxies_explicitly():
    assert len(DATA_CONFIDENCE_LADDER) == 5
    text = " ".join(" ".join(row) for row in DATA_CONFIDENCE_LADDER).lower()
    for concept in ("measured", "official", "supplier", "proxy", "assumption"):
        assert concept in text
