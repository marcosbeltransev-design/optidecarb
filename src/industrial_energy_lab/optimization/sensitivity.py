"""Deterministic one-at-a-time sensitivity analysis."""
from __future__ import annotations
from dataclasses import replace
import gc
from typing import Iterable
import pandas as pd
from industrial_energy_lab.optimization.frontier import cost_decarbonization_frontier
from industrial_energy_lab.optimization.model import OptimizationAssumptions, OptimizationResult
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions

DEFAULT_MULTIPLIERS=(0.8,0.9,1.0,1.1,1.2)
SENSITIVITY_FAMILIES=("electricity_price_multiplier","pv_capex_multiplier","battery_capex_multiplier","grid_emission_factor_multiplier","wacc","carbon_target")

def _row(variable,value,result):
    return {"input_variable":variable,"input_value":value,"status":result.status,"pv_capacity_kw":result.pv_capacity_kw,"battery_energy_capacity_kwh":result.battery_energy_capacity_kwh,"battery_power_capacity_kw":result.battery_power_capacity_kw,"annualized_cost_eur":result.objective_annualized_cost_eur,"project_npv_eur":result.project_npv_eur,"annual_saving_eur":result.annual_saving_vs_baseline_eur,"scenario_emissions_tco2":result.scenario_emissions_tco2,"co2_reduction_fraction":result.emissions_reduction_fraction,"solve_seconds":result.solve_seconds}

def run_sensitivity(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,*,export_price_eur_per_mwh=0.0,multipliers:Iterable[float]=DEFAULT_MULTIPLIERS,wacc_values:Iterable[float]|None=None,carbon_targets:Iterable[float]|None=None,variables:Iterable[str]|None=None)->pd.DataFrame:
    multipliers=tuple(float(v) for v in multipliers)
    if any(v<=0 for v in multipliers):raise ValueError("Sensitivity multipliers must be positive.")
    allowed=set(SENSITIVITY_FAMILIES); selected=allowed if variables is None else set(variables); unknown=selected-allowed
    if unknown:raise ValueError(f"Unknown sensitivity variables: {sorted(unknown)}")
    _,base=optimize_annual_system(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,carbon_target=0.0)
    rows=[]
    def solve(variable,value,varied_assumptions,varied_prices):
        if (variable!="wacc" and abs(value-1.0)<=1e-12) or (variable=="wacc" and abs(value-assumptions.wacc)<=1e-12):r=base
        else:
            dispatch,r=optimize_annual_system(load_frame,pv_profile_frame,varied_prices,grid_assumptions,varied_assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,carbon_target=0.0);del dispatch;gc.collect()
        rows.append(_row(variable,value,r))
    if "carbon_target" in selected:
        if carbon_targets is None:carbon_targets=(0.0,0.1,0.2,0.3,0.4,0.5)
        frontier=cost_decarbonization_frontier(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,carbon_targets=carbon_targets,economic_optimum=base)
        for fr in frontier.to_dict(orient='records'):
            rows.append({"input_variable":"carbon_target","input_value":float(fr['carbon_target']),"status":fr['status'],"pv_capacity_kw":fr['pv_capacity_kw'],"battery_energy_capacity_kwh":fr['battery_energy_capacity_kwh'],"battery_power_capacity_kw":fr['battery_power_capacity_kw'],"annualized_cost_eur":fr['annualized_cost_eur'],"project_npv_eur":None,"annual_saving_eur":fr['annual_saving_eur'],"scenario_emissions_tco2":fr['emissions_tco2'],"co2_reduction_fraction":fr['emissions_reduction_fraction'],"solve_seconds":fr['solve_seconds']})
        del frontier;gc.collect()
    for m in multipliers:
        if "electricity_price_multiplier" in selected:
            vp=price_frame.copy();vp['price_eur_per_mwh']=vp['price_eur_per_mwh']*m;solve('electricity_price_multiplier',m,assumptions,vp)
        if "pv_capex_multiplier" in selected:solve('pv_capex_multiplier',m,replace(assumptions,pv_capex_eur_per_kw=assumptions.pv_capex_eur_per_kw*m),price_frame)
        if "battery_capex_multiplier" in selected:solve('battery_capex_multiplier',m,replace(assumptions,battery_energy_capex_eur_per_kwh=assumptions.battery_energy_capex_eur_per_kwh*m,battery_power_capex_eur_per_kw=assumptions.battery_power_capex_eur_per_kw*m),price_frame)
        if "grid_emission_factor_multiplier" in selected:
            rr=_row('grid_emission_factor_multiplier',m,base)
            if rr['scenario_emissions_tco2'] is not None:rr['scenario_emissions_tco2']=float(rr['scenario_emissions_tco2'])*m
            rows.append(rr)
    if "wacc" in selected:
        if wacc_values is None:wacc_values=sorted({max(0.0,assumptions.wacc*m) for m in multipliers})
        for v in wacc_values:solve('wacc',float(v),replace(assumptions,wacc=float(v)),price_frame)
    return pd.DataFrame(rows)

def run_sensitivity_family(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,*,variable:str,export_price_eur_per_mwh=0.0,multipliers:Iterable[float]=DEFAULT_MULTIPLIERS,wacc_values:Iterable[float]|None=None,carbon_targets:Iterable[float]|None=None)->pd.DataFrame:
    if variable not in SENSITIVITY_FAMILIES:raise ValueError(f"Unknown sensitivity variable: {variable}")
    return run_sensitivity(load_frame,pv_profile_frame,price_frame,grid_assumptions,assumptions,export_price_eur_per_mwh=export_price_eur_per_mwh,multipliers=multipliers,wacc_values=wacc_values,carbon_targets=carbon_targets,variables=(variable,))

def battery_break_even_from_sensitivity(sensitivity:pd.DataFrame,*,capacity_tolerance_kwh:float=1e-6)->float|None:
    subset=sensitivity[sensitivity['input_variable']=='battery_capex_multiplier'].copy()
    if subset.empty:return None
    subset=subset.sort_values('input_value');caps=subset['battery_energy_capacity_kwh'].fillna(0).to_numpy(float);vals=subset['input_value'].to_numpy(float)
    for i in range(1,len(vals)):
        if caps[i-1]>capacity_tolerance_kwh and caps[i]<=capacity_tolerance_kwh:return float(vals[i])
    return None
