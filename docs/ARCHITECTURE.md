# Architecture decisions — v0.3

1. **Offline-first engine:** `core/`, `economics/`, `optimization/` and `explainability/` make no HTTP requests.
2. **UTC engine timeline:** DST/leap-year normalization occurs before data enter the engine; validated annual datasets contain exactly 8,760 uninterrupted UTC hours.
3. **Frozen historical regression:** Golden Cases v1 and v2 retain their original model/case identifiers after optimization advances to v0.3.
4. **Validated physical conventions are reused:** optimization keeps the AC-bus battery convention, explicit losses, PV-only charging and no CO2 export credit established by the simulator.
5. **Sparse linear program:** annual sizing/dispatch is formulated as an LP with `4n+3` decision variables after removing redundant grid-import/export variables.
6. **Open-source solver:** v0.3 solves with HiGHS through SciPy `linprog`; the solver adapter is an implementation detail, not the architecture.
7. **Cyclic optimization SOC:** the annual LP enforces final SOC equal to the configured initial SOC fraction of optimized energy capacity, preventing free initial energy.
8. **Anti-arbitrage assumptions:** batteries charge only from PV allocation; export price must be strictly below every import price.
9. **Annualized objective, investment post-processing:** the LP minimizes equivalent annual cost; initial CAPEX, NPV and payback are calculated after solving.
10. **Explicit carbon constraint:** grid-related emissions equal grid imports times an explicit constant factor; exports receive no CO2 credit.
11. **On-demand sensitivity:** interactive use solves one sensitivity family at a time rather than an unnecessary full batch.
12. **Central explainability registry:** UI help must consume one structured metric/input registry rather than duplicate prose.
13. **No database/backend/auth:** none is required for v1 screening.
14. **UI remains separate:** Iteration 4 may display results but must not reimplement engineering equations.
