"""Sparse linear techno-economic sizing model solved with HiGHS via SciPy."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, csr_matrix

from industrial_energy_lab.economics.cashflows import capital_recovery_factor
from industrial_energy_lab.economics.emissions import abatement_cost_eur_per_tco2
from industrial_energy_lab.economics.npv import npv
from industrial_energy_lab.economics.payback import simple_payback_years

NUMERICAL_TOLERANCE = 1e-7
THROUGHPUT_TIE_BREAK_EUR_PER_KWH = 1e-9


@dataclass(frozen=True)
class OptimizationBounds:
    max_pv_capacity_kw: float
    max_battery_energy_kwh: float
    max_battery_power_kw: float

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative.")


@dataclass(frozen=True)
class OptimizationAssumptions:
    pv_capex_eur_per_kw: float
    pv_opex_eur_per_kw_year: float
    pv_lifetime_years: int
    battery_energy_capex_eur_per_kwh: float
    battery_power_capex_eur_per_kw: float
    battery_opex_eur_per_kwh_year: float
    battery_opex_eur_per_kw_year: float
    battery_lifetime_years: int
    wacc: float
    project_life_years: int
    battery_charge_efficiency: float
    battery_discharge_efficiency: float
    battery_min_soc_fraction: float
    battery_max_soc_fraction: float
    battery_initial_soc_fraction: float
    bounds: OptimizationBounds

    def __post_init__(self) -> None:
        for name in (
            "pv_capex_eur_per_kw", "pv_opex_eur_per_kw_year",
            "battery_energy_capex_eur_per_kwh", "battery_power_capex_eur_per_kw",
            "battery_opex_eur_per_kwh_year", "battery_opex_eur_per_kw_year", "wacc",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative.")
        if self.pv_lifetime_years <= 0 or self.battery_lifetime_years <= 0:
            raise ValueError("Technology lifetimes must be positive.")
        if self.project_life_years <= 0:
            raise ValueError("project_life_years must be positive.")
        if self.project_life_years > min(self.pv_lifetime_years, self.battery_lifetime_years):
            raise ValueError("project_life_years cannot exceed the shortest technology lifetime in the simplified no-replacement NPV model.")
        if not 0 < self.battery_charge_efficiency <= 1:
            raise ValueError("battery_charge_efficiency must be within (0, 1].")
        if not 0 < self.battery_discharge_efficiency <= 1:
            raise ValueError("battery_discharge_efficiency must be within (0, 1].")
        if not 0 <= self.battery_min_soc_fraction <= self.battery_max_soc_fraction <= 1:
            raise ValueError("SOC fractions must satisfy 0 <= min <= max <= 1.")
        if not self.battery_min_soc_fraction <= self.battery_initial_soc_fraction <= self.battery_max_soc_fraction:
            raise ValueError("battery_initial_soc_fraction must lie within SOC bounds.")


@dataclass(frozen=True)
class OptimizationResult:
    status: str
    solver_message: str
    objective_annualized_cost_eur: float | None
    pv_capacity_kw: float | None
    battery_energy_capacity_kwh: float | None
    battery_power_capacity_kw: float | None
    load_mwh: float | None
    pv_generation_mwh: float | None
    pv_self_consumption_mwh: float | None
    pv_export_mwh: float | None
    battery_charge_mwh: float | None
    battery_discharge_mwh: float | None
    battery_losses_mwh: float | None
    grid_import_mwh: float | None
    grid_export_mwh: float | None
    self_consumption_ratio: float | None
    self_sufficiency_ratio: float | None
    annualized_pv_cost_eur: float | None
    annualized_battery_cost_eur: float | None
    annual_pv_opex_eur: float | None
    annual_battery_opex_eur: float | None
    grid_purchase_cost_eur: float | None
    export_revenue_eur: float | None
    baseline_annual_cost_eur: float | None
    annual_saving_vs_baseline_eur: float | None
    initial_capex_eur: float | None
    project_npv_eur: float | None
    simple_payback_years: float | None
    baseline_emissions_tco2: float | None
    scenario_emissions_tco2: float | None
    emissions_reduction_tco2: float | None
    emissions_reduction_fraction: float | None
    abatement_cost_eur_per_tco2: float | None
    carbon_target: float | None
    carbon_constraint_binding: bool | None
    carbon_constraint_slack_tco2: float | None
    model_build_seconds: float
    solve_seconds: float
    total_seconds: float
    solver_backend: str


@dataclass(frozen=True)
class _VariableIndex:
    pv_capacity: int
    battery_energy: int
    battery_power: int
    pv_to_load: slice
    pv_to_battery: slice
    battery_discharge: slice
    soc: slice
    n_variables: int


def _indices(n: int) -> _VariableIndex:
    offset = 3
    blocks = []
    for _ in range(4):
        blocks.append(slice(offset, offset + n))
        offset += n
    return _VariableIndex(0, 1, 2, *blocks, n_variables=offset)


def _si(block: slice, t: int) -> int:
    assert block.start is not None
    return block.start + t


def _as_float_array(values: Sequence[float] | np.ndarray | pd.Series, name: str) -> np.ndarray:
    a = np.asarray(values, dtype=float)
    if a.ndim != 1 or a.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional series.")
    if not np.isfinite(a).all():
        raise ValueError(f"{name} must contain only finite values.")
    return a


def _price_array(value, n: int, name: str) -> np.ndarray:
    if np.isscalar(value):
        return np.full(n, float(value), dtype=float)
    a = _as_float_array(value, name)
    if a.size != n:
        raise ValueError(f"{name} must have the same length as load.")
    return a


def validate_optimization_inputs(load_kwh, pv_capacity_factor, import_price_eur_per_mwh,
                                 export_price_eur_per_mwh, grid_emission_factor_kg_co2_per_mwh,
                                 carbon_target):
    load = _as_float_array(load_kwh, "load_kwh")
    cf = _as_float_array(pv_capacity_factor, "pv_capacity_factor")
    buy = _as_float_array(import_price_eur_per_mwh, "import_price_eur_per_mwh")
    if load.size != cf.size or load.size != buy.size:
        raise ValueError("Load, PV profile and import-price series must have equal length.")
    sell = _price_array(export_price_eur_per_mwh, load.size, "export_price_eur_per_mwh")
    if (load < 0).any():
        raise ValueError("Load must be non-negative.")
    if ((cf < 0) | (cf > 1)).any():
        raise ValueError("PV capacity factor must lie within [0, 1].")
    if grid_emission_factor_kg_co2_per_mwh < 0:
        raise ValueError("Grid emission factor must be non-negative.")
    if carbon_target is not None and not 0 <= carbon_target <= 1:
        raise ValueError("carbon_target must lie within [0, 1].")
    if np.any(sell >= buy - NUMERICAL_TOLERANCE):
        raise ValueError("Export price must be strictly below import price in every interval to prevent grid arbitrage/degeneracy in the LP.")
    return load, cf, buy, sell


def _add(rows, cols, data, row, coeffs):
    for col, value in coeffs.items():
        if value != 0:
            rows.append(row); cols.append(col); data.append(float(value))


def _build_lp(load, cf, buy, sell, grid_ef, assumptions, carbon_target):
    n = len(load); idx = _indices(n)
    c = np.zeros(idx.n_variables)
    pv_crf = capital_recovery_factor(assumptions.wacc, assumptions.pv_lifetime_years)
    bat_crf = capital_recovery_factor(assumptions.wacc, assumptions.battery_lifetime_years)
    pv_unit = assumptions.pv_capex_eur_per_kw * pv_crf + assumptions.pv_opex_eur_per_kw_year
    be_unit = assumptions.battery_energy_capex_eur_per_kwh * bat_crf + assumptions.battery_opex_eur_per_kwh_year
    bp_unit = assumptions.battery_power_capex_eur_per_kw * bat_crf + assumptions.battery_opex_eur_per_kw_year
    c[idx.pv_capacity] = pv_unit - float(np.sum(sell / 1000.0 * cf))
    c[idx.battery_energy] = be_unit
    c[idx.battery_power] = bp_unit
    c[idx.pv_to_load] = (sell - buy) / 1000.0
    c[idx.pv_to_battery] = sell / 1000.0 + THROUGHPUT_TIE_BREAK_EUR_PER_KWH
    c[idx.battery_discharge] = -buy / 1000.0 + THROUGHPUT_TIE_BREAK_EUR_PER_KWH

    er=[]; ec=[]; ed=[]; beq=[]; row=0
    ecff=assumptions.battery_charge_efficiency; edff=assumptions.battery_discharge_efficiency
    init=assumptions.battery_initial_soc_fraction
    for t in range(n):
        coeff={_si(idx.soc,t):1.0, _si(idx.pv_to_battery,t):-ecff, _si(idx.battery_discharge,t):1.0/edff}
        if t==0: coeff[idx.battery_energy]=-init
        else: coeff[_si(idx.soc,t-1)] = -1.0
        _add(er,ec,ed,row,coeff); beq.append(0.0); row+=1
    _add(er,ec,ed,row,{_si(idx.soc,n-1):1.0, idx.battery_energy:-init}); beq.append(0.0); row+=1
    Aeq=coo_matrix((ed,(er,ec)),shape=(row,idx.n_variables)).tocsr()

    ur=[]; uc=[]; ud=[]; bub=[]; row=0
    mn=assumptions.battery_min_soc_fraction; mx=assumptions.battery_max_soc_fraction
    for t in range(n):
        _add(ur,uc,ud,row,{_si(idx.pv_to_load,t):1,_si(idx.pv_to_battery,t):1,idx.pv_capacity:-cf[t]}); bub.append(0); row+=1
        _add(ur,uc,ud,row,{_si(idx.pv_to_load,t):1,_si(idx.battery_discharge,t):1}); bub.append(load[t]); row+=1
        _add(ur,uc,ud,row,{_si(idx.pv_to_battery,t):1,idx.battery_power:-1}); bub.append(0); row+=1
        _add(ur,uc,ud,row,{_si(idx.battery_discharge,t):1,idx.battery_power:-1}); bub.append(0); row+=1
        _add(ur,uc,ud,row,{_si(idx.soc,t):1,idx.battery_energy:-mx}); bub.append(0); row+=1
        _add(ur,uc,ud,row,{_si(idx.soc,t):-1,idx.battery_energy:mn}); bub.append(0); row+=1
    if carbon_target is not None and carbon_target > 0 and grid_ef > 0:
        k=grid_ef/1_000_000.0
        coeff={}
        for t in range(n):
            coeff[_si(idx.pv_to_load,t)] = -k
            coeff[_si(idx.battery_discharge,t)] = -k
        _add(ur,uc,ud,row,coeff)
        baseline=float(load.sum()*k)
        bub.append(-carbon_target*baseline); row+=1
    Aub=coo_matrix((ud,(ur,uc)),shape=(row,idx.n_variables)).tocsr()
    bounds=[(0,assumptions.bounds.max_pv_capacity_kw),(0,assumptions.bounds.max_battery_energy_kwh),(0,assumptions.bounds.max_battery_power_kw)] + [(0,None)]*(4*n)
    meta={"pv_crf":pv_crf,"battery_crf":bat_crf,"baseline_grid_cost":float(np.sum(load/1000*buy)),"baseline_emissions":float(load.sum()*grid_ef/1_000_000)}
    return c,Aub,np.asarray(bub),Aeq,np.asarray(beq),bounds,idx,meta


def _empty_result(status, message, build, solve, total, carbon_target, backend):
    return OptimizationResult(status,message,*([None]*35),carbon_target,None,None,build,solve,total,backend)


def optimize_lp(load_kwh, pv_capacity_factor, import_price_eur_per_mwh, export_price_eur_per_mwh,
                *, grid_emission_factor_kg_co2_per_mwh, assumptions, carbon_target=None, timestamps=None):
    started=perf_counter()
    load,cf,buy,sell=validate_optimization_inputs(load_kwh,pv_capacity_factor,import_price_eur_per_mwh,export_price_eur_per_mwh,grid_emission_factor_kg_co2_per_mwh,carbon_target)
    build_start=perf_counter()
    c,Aub,bub,Aeq,beq,bounds,idx,meta=_build_lp(load,cf,buy,sell,grid_emission_factor_kg_co2_per_mwh,assumptions,carbon_target)
    build_seconds=perf_counter()-build_start
    method="highs-ipm" if carbon_target is not None and carbon_target>0 else "highs-ds"
    solve_start=perf_counter()
    solved=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=bounds,method=method)
    solve_seconds=perf_counter()-solve_start
    total_seconds=perf_counter()-started
    status_map={0:"optimal",2:"infeasible",3:"unbounded"}
    status=status_map.get(solved.status,"solver_error")
    backend=f"scipy.linprog/{method}"
    if status!="optimal":
        none_fields=dict(
            objective_annualized_cost_eur=None,pv_capacity_kw=None,battery_energy_capacity_kwh=None,battery_power_capacity_kw=None,
            load_mwh=None,pv_generation_mwh=None,pv_self_consumption_mwh=None,pv_export_mwh=None,battery_charge_mwh=None,battery_discharge_mwh=None,battery_losses_mwh=None,grid_import_mwh=None,grid_export_mwh=None,self_consumption_ratio=None,self_sufficiency_ratio=None,annualized_pv_cost_eur=None,annualized_battery_cost_eur=None,annual_pv_opex_eur=None,annual_battery_opex_eur=None,grid_purchase_cost_eur=None,export_revenue_eur=None,baseline_annual_cost_eur=meta['baseline_grid_cost'],annual_saving_vs_baseline_eur=None,initial_capex_eur=None,project_npv_eur=None,simple_payback_years=None,baseline_emissions_tco2=meta['baseline_emissions'],scenario_emissions_tco2=None,emissions_reduction_tco2=None,emissions_reduction_fraction=None,abatement_cost_eur_per_tco2=None,
        )
        return None, OptimizationResult(status=status,solver_message=str(solved.message),carbon_target=carbon_target,carbon_constraint_binding=None,carbon_constraint_slack_tco2=None,model_build_seconds=build_seconds,solve_seconds=solve_seconds,total_seconds=total_seconds,solver_backend=backend,**none_fields)

    x=np.maximum(np.asarray(solved.x,float),0.0)
    pv_capacity=float(x[idx.pv_capacity]); be=float(x[idx.battery_energy]); bp=float(x[idx.battery_power])
    ptl=x[idx.pv_to_load]; ptb=x[idx.pv_to_battery]; bd=x[idx.battery_discharge]; soc=x[idx.soc]
    pvg=cf*pv_capacity
    gi=np.maximum(load-ptl-bd,0.0); pe=np.maximum(pvg-ptl-ptb,0.0)
    soc_start=np.empty_like(soc); soc_start[0]=assumptions.battery_initial_soc_fraction*be; soc_start[1:]=soc[:-1]
    losses=ptb*(1-assumptions.battery_charge_efficiency)+bd*(1/assumptions.battery_discharge_efficiency-1)
    if timestamps is None: timestamp_values=pd.RangeIndex(len(load))
    else: timestamp_values=pd.Series(timestamps).reset_index(drop=True)
    dispatch=pd.DataFrame({"timestamp_utc":timestamp_values,"load_kwh":load,"pv_generation_kwh":pvg,"pv_to_load_kwh":ptl,"pv_to_battery_kwh":ptb,"pv_export_kwh":pe,"battery_charge_kwh":ptb,"battery_discharge_kwh":bd,"battery_losses_kwh":losses,"soc_start_kwh":soc_start,"soc_kwh":soc,"grid_import_kwh":gi,"grid_export_kwh":pe})
    load_mwh=float(load.sum()/1000); pvg_mwh=float(pvg.sum()/1000); pe_mwh=float(pe.sum()/1000); self_mwh=pvg_mwh-pe_mwh; gi_mwh=float(gi.sum()/1000)
    scr=0 if pvg_mwh<=NUMERICAL_TOLERANCE else self_mwh/pvg_mwh
    ssr=0 if load_mwh<=NUMERICAL_TOLERANCE else (load_mwh-gi_mwh)/load_mwh
    annual_pv_opex=pv_capacity*assumptions.pv_opex_eur_per_kw_year
    annual_bat_opex=be*assumptions.battery_opex_eur_per_kwh_year+bp*assumptions.battery_opex_eur_per_kw_year
    annual_pv=pv_capacity*(assumptions.pv_capex_eur_per_kw*meta['pv_crf']+assumptions.pv_opex_eur_per_kw_year)
    annual_bat=be*(assumptions.battery_energy_capex_eur_per_kwh*meta['battery_crf']+assumptions.battery_opex_eur_per_kwh_year)+bp*(assumptions.battery_power_capex_eur_per_kw*meta['battery_crf']+assumptions.battery_opex_eur_per_kw_year)
    purchase=float(np.sum(gi/1000*buy)); revenue=float(np.sum(pe/1000*sell)); total=annual_pv+annual_bat+purchase-revenue
    capex=pv_capacity*assumptions.pv_capex_eur_per_kw+be*assumptions.battery_energy_capex_eur_per_kwh+bp*assumptions.battery_power_capex_eur_per_kw
    cash=meta['baseline_grid_cost']-(purchase-revenue)-annual_pv_opex-annual_bat_opex
    pnpv=npv(capex,[cash]*assumptions.project_life_years,assumptions.wacc); payback=simple_payback_years(capex,cash)
    scen=float(gi.sum()*grid_emission_factor_kg_co2_per_mwh/1_000_000); reduction=meta['baseline_emissions']-scen; redfrac=0 if meta['baseline_emissions']<=NUMERICAL_TOLERANCE else reduction/meta['baseline_emissions']; abat=abatement_cost_eur_per_tco2(total-meta['baseline_grid_cost'],reduction)
    if carbon_target is not None and carbon_target>0:
        allowed=(1-carbon_target)*meta['baseline_emissions']; slack=allowed-scen; bind=abs(slack)<=max(1e-6,meta['baseline_emissions']*1e-7)
    else: slack=None; bind=False
    result=OptimizationResult(status='optimal',solver_message=str(solved.message),objective_annualized_cost_eur=float(total),pv_capacity_kw=pv_capacity,battery_energy_capacity_kwh=be,battery_power_capacity_kw=bp,load_mwh=load_mwh,pv_generation_mwh=pvg_mwh,pv_self_consumption_mwh=float(self_mwh),pv_export_mwh=pe_mwh,battery_charge_mwh=float(ptb.sum()/1000),battery_discharge_mwh=float(bd.sum()/1000),battery_losses_mwh=float(losses.sum()/1000),grid_import_mwh=gi_mwh,grid_export_mwh=pe_mwh,self_consumption_ratio=float(scr),self_sufficiency_ratio=float(ssr),annualized_pv_cost_eur=float(annual_pv),annualized_battery_cost_eur=float(annual_bat),annual_pv_opex_eur=float(annual_pv_opex),annual_battery_opex_eur=float(annual_bat_opex),grid_purchase_cost_eur=purchase,export_revenue_eur=revenue,baseline_annual_cost_eur=meta['baseline_grid_cost'],annual_saving_vs_baseline_eur=float(meta['baseline_grid_cost']-total),initial_capex_eur=float(capex),project_npv_eur=float(pnpv),simple_payback_years=payback,baseline_emissions_tco2=meta['baseline_emissions'],scenario_emissions_tco2=scen,emissions_reduction_tco2=float(reduction),emissions_reduction_fraction=float(redfrac),abatement_cost_eur_per_tco2=abat,carbon_target=carbon_target,carbon_constraint_binding=bind,carbon_constraint_slack_tco2=slack,model_build_seconds=build_seconds,solve_seconds=solve_seconds,total_seconds=total_seconds,solver_backend=backend)
    return dispatch,result
