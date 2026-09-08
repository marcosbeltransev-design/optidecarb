"""OptiDecarb v1.3.2 evidence and data-forensics learning layer.

Builds on v1.3.1 without changing Optimization Model v0.3.0.
"""
from __future__ import annotations

from industrial_energy_lab.ui import energy_forensics as forensics
from industrial_energy_lab.ui import v131_app as base

_BASE_ENERGY_DATA = base._energy_data_lab
_BASE_MODEL_INTUITION = base._model_intuition_lab
_BASE_ABOUT = base._about_v131


def _energy_data_lab_v132(st) -> None:
    _BASE_ENERGY_DATA(st)
    st.divider()
    forensics.render_visual_forensics(st)
    st.divider()
    forensics.render_confidence_ladder(st)


def _model_intuition_lab_v132(st) -> None:
    _BASE_MODEL_INTUITION(st)
    st.divider()
    forensics.render_validation_priority(st)
    st.divider()
    forensics.render_trace_the_number(st)


def _about_v132(st) -> None:
    _BASE_ABOUT(st)
    st.subheader("v1.3.2 — Energy Data Forensics & Evidence Traceability")
    st.write(
        "This patch adds visual meter-data forensics, source-to-result traceability and sensitivity-driven data-priority training. The purpose is to help the student decide what to trust, what to challenge and what evidence to request next. Optimization Model v0.3.0 remains unchanged."
    )


def main() -> None:
    """Run the v1.3.1 learning shell with the v1.3.2 evidence layer."""
    base._energy_data_lab = _energy_data_lab_v132
    base._model_intuition_lab = _model_intuition_lab_v132
    base._about_v131 = _about_v132
    base.main()


if __name__ == "__main__":
    main()
