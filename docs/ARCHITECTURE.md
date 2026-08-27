# Architecture decisions — v0.2

1. **Offline-first engine:** core/economics modules make no HTTP requests.
2. **UTC engine timeline:** DST/leap-year normalization occurs before data enter the engine.
3. **Dependency-light schemas:** dataclasses are retained rather than adding a validation framework prematurely.
4. **CSV + JSON metadata:** transparent and sufficient for 8,760-row screening datasets.
5. **Frozen historical regression:** Golden Case v1 keeps its original model/case identifiers after the model advances to v0.2.
6. **PV-first deterministic dispatch:** Iteration 2 validates physics without mixing in economic optimization.
7. **AC-bus battery convention:** charge/discharge flows are AC-side, while SOC is stored energy in kWh; conversion losses are explicit.
8. **No cyclic SOC enforcement in simulation:** initial and final SOC are reported; annual regression starts at minimum SOC. Cyclic boundary conditions belong to Iteration 3 optimization.
9. **No database/backend/auth:** none is required for the screening engine.
10. **Optimization is a separate layer:** Pyomo/HiGHS will consume the validated physical/economic conventions rather than replacing them.
