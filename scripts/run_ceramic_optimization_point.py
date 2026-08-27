"""Solve one isolated carbon target for the Castellón ceramic case."""
from __future__ import annotations
import argparse, json
from industrial_energy_lab.case_studies.bundles import CERAMIC_CASE_ID, load_case_bundle
from industrial_energy_lab.core.baseline import run_baseline
from industrial_energy_lab.optimization.config import optimization_assumptions_from_mapping
from industrial_energy_lab.optimization.sizing import optimize_annual_system
from industrial_energy_lab.schemas.models import GridAssumptions

ap=argparse.ArgumentParser(); ap.add_argument('target', type=float); args=ap.parse_args()
b=load_case_bundle(CERAMIC_CASE_ID); cfg=b.config; grid=GridAssumptions(cfg['grid_emissions_factor_kg_co2_per_mwh'])
base=run_baseline(b.load,b.prices,grid)
d,r=optimize_annual_system(b.load,b.pv,b.prices,grid,optimization_assumptions_from_mapping(cfg),export_price_eur_per_mwh=cfg['export_price_eur_per_mwh'],carbon_target=args.target)
fields=('status','solver_backend','objective_annualized_cost_eur','pv_capacity_kw','battery_energy_capacity_kwh','battery_power_capacity_kw','load_mwh','pv_generation_mwh','pv_self_consumption_mwh','pv_export_mwh','battery_charge_mwh','battery_discharge_mwh','battery_losses_mwh','grid_import_mwh','grid_export_mwh','self_consumption_ratio','self_sufficiency_ratio','annualized_pv_cost_eur','annualized_battery_cost_eur','annual_pv_opex_eur','annual_battery_opex_eur','grid_purchase_cost_eur','export_revenue_eur','baseline_annual_cost_eur','annual_saving_vs_baseline_eur','initial_capex_eur','project_npv_eur','simple_payback_years','baseline_emissions_tco2','scenario_emissions_tco2','emissions_reduction_tco2','emissions_reduction_fraction','abatement_cost_eur_per_tco2','carbon_target','carbon_constraint_binding','carbon_constraint_slack_tco2','model_build_seconds','solve_seconds','total_seconds')
p={'target':args.target,'baseline':{'annual_load_mwh':base.annual_consumption_mwh,'energy_component_cost_eur':base.annual_energy_cost_eur,'grid_emissions_tco2':base.annual_emissions_tco2},'result':{f:getattr(r,f) for f in fields},'dispatch':{'rows':len(d) if d is not None else None,'initial_soc_kwh':float(d['soc_start_kwh'].iloc[0]) if d is not None else None,'final_soc_kwh':float(d['soc_kwh'].iloc[-1]) if d is not None else None}}
print(json.dumps(p))
