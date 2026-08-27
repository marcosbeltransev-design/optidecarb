from types import SimpleNamespace

import pytest

import industrial_energy_lab.ui.services as services


def test_ui_baseline_loads_complete_demo_case():
    params = services.default_parameters()
    baseline, load, prices = services.run_baseline_request(params)
    assert baseline.annual_consumption_mwh == pytest.approx(22_000.0, abs=1e-5)
    assert len(load) == len(prices) == 8760


def test_ui_optimization_service_forwards_validated_engine_inputs(monkeypatch):
    captured = {}
    sentinel_dispatch = object()
    sentinel_result = SimpleNamespace(status="optimal")

    def fake_optimize(load, pv, prices, grid, assumptions, **kwargs):
        captured.update(
            rows=len(load),
            grid_ef=grid.emissions_factor_kg_co2_per_mwh,
            pv_capex=assumptions.pv_capex_eur_per_kw,
            export_price=kwargs["export_price_eur_per_mwh"],
            carbon_target=kwargs["carbon_target"],
        )
        return sentinel_dispatch, sentinel_result

    monkeypatch.setattr(services, "optimize_annual_system", fake_optimize)
    params = services.default_parameters()
    dispatch, result = services.run_optimization_request(params, carbon_target=0.40)
    assert dispatch is sentinel_dispatch
    assert result is sentinel_result
    assert captured == {
        "rows": 8760,
        "grid_ef": 180.0,
        "pv_capex": 1600.0,
        "export_price": 20.0,
        "carbon_target": 0.40,
    }
