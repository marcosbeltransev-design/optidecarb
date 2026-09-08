from pathlib import Path


def test_cv_reliability_healthcheck():
    import app
    from industrial_energy_lab.learning import INDUSTRY_CASES
    from industrial_energy_lab.learning.readiness import (
        DATA_QUALITY_CASES,
        DIAGNOSTIC_QUESTIONS,
        SKILLS,
    )
    from industrial_energy_lab.ui import APP_VERSION, v13_app

    assert callable(app.main)
    assert callable(v13_app.main)
    assert APP_VERSION == "1.3.0"

    root = Path(__file__).resolve().parents[2]
    for relative in (
        "assets/optidecarb-logo.svg",
        "assets/optidecarb-icon.svg",
        "assets/optidecarb-hero.svg",
        "portfolio/index.html",
        "docs/DEPLOYMENT_RECOVERY.md",
    ):
        assert (root / relative).is_file(), relative

    skill_ids = [item.skill_id for item in SKILLS]
    diagnostic_ids = [item.question_id for item in DIAGNOSTIC_QUESTIONS]
    data_case_ids = [item.case_id for item in DATA_QUALITY_CASES]

    assert SKILLS and len(skill_ids) == len(set(skill_ids))
    assert DIAGNOSTIC_QUESTIONS and len(diagnostic_ids) == len(set(diagnostic_ids))
    assert DATA_QUALITY_CASES and len(data_case_ids) == len(set(data_case_ids))
    assert INDUSTRY_CASES

    landing = (root / "portfolio/index.html").read_text(encoding="utf-8")
    assert "https://optidecarb.streamlit.app" in landing
    assert "https://github.com/marcosbeltransev-design/optidecarb" in landing
    assert "Industrial Energy Optimization &amp; Learning" in landing
    assert "AI-assisted" in landing
