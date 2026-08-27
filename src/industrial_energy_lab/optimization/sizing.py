"""High-level annual optimization orchestration for validated hourly datasets."""
from __future__ import annotations
import pandas as pd
from industrial_energy_lab.optimization.model import OptimizationAssumptions, OptimizationResult, optimize_lp
from industrial_energy_lab.schemas.models import GridAssumptions
from industrial_energy_lab.validation.datasets import validate_hourly_dataframe

def optimize_annual_system(load_frame: pd.DataFrame,pv_profile_frame: pd.DataFrame,price_frame: pd.DataFrame,grid_assumptions: GridAssumptions,assumptions: OptimizationAssumptions,*,export_price_eur_per_mwh: float | pd.Series=0.0,carbon_target: float | None=None)->tuple[pd.DataFrame|None,OptimizationResult]:
    load=validate_hourly_dataframe(load_frame,value_column='load_kw')
    pv=validate_hourly_dataframe(pv_profile_frame,value_column='capacity_factor',min_value=0,max_value=1)
    prices=validate_hourly_dataframe(price_frame,value_column='price_eur_per_mwh',allow_negative=True)
    if not load['timestamp_utc'].equals(pv['timestamp_utc']): raise ValueError('Load and PV timestamps must match exactly.')
    if not load['timestamp_utc'].equals(prices['timestamp_utc']): raise ValueError('Load and price timestamps must match exactly.')
    return optimize_lp(load['load_kw'],pv['capacity_factor'],prices['price_eur_per_mwh'],export_price_eur_per_mwh,grid_emission_factor_kg_co2_per_mwh=grid_assumptions.emissions_factor_kg_co2_per_mwh,assumptions=assumptions,carbon_target=carbon_target,timestamps=load['timestamp_utc'])
