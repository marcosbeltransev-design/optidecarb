import importlib.util
from pathlib import Path


def test_cv_reliability_healthcheck():
    from industrial_energy_lab.learning import INDUSTRY_CASES
    from industrial_energy_lab.learning.readiness import (
        DATA_QUALITY_CASES,
        DIAGNOSTIC_QUESTIONS,
        SKILLS,
    )
    from industrial_energy_lab.ui import APP_VERSION, v131_app

    root = Path(__file__).resolve().parents[2]
    entrypoint = root / "app.py"
    spec = importlib.util.spec_from_file_location("optidecarb_app_entrypoint", entrypoint)
    assert spec is not None and spec.loader is not None
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)

    assert callable(app_module.main)
    assert callable(v131_app.main)
    assert APP_VERSION == "1.3.1"

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