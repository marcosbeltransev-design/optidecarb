from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


def test_streamlit_app_starts_and_navigation_is_present():
    at = AppTest.from_file(ROOT / "app.py", default_timeout=15).run()
    assert not at.exception
    assert at.title and at.title[0].value == "Industrial Energy Lab"
    assert at.radio
    options = list(at.radio[0].options)
    assert "Inputs" in options
    assert "Sensitivity" in options
    assert "Methodology" in options
