# Architecture decisions — v0.1

1. **Offline-first engine:** core/economics modules make no HTTP requests.
2. **UTC engine timeline:** DST normalization occurs before data enter the engine.
3. **Dependency-light schemas:** dataclasses are used in Iteration 1 rather than adding validation frameworks prematurely.
4. **CSV + JSON metadata:** transparent, recruiter-readable and sufficient for small 8,760-row datasets.
5. **Regression-first roadmap:** a golden grid-only baseline is frozen before PV/battery/optimization are introduced.
6. **No database/backend/auth:** none is required for the screening engine.
