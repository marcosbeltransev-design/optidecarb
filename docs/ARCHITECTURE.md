# Architecture decisions — v0.4 candidate

1. **Offline-first engine:** `core/`, `economics/`, `optimization/` and `explainability/` make no HTTP requests.
2. **UTC engine timeline:** all annual inputs are normalized before entering the engine; the demo uses exactly 8,760 uninterrupted UTC hours.
3. **Frozen regression layers:** Golden Cases v1, v2 and v3 preserve their version identifiers and numerical behavior.
4. **Sparse LP remains the model:** Streamlit never reconstructs energy balances or objective terms.
5. **UI service boundary:** `ui/services.py` is the only application-facing orchestration layer for validated datasets, baseline, optimizer, frontier and sensitivity.
6. **Central explainability:** labels/help are read from `explainability/metrics.py`; page-specific copies are avoided.
7. **Controlled reruns:** expensive optimization occurs only after explicit form/button actions, not on every widget change.
8. **On-demand sensitivity:** one family is solved at a time. Full-batch sensitivity is a scripting capability, not the interactive default.
9. **Minimal state:** Streamlit session state stores only current assumptions, custom load and last requested results. It is not persistence.
10. **No database/backend/auth:** v1 requires none.
11. **Validated uploads:** a custom load must contain 8,760 valid hours and align to the existing PV/price UTC snapshot.
12. **Native UI help:** Streamlit `help` controls expose definition, unit, usefulness, calculation, interpretation, relationships, source/assumption status and caveats.
13. **Plotly is presentation only:** plots receive engine outputs and do not change calculations.
14. **Deployment target:** Streamlit Community Cloud remains the preferred zero-cost target once a standalone GitHub remote exists.
15. **Release-candidate status:** this sandbox lacks Streamlit, so native app/browser verification is deferred rather than simulated or claimed.
