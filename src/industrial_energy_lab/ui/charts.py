"""Plotly charts for the engineering interface."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def load_duration_curve(load: pd.DataFrame):
    values = np.sort(load["load_kw"].to_numpy(float))[::-1] / 1000.0
    frame = pd.DataFrame({"Hours exceeded": np.arange(1, len(values) + 1), "Demand (MW)": values})
    fig = px.line(frame, x="Hours exceeded", y="Demand (MW)")
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig


def monthly_consumption(load: pd.DataFrame):
    frame = load.copy()
    ts = pd.to_datetime(frame["timestamp_utc"], utc=True)
    monthly = frame.assign(month=ts.dt.strftime("%b")).groupby("month", sort=False)["load_kw"].sum().div(1000).reset_index(name="Consumption (MWh)")
    fig = px.bar(monthly, x="month", y="Consumption (MWh)")
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig


def hourly_energy(dispatch: pd.DataFrame, start: int = 0, hours: int = 168):
    view = dispatch.iloc[start : start + hours].copy()
    ts = pd.to_datetime(view["timestamp_utc"], utc=True, errors="coerce")
    fig = go.Figure()
    for col, label in [
        ("load_kwh", "Load"), ("pv_generation_kwh", "PV generation"),
        ("grid_import_kwh", "Grid import"), ("battery_charge_kwh", "Battery charge"),
        ("battery_discharge_kwh", "Battery discharge"),
    ]:
        if col in view:
            fig.add_trace(go.Scatter(x=ts, y=view[col] / 1000.0, name=label, mode="lines"))
    fig.update_layout(yaxis_title="Energy per hour (MWh)", xaxis_title="UTC", margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h"))
    return fig


def soc_chart(dispatch: pd.DataFrame, battery_energy_kwh: float | None, start: int = 0, hours: int = 168):
    view = dispatch.iloc[start : start + hours].copy()
    ts = pd.to_datetime(view["timestamp_utc"], utc=True, errors="coerce")
    cap = float(battery_energy_kwh or 0.0)
    if cap > 1e-9:
        y = 100.0 * view["soc_kwh"] / cap
        ylabel = "SOC (%)"
    else:
        y = view["soc_kwh"] / 1000.0
        ylabel = "SOC (MWh)"
    fig = px.line(x=ts, y=y, labels={"x": "UTC", "y": ylabel})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig


def economics_breakdown(result):
    frame = pd.DataFrame({
        "Component": ["Annualized PV", "Annualized battery", "Grid purchases", "Export revenue"],
        "EUR/year": [
            result.annualized_pv_cost_eur or 0.0,
            result.annualized_battery_cost_eur or 0.0,
            result.grid_purchase_cost_eur or 0.0,
            -(result.export_revenue_eur or 0.0),
        ],
    })
    fig = px.bar(frame, x="Component", y="EUR/year")
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig


def frontier_cost(frontier: pd.DataFrame):
    frame = frontier.copy()
    frame["CO2 reduction target (%)"] = 100 * pd.to_numeric(frame["carbon_target"], errors="coerce")
    frame["Annualized cost (M€/year)"] = pd.to_numeric(frame["annualized_cost_eur"], errors="coerce") / 1_000_000
    fig = px.line(
        frame, x="CO2 reduction target (%)", y="Annualized cost (M€/year)",
        markers=True, hover_data=["status", "carbon_constraint_binding"],
    )
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig


def frontier_capacities(frontier: pd.DataFrame):
    frame = frontier.copy()
    frame["Target (%)"] = 100 * pd.to_numeric(frame["carbon_target"], errors="coerce")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame["Target (%)"], y=pd.to_numeric(frame["pv_capacity_kw"], errors="coerce") / 1000, name="PV (MW)", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=frame["Target (%)"], y=pd.to_numeric(frame["battery_energy_capacity_kwh"], errors="coerce") / 1000, name="Battery energy (MWh)", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=frame["Target (%)"], y=pd.to_numeric(frame["battery_power_capacity_kw"], errors="coerce") / 1000, name="Battery power (MW)", mode="lines+markers"))
    fig.update_layout(xaxis_title="Minimum CO₂ reduction (%)", yaxis_title="Capacity", margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h"))
    return fig


def sensitivity_chart(frame: pd.DataFrame, variable_label: str):
    data = frame.copy()
    data["PV (MW)"] = pd.to_numeric(data["pv_capacity_kw"], errors="coerce") / 1000
    data["Battery energy (MWh)"] = pd.to_numeric(data["battery_energy_capacity_kwh"], errors="coerce") / 1000
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["input_value"], y=data["PV (MW)"], name="PV (MW)", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=data["input_value"], y=data["Battery energy (MWh)"], name="Battery energy (MWh)", mode="lines+markers"))
    fig.update_layout(xaxis_title=variable_label, yaxis_title="Optimized capacity", margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h"))
    return fig


def sensitivity_cost_chart(frame: pd.DataFrame, variable_label: str):
    data = frame.copy()
    data["Annualized cost (M€/year)"] = pd.to_numeric(data["annualized_cost_eur"], errors="coerce") / 1_000_000
    fig = px.line(data, x="input_value", y="Annualized cost (M€/year)", markers=True, labels={"input_value": variable_label})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    return fig
