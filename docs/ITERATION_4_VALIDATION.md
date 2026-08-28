# Iteration 4 validation record

Iteration 4 freezes the Streamlit engineering interface on top of the v0.3 optimization engine.

## Executed locally

- active-repository editable reinstall;
- 66 tests passed;
- Python compile check;
- demo dataset/metadata reproducibility check;
- clean-clone regression;
- nine-section UI structure and service wiring;
- centralized explainability/help coverage;
- Golden Cases v1-v3 preserved by the full test suite.

## Native Streamlit check

`tests/integration/test_streamlit_smoke.py` uses `streamlit.testing.v1.AppTest`. The test is intentionally optional locally and mandatory in CI when the `app` extra is installed.

The current sandbox cannot resolve/download the Streamlit package, including via direct wheel-install attempts. Therefore AppTest, browser visual verification and screenshot capture cannot be executed in this runtime.

## Deployment boundary

Public Streamlit Community Cloud deployment also requires a standalone GitHub repository. The connected GitHub integration currently exposes only the unrelated `notas-albinegras` repository and does not expose repository creation. OptiDecarb is deliberately not mixed into that project.

These two constraints are external deployment/acceptance boundaries. The v0.4 code is frozen so Iteration 5 can proceed without turning the UI into an open-ended redesign cycle.
