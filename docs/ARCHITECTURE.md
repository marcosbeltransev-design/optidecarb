# Architecture decisions — v1.1 Student Learning Lab

1. **Offline-first engine:** `core/`, `economics/`, `optimization/` and `explainability/` make no runtime HTTP requests.
2. **UTC engine timeline:** annual inputs are normalized before entering the engine; both demo and representative case use exactly 8,760 uninterrupted UTC hours.
3. **Frozen regression layers:** Golden Cases v1, v2 and v3 plus `ceramic-castellon-v1` preserve numerical behavior independently from education/UI releases.
4. **Sparse LP remains the model:** Streamlit and Student Learning Lab never reconstruct optimization equations.
5. **UI service boundary:** `ui/services.py` remains the application-facing orchestration layer for validated datasets, baseline, optimizer, frontier and sensitivity.
6. **Central explainability:** labels/help come from `explainability/metrics.py` and `explainability/glossary.py`; page-specific copies are avoided where structured metadata exists.
7. **Worked-calculation layer:** `explainability/calculations.py` explains already-computed outputs as formula → scenario inputs → substitution → result → unit check. It does not recalculate the engineering solution.
8. **Student learning layer:** `learning/` contains small deterministic examples, guided-experiment definitions, prediction/comparison helpers and hourly explanations.
9. **Active learning uses the real engine:** full-year student experiments call the same validated UI/engine services as normal optimization. They are deliberately one-at-a-time and on demand.
10. **Small examples stay small:** MW/MWh, CRF and three-hour battery labs use hand-checkable deterministic calculations instead of launching 8,760-hour LPs.
11. **Controlled reruns:** expensive optimization occurs only after explicit form/button actions, not on every widget change.
12. **On-demand sensitivity:** one family is solved at a time. Full-batch sensitivity is a scripting capability, not the interactive default.
13. **Minimal state:** Streamlit session state stores current assumptions, last requested results and optional session-only student progress. It is not persistence.
14. **No database/backend/auth:** v1.1 requires none.
15. **Validated uploads:** a custom load must contain 8,760 valid hours and align to the active PV/price UTC snapshot.
16. **Native UI help:** Streamlit `help` controls expose definition, unit, usefulness, calculation, interpretation, relationships, source/assumption status and caveats.
17. **Plotly is presentation only:** plots receive engine outputs and do not change calculations.
18. **Model version remains v0.3.0:** v1.1 changes education, UI and docs only; physical and optimization equations are unchanged.
19. **Deployment target:** Streamlit Community Cloud remains the preferred zero-cost target once a standalone GitHub remote exists.
20. **Runtime limitation:** this sandbox still lacks Streamlit, so native AppTest/browser verification is an external acceptance check rather than something simulated or claimed.

## Dependency direction

```text
public-data adapters / offline snapshots
                |
                v
             case bundles
                |
                +-------------------------+
                |                         |
                v                         v
      core / economics / optimization   explainability
                |                         |
                +-----------+-------------+
                            v
                       ui services
                            |
                  +---------+---------+
                  |                   |
                  v                   v
             Streamlit UI        learning/
                                      |
                                      +--> hand-checkable examples
                                      +--> guided experiments
                                      +--> scenario comparison
                                      +--> hourly explanations
```

The key rule is that education explains or calls the engine; it never becomes a second engineering model.
