"""Worked, traceable calculations for the educational UI.

These helpers explain calculations already performed by the engineering model. They
never change optimization results and deliberately return structured data so the UI
can show a short explanation, formula, numerical substitution and unit check.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from industrial_energy_lab.economics.cashflows import capital_recovery_factor
from industrial_energy_lab.optimization.model import OptimizationResult


@dataclass(frozen=True)
class WorkedCalculation:
    metric_id: str
    label: str
    formula: str
    inputs: tuple[tuple[str, float, str], ...]
    substitution: str
    result_value: float
    result_unit: str
    interpretation: str
    unit_check: str = ""


def _require(result: OptimizationResult, *names: str) -> list[float]:
    values: list[float] = []
    for name in names:
        value = getattr(result, name)
        if value is None or not isfinite(float(value)):
            raise ValueError(f"{name} is required for this worked calculation.")
        values.append(float(value))
    return values


def explain_calculation(
    metric_id: str,
    result: OptimizationResult,
    parameters: Mapping[str, object],
) -> WorkedCalculation:
    """Build a worked calculation from one solved optimization result."""
    if result.status != "optimal":
        raise ValueError("Worked calculations require an optimal result.")

    ef = float(parameters["grid_emissions_factor_kg_co2_per_mwh"])

    if metric_id == "self_consumption":
        pv, used = _require(result, "pv_generation_mwh", "pv_self_consumption_mwh")
        value = 0.0 if pv == 0 else used / pv
        return WorkedCalculation(
            metric_id, "PV self-consumption ratio", "PV used onsite / PV generation",
            (("PV used onsite", used, "MWh"), ("PV generation", pv, "MWh")),
            f"{used:,.2f} MWh / {pv:,.2f} MWh = {value:.1%}", value, "%",
            "This answers: what share of the PV electricity stays onsite?",
            "MWh / MWh → dimensionless ratio",
        )

    if metric_id == "self_sufficiency":
        load, grid = _require(result, "load_mwh", "grid_import_mwh")
        value = 0.0 if load == 0 else (load - grid) / load
        return WorkedCalculation(
            metric_id, "Electrical self-sufficiency", "(Load - grid import) / Load",
            (("Annual load", load, "MWh"), ("Grid import", grid, "MWh")),
            f"({load:,.2f} - {grid:,.2f}) MWh / {load:,.2f} MWh = {value:.1%}", value, "%",
            "This answers: what share of site demand is supplied without importing electricity from the grid?",
            "MWh / MWh → dimensionless ratio",
        )

    if metric_id == "baseline_emissions":
        load, emissions = _require(result, "load_mwh", "baseline_emissions_tco2")
        return WorkedCalculation(
            metric_id, "Baseline grid emissions", "Grid electricity × grid emission factor / 1,000",
            (("Baseline grid electricity", load, "MWh"), ("Grid emission factor", ef, "kgCO₂/MWh")),
            f"{load:,.2f} MWh × {ef:,.2f} kgCO₂/MWh / 1,000 = {emissions:,.2f} tCO₂",
            emissions, "tCO₂/year",
            "The baseline is grid-only, so annual load is also baseline grid import.",
            "MWh × kgCO₂/MWh = kgCO₂; /1,000 = tCO₂",
        )

    if metric_id == "scenario_emissions":
        grid, emissions = _require(result, "grid_import_mwh", "scenario_emissions_tco2")
        return WorkedCalculation(
            metric_id, "Scenario grid emissions", "Grid import × grid emission factor / 1,000",
            (("Grid import", grid, "MWh"), ("Grid emission factor", ef, "kgCO₂/MWh")),
            f"{grid:,.2f} MWh × {ef:,.2f} kgCO₂/MWh / 1,000 = {emissions:,.2f} tCO₂",
            emissions, "tCO₂/year",
            "IEL gives no CO₂ credit for exported electricity in v1.1.",
            "MWh × kgCO₂/MWh = kgCO₂; /1,000 = tCO₂",
        )

    if metric_id == "co2_reduction":
        baseline, scenario, reduction = _require(
            result, "baseline_emissions_tco2", "scenario_emissions_tco2", "emissions_reduction_tco2"
        )
        return WorkedCalculation(
            metric_id, "Absolute CO₂ reduction", "Baseline emissions - scenario emissions",
            (("Baseline emissions", baseline, "tCO₂"), ("Scenario emissions", scenario, "tCO₂")),
            f"{baseline:,.2f} - {scenario:,.2f} = {reduction:,.2f} tCO₂/year",
            reduction, "tCO₂/year", "Positive values mean fewer modeled grid-related emissions than baseline.",
            "tCO₂ - tCO₂ = tCO₂",
        )

    if metric_id == "co2_reduction_fraction":
        baseline, reduction, fraction = _require(
            result, "baseline_emissions_tco2", "emissions_reduction_tco2", "emissions_reduction_fraction"
        )
        return WorkedCalculation(
            metric_id, "Percentage CO₂ reduction", "CO₂ reduction / baseline emissions",
            (("CO₂ reduction", reduction, "tCO₂"), ("Baseline emissions", baseline, "tCO₂")),
            f"{reduction:,.2f} / {baseline:,.2f} = {fraction:.1%}", fraction, "%",
            "This percentage is relative to the defined electrical baseline, not total ceramic-process emissions.",
            "tCO₂ / tCO₂ → dimensionless ratio",
        )

    if metric_id == "abatement_cost":
        total, baseline_cost, reduction, value = _require(
            result, "objective_annualized_cost_eur", "baseline_annual_cost_eur",
            "emissions_reduction_tco2", "abatement_cost_eur_per_tco2",
        )
        delta = total - baseline_cost
        return WorkedCalculation(
            metric_id, "Abatement cost", "(Scenario annualized cost - baseline annual cost) / CO₂ reduction",
            (("Cost difference", delta, "€/year"), ("CO₂ reduction", reduction, "tCO₂/year")),
            f"({total:,.0f} - {baseline_cost:,.0f}) €/year / {reduction:,.2f} tCO₂/year = {value:,.2f} €/tCO₂",
            value, "€/tCO₂",
            "Negative means the modeled emissions reduction also saves annualized cost; positive means deeper reduction has a net annualized cost.",
            "€/year ÷ tCO₂/year = €/tCO₂",
        )

    if metric_id == "initial_capex":
        pv_kw, be_kwh, bp_kw, capex = _require(
            result, "pv_capacity_kw", "battery_energy_capacity_kwh", "battery_power_capacity_kw", "initial_capex_eur"
        )
        pv_rate = float(parameters["pv_capex_eur_per_kw"])
        be_rate = float(parameters["battery_energy_capex_eur_per_kwh"])
        bp_rate = float(parameters["battery_power_capex_eur_per_kw"])
        return WorkedCalculation(
            metric_id, "Initial CAPEX", "PV kW×€/kW + battery kWh×€/kWh + battery kW×€/kW",
            (("PV capacity", pv_kw, "kW"), ("Battery energy", be_kwh, "kWh"), ("Battery power", bp_kw, "kW")),
            f"{pv_kw:,.1f}×{pv_rate:,.0f} + {be_kwh:,.1f}×{be_rate:,.0f} + {bp_kw:,.1f}×{bp_rate:,.0f} = €{capex:,.0f}",
            capex, "€", "This is upfront investment, not annual cost.", "capacity × unit CAPEX = €",
        )

    if metric_id == "crf":
        r = float(parameters["wacc"])
        n = int(parameters["pv_lifetime_years"])
        crf = capital_recovery_factor(r, n)
        return WorkedCalculation(
            metric_id, "PV capital recovery factor", "r(1+r)^n / ((1+r)^n - 1)",
            (("WACC (r)", r, "fraction/year"), ("PV lifetime (n)", float(n), "years")),
            f"{r:.2%}×(1+{r:.2%})^{n} / ((1+{r:.2%})^{n}-1) = {crf:.4f}", crf, "1/year",
            "Multiplying upfront PV CAPEX by this factor gives its equivalent annual capital cost.",
            "dimensionless/year",
        )

    if metric_id == "annualized_capex":
        pv_total, bat_total, pv_opex, bat_opex = _require(
            result, "annualized_pv_cost_eur", "annualized_battery_cost_eur",
            "annual_pv_opex_eur", "annual_battery_opex_eur",
        )
        cap_component = pv_total + bat_total - pv_opex - bat_opex
        return WorkedCalculation(
            metric_id, "Annualized CAPEX", "Annualized technology cost - recurring OPEX",
            (("PV annualized total", pv_total, "€/year"), ("Battery annualized total", bat_total, "€/year"),
             ("PV OPEX", pv_opex, "€/year"), ("Battery OPEX", bat_opex, "€/year")),
            f"{pv_total:,.0f} + {bat_total:,.0f} - {pv_opex:,.0f} - {bat_opex:,.0f} = €{cap_component:,.0f}/year",
            cap_component, "€/year", "This is an equivalent yearly representation of investment, not a second CAPEX payment.",
            "€/year",
        )

    if metric_id == "annual_saving":
        baseline, total, saving = _require(
            result, "baseline_annual_cost_eur", "objective_annualized_cost_eur", "annual_saving_vs_baseline_eur"
        )
        return WorkedCalculation(
            metric_id, "Annual equivalent improvement", "Baseline annual cost - optimized annualized cost",
            (("Baseline cost", baseline, "€/year"), ("Optimized annualized cost", total, "€/year")),
            f"€{baseline:,.0f}/year - €{total:,.0f}/year = €{saving:,.0f}/year", saving, "€/year",
            "This is an annual-equivalent comparison used for screening; it is not identical to accounting profit or cash flow.",
            "€/year - €/year = €/year",
        )

    if metric_id in {"payback", "npv"}:
        capex, purchase, revenue, pv_opex, bat_opex, baseline = _require(
            result, "initial_capex_eur", "grid_purchase_cost_eur", "export_revenue_eur",
            "annual_pv_opex_eur", "annual_battery_opex_eur", "baseline_annual_cost_eur",
        )
        cash = baseline - (purchase - revenue) - pv_opex - bat_opex
        if metric_id == "payback":
            payback, = _require(result, "simple_payback_years")
            return WorkedCalculation(
                metric_id, "Simple payback", "Initial CAPEX / annual operating cash benefit",
                (("Initial CAPEX", capex, "€"), ("Annual operating cash benefit", cash, "€/year")),
                f"€{capex:,.0f} / €{cash:,.0f}/year = {payback:.2f} years", payback, "years",
                "Simple payback ignores the time value of money, so it answers a different question from NPV.",
                "€ ÷ €/year = years",
            )
        pnpv, = _require(result, "project_npv_eur")
        r = float(parameters["wacc"]); years = int(parameters["project_life_years"])
        pv_cash = sum(cash / (1 + r) ** t for t in range(1, years + 1))
        return WorkedCalculation(
            metric_id, "Net Present Value", "-CAPEX + Σ annual cash flow / (1+r)^t",
            (("Initial CAPEX", capex, "€"), ("Annual operating cash benefit", cash, "€/year"),
             ("WACC", r, "fraction/year"), ("Project life", float(years), "years")),
            f"-€{capex:,.0f} + PV({years} annual cash flows of €{cash:,.0f} at {r:.1%}) = €{pnpv:,.0f}",
            pnpv, "€",
            f"The discounted value of the modeled annual cash benefits is €{pv_cash:,.0f}; positive NPV is supportive evidence, not an automatic build decision.",
            "discounted € - € = €",
        )

    raise KeyError(f"No worked calculation is defined for metric_id={metric_id!r}.")


WORKED_METRIC_IDS = (
    "self_consumption", "self_sufficiency", "baseline_emissions", "scenario_emissions",
    "co2_reduction", "co2_reduction_fraction", "abatement_cost", "initial_capex",
    "crf", "annualized_capex", "annual_saving", "payback", "npv",
)
