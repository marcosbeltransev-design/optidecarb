import numpy as np
import pytest

from industrial_energy_lab.optimization.model import (
    OptimizationAssumptions,
    OptimizationBounds,
    optimize_lp,
)


def assumptions(*, pv_capex=1e6, battery_capex=1e6, battery_power_capex=1e6,
                max_pv=100.0, max_be=100.0, max_bp=100.0,
                eta_c=1.0, eta_d=1.0):
    return OptimizationAssumptions(
        pv_capex_eur_per_kw=pv_capex,
        pv_opex_eur_per_kw_year=0.0,
        pv_lifetime_years=1,
        battery_energy_capex_eur_per_kwh=battery_capex,
        battery_power_capex_eur_per_kw=battery_power_capex,
        battery_opex_eur_per_kwh_year=0.0,
        battery_opex_eur_per_kw_year=0.0,
        battery_lifetime_years=1,
        wacc=0.0,
        project_life_years=1,
        battery_charge_efficiency=eta_c,
        battery_discharge_efficiency=eta_d,
        battery_min_soc_fraction=0.0,
        battery_max_soc_fraction=1.0,
        battery_initial_soc_fraction=0.0,
        bounds=OptimizationBounds(max_pv, max_be, max_bp),
    )


def solve(load, cf, price, a, *, target=0.0, grid_ef=180.0, export=0.0):
    return optimize_lp(
        np.asarray(load, float), np.asarray(cf, float), np.asarray(price, float), export,
        grid_emission_factor_kg_co2_per_mwh=grid_ef,
        assumptions=a,
        carbon_target=target,
    )


def test_high_capex_returns_no_investment():
    dispatch, result = solve([10.0], [1.0], [100.0], assumptions())
    assert result.status == "optimal"
    assert result.pv_capacity_kw == pytest.approx(0.0, abs=1e-8)
    assert result.battery_energy_capacity_kwh == pytest.approx(0.0, abs=1e-8)
    assert result.grid_import_mwh == pytest.approx(0.01)
    assert dispatch["grid_import_kwh"].iloc[0] == pytest.approx(10.0)


def test_known_one_hour_pv_optimum_is_load_capacity():
    a = assumptions(pv_capex=0.5, max_pv=20.0)
    _, result = solve([10.0], [1.0], [1000.0], a)
    assert result.pv_capacity_kw == pytest.approx(10.0, abs=1e-6)
    assert result.grid_import_mwh == pytest.approx(0.0, abs=1e-9)
    assert result.grid_export_mwh == pytest.approx(0.0, abs=1e-9)


def test_cheap_storage_enters_when_it_can_shift_pv_to_expensive_hour():
    a = assumptions(
        pv_capex=0.1, battery_capex=0.1, battery_power_capex=0.1,
        max_pv=20.0, max_be=20.0, max_bp=20.0,
    )
    _, result = solve([0.0, 10.0], [1.0, 0.0], [10.0, 1000.0], a)
    assert result.status == "optimal"
    assert result.battery_energy_capacity_kwh > 9.9
    assert result.battery_power_capacity_kw > 9.9
    assert result.grid_import_mwh == pytest.approx(0.0, abs=1e-8)


def test_known_carbon_constraint_requires_five_kw_pv():
    a = assumptions(pv_capex=1000.0, max_pv=20.0, max_be=0.0, max_bp=0.0)
    _, result = solve([10.0], [1.0], [100.0], a, target=0.50)
    assert result.status == "optimal"
    assert result.pv_capacity_kw == pytest.approx(5.0, abs=1e-6)
    assert result.emissions_reduction_fraction == pytest.approx(0.50, abs=1e-7)
    assert result.carbon_constraint_binding is True


def test_infeasible_carbon_target_is_not_solver_error():
    a = assumptions(max_pv=0.0, max_be=0.0, max_bp=0.0)
    dispatch, result = solve([10.0], [0.0], [100.0], a, target=0.10)
    assert dispatch is None
    assert result.status == "infeasible"


def test_export_price_must_be_below_import_price():
    with pytest.raises(ValueError, match="Export price"):
        solve([10.0], [1.0], [50.0], assumptions(), export=50.0)


def test_invalid_carbon_target_is_rejected_before_solver():
    with pytest.raises(ValueError, match="carbon_target"):
        solve([10.0], [1.0], [100.0], assumptions(), target=1.01)


def test_storage_soc_is_cyclic_and_energy_conserved():
    a = assumptions(
        pv_capex=0.1, battery_capex=0.1, battery_power_capex=0.1,
        max_pv=20.0, max_be=20.0, max_bp=20.0, eta_c=0.9, eta_d=0.9,
    )
    dispatch, result = solve([0.0, 8.0], [1.0, 0.0], [10.0, 1000.0], a)
    assert result.battery_energy_capacity_kwh > 0
    assert dispatch["soc_kwh"].iloc[-1] == pytest.approx(0.0, abs=1e-7)
    delta = dispatch["soc_kwh"] - dispatch["soc_start_kwh"]
    expected = 0.9 * dispatch["battery_charge_kwh"] - dispatch["battery_discharge_kwh"] / 0.9
    assert np.allclose(delta, expected, atol=1e-7)


def test_optimal_dispatch_has_no_simultaneous_physical_flows():
    a = assumptions(
        pv_capex=0.1, battery_capex=0.1, battery_power_capex=0.1,
        max_pv=20.0, max_be=20.0, max_bp=20.0,
    )
    dispatch, _ = solve([5.0, 10.0, 5.0], [0.0, 1.0, 0.0], [100.0, 100.0, 1000.0], a)
    assert np.max(dispatch["battery_charge_kwh"] * dispatch["battery_discharge_kwh"]) <= 1e-8
    assert np.max(dispatch["grid_import_kwh"] * dispatch["grid_export_kwh"]) <= 1e-8
