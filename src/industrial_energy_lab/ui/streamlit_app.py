"""Professional Streamlit interface for the validated screening engine.

The module deliberately imports Streamlit only inside ``main`` so the engine and
UI service tests remain importable in environments where the optional app
extras are not installed.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from industrial_energy_lab.explainability.insights import (
    explain_optimization_result,
    explain_scenario_change,
    explain_sensitivity_results,
)
from industrial_energy_lab.explainability.metrics import get_metric
from industrial_energy_lab.optimization.sensitivity import SENSITIVITY_FAMILIES
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui.charts import (
    economics_breakdown,
    frontier_capacities,
    frontier_cost,
    hourly_energy,
    load_duration_curve,
    monthly_consumption,
    sensitivity_chart,
    sensitivity_cost_chart,
    soc_chart,
)
from industrial_energy_lab.ui.formatting import (
    format_energy_kwh,
    format_energy_mwh,
    format_eur,
    format_eur_per_year,
    format_percent,
    format_power_kw,
    format_tco2,
    format_years,
    metric_help,
)
from industrial_energy_lab.ui.services import (
    ROOT,
    default_parameters,
    load_demo_bundle,
    run_baseline_request,
    run_frontier_request,
    run_optimization_request,
    run_sensitivity_request,
    validate_custom_load,
)
from industrial_energy_lab.utils.version import (
    DATASET_VERSION,
    OPTIMIZATION_CASE_VERSION,
    OPTIMIZATION_MODEL_VERSION,
)

SECTIONS = (
    "Overview",
    "Inputs",
    "Baseline",
    "Optimized system",
    "Hourly results",
    "Economics",
    "Decarbonization",
    "Sensitivity",
    "Methodology",
)

SENSITIVITY_LABELS = {
    "electricity_price_multiplier": "Electricity price multiplier",
    "pv_capex_multiplier": "PV CAPEX multiplier",
    "battery_capex_multiplier": "Battery CAPEX multiplier",
    "grid_emission_factor_multiplier": "Grid emission factor multiplier",
    "wacc": "WACC",
    "carbon_target": "Carbon target",
}


def _state_defaults(st) -> None:
    defaults = {
        "params": default_parameters(),
        "custom_load": None,
        "last_result": None,
        "last_dispatch": None,
        "economic_result": None,
        "economic_dispatch": None,
        "frontier": None,
        "sensitivity_results": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _invalidate_results(st) -> None:
    for key, value in (
        ("last_result", None), ("last_dispatch", None),
        ("economic_result", None), ("economic_dispatch", None),
        ("frontier", None), ("sensitivity_results", {}),
    ):
        st.session_state[key] = value


def _load_frame(st) -> pd.DataFrame | None:
    return st.session_state.get("custom_load")


def _result_error(st, result) -> None:
    if result.status == "infeasible":
        st.error(
            "**Infeasible scenario.** No combination of PV and battery within the "
            "current model bounds can satisfy the selected constraints."
        )
    elif result.status == "unbounded":
        st.error("**Unbounded optimization.** Review economic inputs and model bounds.")
    else:
        st.error("**Solver error.** The optimization did not return an interpretable solution.")
    with st.expander("Technical details"):
        st.code(result.solver_message)


def _metric(st, metric_id: str, value: str, *, delta: str | None = None) -> None:
    m = get_metric(metric_id)
    st.metric(m.label, value, delta=delta, help=metric_help(metric_id), border=True)


def _run_current_optimization(st, *, target: float | None = None) -> None:
    params = st.session_state.params
    requested_target = float(params.get("carbon_target", 0.0) if target is None else target)
    with st.spinner("Optimizing 8,760 hourly periods…"):
        if requested_target > 0 and st.session_state.economic_result is None:
            e_dispatch, economic = run_optimization_request(params, _load_frame(st), carbon_target=0.0)
            st.session_state.economic_dispatch = e_dispatch
            st.session_state.economic_result = economic
        dispatch, result = run_optimization_request(params, _load_frame(st), carbon_target=requested_target)
    st.session_state.last_dispatch = dispatch
    st.session_state.last_result = result
    if requested_target <= 0:
        st.session_state.economic_dispatch = dispatch
        st.session_state.economic_result = result
    st.session_state.frontier = None
    st.session_state.sensitivity_results = {}


def _render_header(st, section: str) -> None:
    st.title("Industrial Energy Lab")
    st.caption("Industrial Decarbonization & Techno-Economic Screening")
    st.info(
        "**Synthetic industrial demo.** Current profiles and economic assumptions are "
        "software-validation inputs. They do not represent any individual facility or a "
        "documented Castellón ceramic plant."
    )
    if section != "Overview":
        st.caption(f"Section: {section}")


def _overview(st) -> None:
    st.header("What question does this tool answer?")
    st.markdown(
        "> Given an industrial hourly electricity demand profile, what combination of PV "
        "and battery storage minimizes annualized energy cost, and how does that solution "
        "change under explicit CO₂-reduction targets?"
    )
    st.markdown(
        "Industrial Energy Lab is a **pre-feasibility screening tool**, not detailed "
        "engineering, FEED, financial advice, a control system, or a certified energy model."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("8,760 h")
        st.write("Every annual optimization uses the complete validated hourly timeline.")
    with c2:
        st.subheader("LP optimization")
        st.write("PV, battery energy/power and hourly dispatch are solved jointly with HiGHS.")
    with c3:
        st.subheader("Explainable")
        st.write("Important inputs and results include contextual help from one central registry.")
    st.subheader("System boundary")
    st.code("""PV ──┬──> Industrial load\n     ├──> Battery ──> Industrial load\n     └──> Grid export\nGrid ───────────────> Industrial load""")
    st.subheader("How to use it")
    st.markdown(
        "1. Review or change **Inputs**.\n"
        "2. Run the 8,760-hour optimization.\n"
        "3. Inspect the **Optimized system**, hourly behavior and economics.\n"
        "4. Explore a CO₂ frontier or one **Sensitivity** family on demand.\n"
        "5. Use each help icon to understand definitions, units and relationships."
    )


def _input_number(st, label: str, metric_id: str, value: float, *, min_value: float, step: float, key: str, format: str | None = None):
    kwargs = dict(label=label, value=float(value), min_value=float(min_value), step=float(step), key=key, help=metric_help(metric_id))
    if format is not None:
        kwargs["format"] = format
    return st.number_input(**kwargs)


def _inputs(st) -> None:
    st.header("Model inputs")
    st.write("Defaults are **synthetic assumptions for model validation**. Change values, then submit once; sliders do not trigger optimization automatically.")
    p = dict(st.session_state.params)
    with st.form("optimization_inputs", border=True):
        st.subheader("Electricity")
        c1, c2 = st.columns(2)
        with c1:
            p["import_price_multiplier"] = _input_number(st, "Import price multiplier", "import_price_multiplier", p["import_price_multiplier"], min_value=0.01, step=0.05, key="in_price_mult")
        with c2:
            p["export_price_eur_per_mwh"] = _input_number(st, "Export price", "export_price", p["export_price_eur_per_mwh"], min_value=0.0, step=1.0, key="in_export_price")

        st.subheader("PV")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p["pv_capex_eur_per_kw"] = _input_number(st, "PV CAPEX", "pv_capex_rate", p["pv_capex_eur_per_kw"], min_value=0.0, step=25.0, key="in_pv_capex")
        with c2:
            p["pv_opex_eur_per_kw_year"] = _input_number(st, "PV OPEX", "pv_opex_rate", p["pv_opex_eur_per_kw_year"], min_value=0.0, step=1.0, key="in_pv_opex")
        with c3:
            p["pv_lifetime_years"] = int(_input_number(st, "PV lifetime", "pv_lifetime", p["pv_lifetime_years"], min_value=1.0, step=1.0, key="in_pv_life"))
        with c4:
            p["max_pv_capacity_kw"] = _input_number(st, "Maximum PV capacity", "max_pv_capacity", p["max_pv_capacity_kw"], min_value=0.0, step=500.0, key="in_pv_max")

        st.subheader("Battery")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p["battery_energy_capex_eur_per_kwh"] = _input_number(st, "Energy CAPEX", "battery_energy_capex_rate", p["battery_energy_capex_eur_per_kwh"], min_value=0.0, step=10.0, key="in_be_capex")
        with c2:
            p["battery_power_capex_eur_per_kw"] = _input_number(st, "Power CAPEX", "battery_power_capex_rate", p["battery_power_capex_eur_per_kw"], min_value=0.0, step=10.0, key="in_bp_capex")
        with c3:
            p["max_battery_energy_kwh"] = _input_number(st, "Maximum battery energy", "max_battery_energy", p["max_battery_energy_kwh"], min_value=0.0, step=500.0, key="in_be_max")
        with c4:
            p["max_battery_power_kw"] = _input_number(st, "Maximum battery power", "max_battery_power", p["max_battery_power_kw"], min_value=0.0, step=250.0, key="in_bp_max")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p["battery_charge_efficiency"] = _input_number(st, "Charge efficiency", "battery_charge_efficiency", p["battery_charge_efficiency"], min_value=0.01, step=0.01, key="in_eta_c", format="%.2f")
        with c2:
            p["battery_discharge_efficiency"] = _input_number(st, "Discharge efficiency", "battery_discharge_efficiency", p["battery_discharge_efficiency"], min_value=0.01, step=0.01, key="in_eta_d", format="%.2f")
        with c3:
            p["battery_min_soc_fraction"] = _input_number(st, "Minimum SOC", "soc_min_fraction", p["battery_min_soc_fraction"], min_value=0.0, step=0.05, key="in_soc_min", format="%.2f")
        with c4:
            p["battery_max_soc_fraction"] = _input_number(st, "Maximum SOC", "soc_max_fraction", p["battery_max_soc_fraction"], min_value=0.0, step=0.05, key="in_soc_max", format="%.2f")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p["battery_initial_soc_fraction"] = st.number_input("Initial SOC fraction", value=float(p["battery_initial_soc_fraction"]), min_value=0.0, max_value=1.0, step=0.05, key="in_soc_init", help=metric_help("soc"))
        with c2:
            p["battery_opex_eur_per_kwh_year"] = st.number_input("Battery energy OPEX", value=float(p["battery_opex_eur_per_kwh_year"]), min_value=0.0, step=0.5, key="in_be_opex", help=metric_help("opex"))
        with c3:
            p["battery_opex_eur_per_kw_year"] = st.number_input("Battery power OPEX", value=float(p["battery_opex_eur_per_kw_year"]), min_value=0.0, step=0.5, key="in_bp_opex", help=metric_help("opex"))
        with c4:
            p["battery_lifetime_years"] = int(_input_number(st, "Battery lifetime", "battery_lifetime", p["battery_lifetime_years"], min_value=1.0, step=1.0, key="in_bat_life"))

        st.subheader("Finance & carbon")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p["wacc"] = st.number_input("WACC", value=float(p["wacc"]), min_value=0.0, max_value=1.0, step=0.005, format="%.3f", key="in_wacc", help=metric_help("wacc"))
        with c2:
            p["project_life_years"] = int(_input_number(st, "Project life", "project_life", p["project_life_years"], min_value=1.0, step=1.0, key="in_project_life"))
        with c3:
            p["grid_emissions_factor_kg_co2_per_mwh"] = _input_number(st, "Grid emission factor", "grid_emission_factor", p["grid_emissions_factor_kg_co2_per_mwh"], min_value=0.0, step=10.0, key="in_grid_ef")
        with c4:
            p["carbon_target"] = st.number_input("Minimum CO₂ reduction target", value=float(p["carbon_target"]), min_value=0.0, max_value=1.0, step=0.05, format="%.2f", key="in_carbon", help=metric_help("carbon_target"))

        submitted = st.form_submit_button("Run optimization", type="primary", use_container_width=True)

    if submitted:
        try:
            if p["battery_min_soc_fraction"] > p["battery_initial_soc_fraction"] or p["battery_initial_soc_fraction"] > p["battery_max_soc_fraction"]:
                raise ValueError("Initial SOC must lie between minimum and maximum SOC.")
            if p["project_life_years"] > min(p["pv_lifetime_years"], p["battery_lifetime_years"]):
                raise ValueError("Project life cannot exceed the shorter technology lifetime in the current simplified NPV model.")
            st.session_state.params = p
            _invalidate_results(st)
            _run_current_optimization(st)
            st.success("Optimization complete. Open **Optimized system** to inspect the solution.")
        except ValueError as exc:
            st.error(str(exc))

    st.divider()
    st.subheader("Optional industrial load upload")
    st.caption("CSV must contain `timestamp_utc` and `load_kw`, exactly 8,760 hourly rows, and match the current demo UTC timeline so PV and price snapshots remain aligned.")
    uploaded = st.file_uploader("Load-profile CSV", type="csv", help=metric_help("annual_load"))
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Use uploaded load", disabled=uploaded is None):
            try:
                frame = pd.read_csv(uploaded)
                st.session_state.custom_load = validate_custom_load(frame)
                _invalidate_results(st)
                st.success("Uploaded load validated and activated.")
            except Exception as exc:
                st.error(f"Load profile rejected: {exc}")
    with c2:
        if st.button("Restore synthetic demo load"):
            st.session_state.custom_load = None
            _invalidate_results(st)
            st.success("Synthetic demo load restored.")


def _baseline(st) -> None:
    st.header("Baseline")
    result, load, prices = run_baseline_request(st.session_state.params, _load_frame(st))
    cols = st.columns(4)
    with cols[0]: _metric(st, "annual_load", format_energy_mwh(result.annual_consumption_mwh))
    with cols[1]: _metric(st, "baseline_cost", format_eur_per_year(result.annual_energy_cost_eur))
    with cols[2]: _metric(st, "baseline_emissions", format_tco2(result.annual_emissions_tco2))
    with cols[3]: _metric(st, "average_import_price", f"€{prices['price_eur_per_mwh'].mean():.1f}/MWh")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Load-duration curve")
        st.plotly_chart(load_duration_curve(load), use_container_width=True)
    with c2:
        st.subheader("Monthly consumption")
        st.plotly_chart(monthly_consumption(load), use_container_width=True)


def _optimized(st) -> None:
    st.header("Optimized system")
    result = st.session_state.last_result
    if result is None:
        st.write("No optimization has been run with the current inputs.")
        if st.button("Run economic optimum", type="primary"):
            try:
                _run_current_optimization(st, target=0.0)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        return
    if result.status != "optimal":
        _result_error(st, result)
        return
    target = result.carbon_target or 0.0
    st.subheader("Economic optimum" if target <= 0 else f"Optimized system — {target:.0%} minimum CO₂ reduction")
    row1 = st.columns(3)
    with row1[0]: _metric(st, "optimal_pv", format_power_kw(result.pv_capacity_kw))
    with row1[1]: _metric(st, "battery_energy_capacity", format_energy_kwh(result.battery_energy_capacity_kwh))
    with row1[2]: _metric(st, "battery_power_capacity", format_power_kw(result.battery_power_capacity_kw))
    row2 = st.columns(3)
    with row2[0]: _metric(st, "scenario_cost", format_eur_per_year(result.objective_annualized_cost_eur))
    with row2[1]: _metric(st, "annual_saving", format_eur_per_year(result.annual_saving_vs_baseline_eur))
    with row2[2]: _metric(st, "co2_reduction_fraction", format_percent(result.emissions_reduction_fraction))
    if target > 0:
        _metric(
            st,
            "binding_carbon_constraint",
            "BINDING" if result.carbon_constraint_binding else "NOT BINDING",
        )

    st.subheader("Why this solution?")
    insights = explain_optimization_result(result, economic_optimum=st.session_state.economic_result)
    for text in insights:
        st.info(text)
    if target > 0 and st.session_state.economic_result is not None:
        for text in explain_scenario_change(st.session_state.economic_result, result):
            st.write(f"- {text}")

    with st.expander("Advanced details"):
        st.json({
            "solver_status": result.status,
            "solver_backend": result.solver_backend,
            "model_version": OPTIMIZATION_MODEL_VERSION,
            "dataset_version": DATASET_VERSION,
            "case_version": OPTIMIZATION_CASE_VERSION,
            "model_build_seconds": round(result.model_build_seconds, 4),
            "solve_seconds": round(result.solve_seconds, 4),
            "total_seconds": round(result.total_seconds, 4),
        })


def _hourly(st) -> None:
    st.header("Hourly results")
    dispatch = st.session_state.last_dispatch
    result = st.session_state.last_result
    if dispatch is None or result is None or result.status != "optimal":
        st.warning("Run an optimal scenario first.")
        return
    n = len(dispatch)
    max_start = max(0, n - 24)
    start = st.slider("Start hour", min_value=0, max_value=max_start, value=0, step=24, help="Visualization window only; the optimization still uses all 8,760 hours.")
    hours = st.selectbox("Window length", [24, 72, 168, 336, 744], index=2)
    st.plotly_chart(hourly_energy(dispatch, start=start, hours=hours), use_container_width=True)
    st.subheader("Battery state of charge")
    st.caption(metric_help("soc"))
    st.plotly_chart(soc_chart(dispatch, result.battery_energy_capacity_kwh, start=start, hours=hours), use_container_width=True)


def _economics(st) -> None:
    st.header("Economics")
    r = st.session_state.last_result
    if r is None or r.status != "optimal":
        st.warning("Run an optimal scenario first.")
        return
    st.subheader("Initial investment")
    _metric(st, "initial_capex", format_eur(r.initial_capex_eur))
    st.subheader("Annualized economics")
    c1, c2, c3 = st.columns(3)
    with c1: _metric(st, "scenario_cost", format_eur_per_year(r.objective_annualized_cost_eur))
    with c2: _metric(st, "annual_saving", format_eur_per_year(r.annual_saving_vs_baseline_eur))
    with c3: _metric(st, "export_revenue", format_eur_per_year(r.export_revenue_eur))
    c1, c2 = st.columns(2)
    with c1: _metric(st, "npv", format_eur(r.project_npv_eur))
    with c2: _metric(st, "payback", format_years(r.simple_payback_years))
    st.plotly_chart(economics_breakdown(r), use_container_width=True)
    st.caption("NPV and payback are screening indicators under the configured simplified cash-flow assumptions; they are not an investment recommendation.")


def _decarbonization(st) -> None:
    st.header("Decarbonization")
    st.write("The carbon target is a **minimum reduction in modeled grid-related CO₂ versus baseline**. It is not the renewable share or self-sufficiency ratio.")
    if st.button("Run 0–50% cost–decarbonization frontier", type="primary"):
        try:
            with st.spinner("Solving only carbon targets that are stricter than the economic optimum…"):
                if st.session_state.economic_result is None:
                    d, e = run_optimization_request(st.session_state.params, _load_frame(st), carbon_target=0.0)
                    st.session_state.economic_dispatch = d
                    st.session_state.economic_result = e
                st.session_state.frontier = run_frontier_request(
                    st.session_state.params,
                    _load_frame(st),
                    economic_optimum=st.session_state.economic_result,
                )
        except ValueError as exc:
            st.error(str(exc))
    frontier = st.session_state.frontier
    if frontier is None:
        st.info("Run the frontier on demand. Targets already met by the economic optimum are reused without another LP solve.")
        return
    st.plotly_chart(frontier_cost(frontier), use_container_width=True)
    st.plotly_chart(frontier_capacities(frontier), use_container_width=True)
    table = frontier[[
        "carbon_target", "status", "pv_capacity_kw", "battery_energy_capacity_kwh",
        "battery_power_capacity_kw", "annualized_cost_eur", "emissions_reduction_fraction",
        "abatement_cost_eur_per_tco2", "carbon_constraint_binding",
    ]].copy()
    table["carbon_target"] *= 100
    table["emissions_reduction_fraction"] *= 100
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(metric_help("abatement_cost"))


def _sensitivity(st) -> None:
    st.header("Sensitivity — on demand")
    st.write("One assumption family is varied at a time. This is intentionally not a Monte Carlo model and the app does not solve every family on each rerun.")
    variable = st.selectbox(
        "Sensitivity variable",
        list(SENSITIVITY_FAMILIES),
        format_func=lambda v: SENSITIVITY_LABELS[v],
    )
    if st.button("Run sensitivity", type="primary"):
        try:
            with st.spinner(f"Running {SENSITIVITY_LABELS[variable]} sensitivity…"):
                frame = run_sensitivity_request(st.session_state.params, variable, _load_frame(st))
                results = dict(st.session_state.sensitivity_results)
                results[variable] = frame
                st.session_state.sensitivity_results = results
        except ValueError as exc:
            st.error(str(exc))
    frame = st.session_state.sensitivity_results.get(variable)
    if frame is None:
        st.info("Select a family and run it when you need it. Other sensitivity families are not calculated in the background.")
        return
    st.plotly_chart(sensitivity_chart(frame, SENSITIVITY_LABELS[variable]), use_container_width=True)
    st.plotly_chart(sensitivity_cost_chart(frame, SENSITIVITY_LABELS[variable]), use_container_width=True)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    for text in explain_sensitivity_results(frame, variable):
        st.info(text + " This statement is derived from solved results, not generated by an AI model.")


def _methodology(st) -> None:
    st.header("Methodology & learning")
    blocks = {
        "Energy balance": "Hourly electricity demand must be supplied by direct PV, battery discharge or grid import. PV is allocated to load, battery charging or export.",
        "PV": "PV generation equals installed PV capacity multiplied by the validated hourly normalized capacity factor.",
        "Battery": "SOC is stored energy. Charge/discharge efficiencies are explicit, power and SOC bounds are enforced, and optimization uses a cyclic annual SOC condition.",
        "Economics": "The LP minimizes equivalent annualized cost. Initial CAPEX, NPV and simple payback are calculated separately after solving.",
        "Optimization": "Decision variables include PV capacity, battery energy/power and hourly dispatch. HiGHS solves a sparse linear program over 8,760 periods.",
        "Carbon": "Modeled emissions equal grid imports times the explicit grid-emission factor. Exports receive no CO₂ credit. A carbon target can shrink the feasible set.",
        "Sensitivity": "One input family changes at a time. Results are conditional what-if analyses, not probabilities or forecasts.",
        "Limitations": "The current demo uses synthetic data and simplified techno-economic assumptions; it is a screening model, not detailed engineering.",
    }
    for title, text in blocks.items():
        with st.expander(title):
            st.write(text)
    st.subheader("How the optimizer works")
    st.markdown(
        "- **Decision variable:** a quantity the solver is allowed to choose.\n"
        "- **Constraint:** a mathematical rule every feasible solution must satisfy.\n"
        "- **Objective:** the annualized system cost the solver minimizes.\n"
        "- **Optimal:** the lowest-cost feasible solution found for the stated model.\n"
        "- **Binding constraint:** a limit that is active at the solution and therefore shapes it.\n"
        "- **Infeasible:** no combination within the stated model bounds satisfies all constraints."
    )
    guide = Path(ROOT / "docs" / "OPTIMIZATION_GUIDE.md")
    method = Path(ROOT / "METHODOLOGY.md")
    with st.expander("Read full optimization guide"):
        st.markdown(guide.read_text(encoding="utf-8"))
    with st.expander("Read full methodology"):
        st.markdown(method.read_text(encoding="utf-8"))


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Industrial Energy Lab", page_icon="⚡", layout="wide")
    _state_defaults(st)
    with st.sidebar:
        st.header("Industrial Energy Lab")
        section = st.radio("Navigate", SECTIONS, index=0)
        st.divider()
        st.caption(f"App v{APP_VERSION}")
        st.caption(f"Model v{OPTIMIZATION_MODEL_VERSION}")
        st.caption(f"Dataset {DATASET_VERSION}")
        st.caption("Offline engine · synthetic demo")
    _render_header(st, section)
    pages = {
        "Overview": _overview,
        "Inputs": _inputs,
        "Baseline": _baseline,
        "Optimized system": _optimized,
        "Hourly results": _hourly,
        "Economics": _economics,
        "Decarbonization": _decarbonization,
        "Sensitivity": _sensitivity,
        "Methodology": _methodology,
    }
    pages[section](st)


if __name__ == "__main__":
    main()
