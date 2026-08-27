"""Rule-based explanations derived only from computed optimization results."""
from __future__ import annotations
from industrial_energy_lab.optimization.model import OptimizationResult

def explain_optimization_result(result:OptimizationResult,*,economic_optimum:OptimizationResult|None=None,tolerance:float=1e-6)->list[str]:
    if result.status!='optimal':
        if result.status=='infeasible':return ['The scenario is infeasible: the requested constraints cannot be satisfied within the configured capacity bounds.']
        return [f'No physical-economic interpretation is generated because solver status is {result.status}.']
    out=[]
    if result.battery_energy_capacity_kwh is not None and result.battery_energy_capacity_kwh<=tolerance:out.append('The optimal battery energy capacity is zero under the current cost, load, PV and operating assumptions.')
    elif result.battery_energy_capacity_kwh is not None:out.append(f'The optimizer selects {result.battery_energy_capacity_kwh/1000:.2f} MWh of battery energy capacity because storage is part of the minimum-cost feasible solution under the current assumptions.')
    if result.carbon_target is not None and result.carbon_target>0:
        if result.carbon_constraint_binding:out.append(f'The {result.carbon_target:.0%} carbon constraint is binding: optimized emissions are at the allowed limit within numerical tolerance.')
        else:out.append(f'The {result.carbon_target:.0%} carbon constraint is not binding: the optimized system reduces emissions beyond the minimum requirement.')
        if economic_optimum is not None and economic_optimum.status=='optimal':
            base=economic_optimum.emissions_reduction_fraction or 0
            if result.carbon_target>base+tolerance:out.append(f'The carbon target is stricter than the unconstrained economic optimum ({base:.1%} reduction), so decarbonization requirements can alter the selected system.')
    if result.pv_generation_mwh and result.pv_generation_mwh>tolerance:
        share=(result.pv_export_mwh or 0)/result.pv_generation_mwh
        if share>0.2:out.append(f'About {share:.0%} of PV generation is exported, indicating that additional PV increasingly serves the lower-valued export channel rather than onsite demand.')
    if result.abatement_cost_eur_per_tco2 is not None:
        out.append('The abatement cost is negative: this solution reduces modeled CO2 emissions while also lowering annualized cost relative to the baseline.' if result.abatement_cost_eur_per_tco2<0 else 'The abatement cost is positive: the modeled emissions reduction requires additional annualized cost relative to the baseline.')
    return out

def explain_scenario_change(previous:OptimizationResult,current:OptimizationResult,*,tolerance:float=1e-6)->list[str]:
    if previous.status!='optimal' or current.status!='optimal':return ['Scenario-to-scenario comparison requires two optimal solutions.']
    out=[];pt=previous.carbon_target or 0;ct=current.carbon_target or 0
    if ct>pt+tolerance:out.append(f'The carbon requirement increases from {pt:.0%} to {ct:.0%}, reducing the feasible solution space.')
    for label,old,new,unit in (("PV capacity",previous.pv_capacity_kw,current.pv_capacity_kw,"kW"),("battery energy capacity",previous.battery_energy_capacity_kwh,current.battery_energy_capacity_kwh,"kWh"),("battery power capacity",previous.battery_power_capacity_kw,current.battery_power_capacity_kw,"kW")):
        if old is None or new is None:continue
        delta=new-old;scale=max(1,abs(old),abs(new))
        if abs(delta)<=max(tolerance,scale*1e-7):continue
        out.append(f'{label} {"increases" if delta>0 else "decreases"} from {old:,.1f} to {new:,.1f} {unit} between the two solved scenarios.')
    if previous.objective_annualized_cost_eur is not None and current.objective_annualized_cost_eur is not None:
        d=current.objective_annualized_cost_eur-previous.objective_annualized_cost_eur
        if d>tolerance:out.append(f'Total annualized cost rises by €{d:,.0f}/year between the two scenarios.')
        elif d<-tolerance:out.append(f'Total annualized cost falls by €{-d:,.0f}/year between the two scenarios.')
    if previous.scenario_emissions_tco2 is not None and current.scenario_emissions_tco2 is not None and current.scenario_emissions_tco2<previous.scenario_emissions_tco2-tolerance:
        out.append(f'Modeled grid-related emissions fall by {previous.scenario_emissions_tco2-current.scenario_emissions_tco2:,.1f} tCO2/year between the two scenarios.')
    return out


def explain_sensitivity_results(frame, variable: str, *, tolerance: float = 1e-6) -> list[str]:
    """Describe only trends demonstrated by solved sensitivity rows."""
    optimal = frame[frame["status"] == "optimal"].sort_values("input_value").copy()
    if len(optimal) < 2:
        return ["At least two optimal sensitivity points are required for a trend explanation."]
    first, last = optimal.iloc[0], optimal.iloc[-1]
    out: list[str] = []
    for label, column, scale, unit in (
        ("Optimal PV capacity", "pv_capacity_kw", 1000.0, "MW"),
        ("Optimal battery energy", "battery_energy_capacity_kwh", 1000.0, "MWh"),
        ("Annualized cost", "annualized_cost_eur", 1_000_000.0, "M€/year"),
    ):
        old = first[column]
        new = last[column]
        if old is None or new is None:
            continue
        old = float(old); new = float(new); delta = new - old
        if abs(delta) <= max(tolerance, max(abs(old), abs(new), 1.0) * 1e-7):
            continue
        out.append(
            f"{label} {'increases' if delta > 0 else 'decreases'} from "
            f"{old / scale:,.2f} to {new / scale:,.2f} {unit} across the solved range."
        )
    if variable == "battery_capex_multiplier":
        vals = optimal["input_value"].to_numpy(float)
        caps = optimal["battery_energy_capacity_kwh"].fillna(0.0).to_numpy(float)
        for i in range(1, len(vals)):
            if caps[i - 1] > tolerance and caps[i] <= tolerance:
                out.append(
                    f"Storage changes from positive capacity to zero between the tested "
                    f"battery-CAPEX multipliers {vals[i-1]:.2f}× and {vals[i]:.2f}×. "
                    "This is an observed bracket, not a more precise break-even claim."
                )
                break
    return out
