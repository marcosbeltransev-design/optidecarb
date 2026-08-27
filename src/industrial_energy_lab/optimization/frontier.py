"""Cost-decarbonization frontier utilities."""
from __future__ import annotations
from collections.abc import Iterable
import pandas as pd
from industrial_energy_lab.optimization.model import OptimizationAssumptions, OptimizationResult
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions

DEFAULT_CARBON_TARGETS=(0.0,0.10,0.20,0.30,0.40,0.50)

def _frontier_row(target: float,result: OptimizationResult,*,binding_override: bool|None=None,reused_economic_optimum: bool=False):
    return {"carbon_target":target,"status":result.status,"carbon_constraint_binding":result.carbon_constraint_binding if binding_override is None else binding_override,"reused_economic_optimum":reused_economic_optimum,"pv_capacity_kw":result.pv_capacity_kw,"battery_energy_capacity_kwh":result.battery_energy_capacity_kwh,"battery_power_capacity_kw":result.battery_power_capacity_kw,"initial_capex_eur":result.initial_capex_eur,"annualized_cost_eur":result.objective_annualized_cost_eur,"annual_saving_eur":result.annual_saving_vs_baseline_eur,"grid_import_mwh":result.grid_import_mwh,"grid_export_mwh":result.grid_export_mwh,"emissions_tco2":result.scenario_emissions_tco2,"emissions_reduction_fraction":result.emissions_reduction_fraction,"abatement_cost_eur_per_tco2":result.abatement_cost_eur_per_tco2,"model_build_seconds":result.model_build_seconds,"solve_seconds":result.solve_seconds,"total_seconds":result.total_seconds}

def cost_decarbonization_frontier(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,*,export_price_eur_per_mwh=0.0,carbon_targets:Iterable[float]=DEFAULT_CARBON_TARGETS,economic_optimum:OptimizationResult|None=None)->pd.DataFrame:
    targets=tuple(float(t) for t in carbon_targets)
    if not targets:return pd.DataFrame()
    if any(not 0<=t<=1 for t in targets):raise ValueError("All carbon targets must lie within [0, 1].")
    if economic_optimum is None:
        _,economic=optimize_annual_system(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,carbon_target=0.0)
    else:economic=economic_optimum
    if economic.status!="optimal":return pd.DataFrame([_frontier_row(t,economic) for t in targets])
    red=economic.emissions_reduction_fraction or 0.0
    rows=[]
    for t in targets:
        if t<=red+1e-8:
            rows.append(_frontier_row(t,economic,binding_override=False,reused_economic_optimum=True));continue
        _,r=optimize_annual_system(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,carbon_target=t)
        rows.append(_frontier_row(t,r))
    return pd.DataFrame(rows)
