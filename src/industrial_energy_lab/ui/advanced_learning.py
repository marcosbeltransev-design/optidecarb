"""Visual active-learning components for OptiDecarb v1.3.1.

These components read the committed offline Castellón case data and frozen
learning constants. They do not alter or duplicate optimization equations.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from industrial_energy_lab.learning.advanced_energy import (
    CARBON_FRONTIER,
    FORMULA_LESSONS,
    INTERVIEW_DEFENCE,
    PREDICTION_LESSONS,
    SCREENING_VS_FEASIBILITY,
    TRACEABILITY_CARDS,
    TRANSFER_CASE,
)

ROOT = Path(__file__).resolve().parents[3]
LOAD_PATH = ROOT / "cases" / "ceramic_castellon" / "data" / "industrial_load_8760.csv"
PV_PATH = ROOT / "cases" / "ceramic_castellon" / "data" / "pv_profile_8760.csv"

# OptiDecarb learning palette: blue=data/concept, green=validated/correct,
# amber=assumption/check, red=inconsistency/risk, navy=engineering context.
BLUE = "#1768B2"
NAVY = "#0D2D55"
GREEN = "#16A35B"
AMBER = "#F59E0B"
RED = "#DC2626"
SLATE = "#475569"
PALE_BLUE = "#EAF4FF"
PALE_GREEN = "#ECFDF3"
PALE_AMBER = "#FFF7E6"
PALE_RED = "#FEF2F2"


def inject_learning_theme(st) -> None:
    """Add a restrained, accessible visual language for educational content."""
    st.markdown(
        f"""
        <style>
        .od-legend {{display:flex;gap:.55rem;flex-wrap:wrap;margin:.2rem 0 1rem 0}}
        .od-pill {{padding:.28rem .58rem;border-radius:999px;font-size:.78rem;font-weight:650;border:1px solid rgba(15,23,42,.10)}}
        .od-card {{border:1px solid rgba(15,23,42,.10);border-radius:14px;padding:1rem 1.05rem;margin:.45rem 0;box-shadow:0 2px 10px rgba(15,23,42,.035)}}
        .od-card h4 {{margin:.05rem 0 .42rem 0}}
        .od-blue {{background:{PALE_BLUE};border-left:5px solid {BLUE}}}
        .od-green {{background:{PALE_GREEN};border-left:5px solid {GREEN}}}
        .od-amber {{background:{PALE_AMBER};border-left:5px solid {AMBER}}}
        .od-red {{background:{PALE_RED};border-left:5px solid {RED}}}
        .od-flow {{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.45rem;margin:.7rem 0 1rem 0}}
        .od-flow div {{background:{PALE_BLUE};border:1px solid rgba(23,104,178,.20);border-radius:10px;padding:.55rem;text-align:center;font-size:.78rem;font-weight:650;color:{NAVY}}}
        @media(max-width:760px) {{.od-flow {{grid-template-columns:1fr 1fr}}}}
        </style>
        <div class="od-legend">
          <span class="od-pill" style="background:{PALE_BLUE};color:{NAVY}">● Blue — data / concept</span>
          <span class="od-pill" style="background:{PALE_GREEN};color:#0f6f40">● Green — validated / correct</span>
          <span class="od-pill" style="background:{PALE_AMBER};color:#8a5800">● Amber — assumption / check</span>
          <span class="od-pill" style="background:{PALE_RED};color:#991b1b">● Red — inconsistency / risk</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def learning_loop(st) -> None:
    st.markdown(
        """
        <div class="od-flow">
          <div>1 · Estimate</div><div>2 · Predict</div><div>3 · Calculate / run</div><div>4 · Explain why</div><div>5 · Decide what to check</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _record_review(st, concept: str) -> None:
    review = list(st.session_state.get("advanced_energy_review", []))
    if concept not in review:
        review.append(concept)
    st.session_state["advanced_energy_review"] = review


def _read_case_profiles() -> pd.DataFrame:
    load = pd.read_csv(LOAD_PATH, parse_dates=["timestamp_utc"])
    pv = pd.read_csv(PV_PATH, parse_dates=["timestamp_utc"])
    df = load.merge(pv, on="timestamp_utc", validate="one_to_one")
    df["date"] = df["timestamp_utc"].dt.date
    return df


def _representative_day(df: pd.DataFrame) -> object:
    daily = df.groupby("date", as_index=True).agg(load_kwh=("load_kw", "sum"), pv_equivalent_hours=("capacity_factor", "sum"))
    target_load = float(daily["load_kwh"].median())
    target_pv = float(daily["pv_equivalent_hours"].quantile(0.75))
    load_scale = max(float(daily["load_kwh"].std()), 1.0)
    pv_scale = max(float(daily["pv_equivalent_hours"].std()), 1e-6)
    score = (daily["load_kwh"] - target_load).abs() / load_scale + (daily["pv_equivalent_hours"] - target_pv).abs() / pv_scale
    return score.idxmin()


def render_formula_lab(st) -> None:
    st.markdown("### Formula → units → intuition")
    st.caption("Choose one relationship. The objective is to understand the units before memorising the formula.")
    lesson = st.selectbox("Energy relationship", FORMULA_LESSONS, format_func=lambda x: x.title, key="formula_lesson")
    c1, c2 = st.columns([1.05, 1])
    with c1:
        st.markdown(f'<div class="od-card od-blue"><h4>{lesson.title}</h4><b>Formula</b><br>{lesson.formula}<br><br><b>Units</b><br>{lesson.units}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="od-card od-green"><h4>Engineering intuition</h4>{lesson.intuition}<br><br><b>Example:</b> {lesson.example}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="od-card od-red"><b>Common error:</b> {lesson.common_error}</div>', unsafe_allow_html=True)


def render_case_data_visuals(st) -> None:
    """Teach profile reading using the committed representative Castellón data."""
    st.markdown("### Read the load before you optimize it")
    st.caption("These charts use the committed 8,760-hour representative Castellón case — not an invented display curve.")
    try:
        df = _read_case_profiles()
    except Exception as exc:  # educational UI should fail softly; core validation remains elsewhere
        st.warning(f"Representative profile visual is unavailable: {exc}")
        return

    day = _representative_day(df)
    d = df[df["date"] == day].copy()
    d["hour"] = d["timestamp_utc"].dt.hour
    d["load_mw"] = d["load_kw"] / 1000.0
    d["pv_available_mw"] = d["capacity_factor"] * 2.972

    prediction = st.radio(
        "Before opening the interpretation: what does this representative load profile suggest?",
        ("Strongly intermittent plant", "Relatively steady industrial load", "The annual energy must be wrong"),
        index=None,
        key="profile_prediction",
        horizontal=True,
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["hour"], y=d["load_mw"], name="Plant load", mode="lines+markers", line={"color": BLUE, "width": 3}))
    fig.add_trace(go.Scatter(x=d["hour"], y=d["pv_available_mw"], name="PV available at 2.972 MWp", mode="lines", line={"color": GREEN, "width": 3}))
    fig.update_layout(
        height=390,
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        title=f"Representative day selected from the frozen 2025 case · {day}",
        xaxis_title="Hour (UTC)",
        yaxis_title="Power (MW)",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12},
    )
    st.plotly_chart(fig, use_container_width=True, key="rep_day_chart")

    if st.button("Reveal profile interpretation", key="profile_reveal"):
        if prediction == "Relatively steady industrial load":
            st.success("Good. The case has a high load factor, so demand remains relatively steady compared with its peak.")
        else:
            _record_review(st, "Read an industrial load profile and connect it to load factor")
            st.warning("The frozen case is intentionally relatively steady: annual average ≈ 1.71 MW, peak ≈ 2.00 MW, load factor ≈ 85.7%.")
        st.info("**Why this matters:** PV value depends on daytime coincidence. A steady industrial load can absorb a large share of daytime PV before exports rise.")

    sorted_load = df["load_kw"].sort_values(ascending=False).reset_index(drop=True) / 1000.0
    duration_pct = (sorted_load.index.to_series() + 1) / len(sorted_load) * 100
    ldc = go.Figure(go.Scatter(x=duration_pct, y=sorted_load, mode="lines", line={"color": NAVY, "width": 3}, name="Load duration curve"))
    ldc.update_layout(
        height=330,
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        title="Load duration curve — how often each demand level is exceeded",
        xaxis_title="Share of annual hours (%)",
        yaxis_title="Demand (MW)",
        showlegend=False,
    )
    st.plotly_chart(ldc, use_container_width=True, key="ldc_chart")
    st.markdown('<div class="od-card od-amber"><b>What chronology is lost?</b> A load-duration curve preserves the distribution of demand but forgets <i>when</i> each hour occurred. That is why it cannot replace the 8,760-hour chronology for PV/BESS dispatch.</div>', unsafe_allow_html=True)


def render_one_day_energy_story(st) -> None:
    st.markdown("### One-day energy story — reconstruct the balance")
    st.caption("Economic optimum: 2.972 MWp PV and 0 MWh battery. Use the hour selector to follow each MWh equivalent through the electrical balance.")
    try:
        df = _read_case_profiles()
    except Exception as exc:
        st.warning(f"Hourly energy story is unavailable: {exc}")
        return
    day = _representative_day(df)
    d = df[df["date"] == day].copy()
    d["hour"] = d["timestamp_utc"].dt.hour
    d["load_mw"] = d["load_kw"] / 1000.0
    d["pv_mw"] = d["capacity_factor"] * 2.972
    d["pv_to_load_mw"] = d[["load_mw", "pv_mw"]].min(axis=1)
    d["grid_mw"] = (d["load_mw"] - d["pv_mw"]).clip(lower=0)
    d["export_mw"] = (d["pv_mw"] - d["load_mw"]).clip(lower=0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["hour"], y=d["pv_to_load_mw"], stackgroup="supply", name="PV → load", line={"color": GREEN}))
    fig.add_trace(go.Scatter(x=d["hour"], y=d["grid_mw"], stackgroup="supply", name="Grid → load", line={"color": BLUE}))
    fig.add_trace(go.Scatter(x=d["hour"], y=d["load_mw"], mode="lines", name="Load", line={"color": NAVY, "width": 3, "dash": "dot"}))
    fig.update_layout(height=360, margin={"l": 20, "r": 20, "t": 40, "b": 20}, xaxis_title="Hour (UTC)", yaxis_title="Power (MW)", hovermode="x unified", legend={"orientation": "h", "y": 1.13})
    st.plotly_chart(fig, use_container_width=True, key="day_balance_chart")

    hour = st.slider("Inspect one hour", 0, 23, 12, key="energy_story_hour")
    row = d[d["hour"] == hour].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Load", f"{row['load_mw']:.2f} MW")
    c2.metric("PV available", f"{row['pv_mw']:.2f} MW")
    c3.metric("Grid import", f"{row['grid_mw']:.2f} MW")
    c4.metric("PV export", f"{row['export_mw']:.2f} MW")
    st.markdown(
        f'<div class="od-card od-blue"><b>Balance at {hour:02d}:00 UTC</b><br>Load {row["load_mw"]:.3f} MW = PV to load {row["pv_to_load_mw"]:.3f} MW + grid {row["grid_mw"]:.3f} MW. PV export = {row["export_mw"]:.3f} MW. Battery = 0 in this economic optimum.</div>',
        unsafe_allow_html=True,
    )


def render_prediction_lab(st) -> None:
    st.markdown("### Predict before you reveal the model result")
    st.caption("Direction first, decimals second. These are frozen Castellón sensitivity results already covered by regression tests.")
    lesson = st.selectbox("Scenario", PREDICTION_LESSONS, format_func=lambda x: x.change, key="prediction_lesson")
    answer = st.radio(lesson.question, lesson.options, index=None, key=f"prediction_{lesson.lesson_id}", horizontal=True)
    if st.button("Reveal validated result", key="prediction_reveal"):
        if answer == lesson.correct:
            st.success(f"Prediction correct — **{lesson.correct}**")
        else:
            _record_review(st, f"Sensitivity reasoning: {lesson.change}")
            st.warning(f"Better prediction: **{lesson.correct}**")
        c1, c2 = st.columns(2)
        c1.metric("Before", lesson.before)
        c2.metric("After", lesson.after)
        st.markdown(f'<div class="od-card od-green"><b>Why:</b> {lesson.why}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="od-card od-amber"><b>What would I validate next?</b> {lesson.next_check}</div>', unsafe_allow_html=True)


def render_carbon_frontier(st) -> None:
    st.markdown("### Why 20% is non-binding and 40% changes the system")
    frontier = pd.DataFrame(CARBON_FRONTIER)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=frontier["target_pct"], y=frontier["pv_mw"], name="PV MWp", marker_color=GREEN))
    fig.add_trace(go.Bar(x=frontier["target_pct"], y=frontier["battery_mwh"], name="Battery MWh", marker_color=BLUE))
    fig.update_layout(barmode="group", height=360, margin={"l": 20, "r": 20, "t": 40, "b": 20}, xaxis_title="Minimum electrical CO₂ reduction target (%)", yaxis_title="Capacity", legend={"orientation": "h", "y": 1.12})
    st.plotly_chart(fig, use_container_width=True, key="carbon_frontier_capacity")

    cost = go.Figure(go.Scatter(x=frontier["target_pct"], y=frontier["annualized_cost_eur"], mode="lines+markers", line={"color": AMBER, "width": 3}, marker={"size": 10}))
    cost.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, xaxis_title="Minimum electrical CO₂ reduction target (%)", yaxis_title="Annualized system cost (€/year)", showlegend=False)
    st.plotly_chart(cost, use_container_width=True, key="carbon_frontier_cost")

    st.markdown('<div class="od-card od-green"><b>0–30%:</b> the economic optimum already achieves ≈30.4%, so these minimum targets do not force a new solution.</div>', unsafe_allow_html=True)
    st.markdown('<div class="od-card od-amber"><b>40%:</b> the target is stricter than the unconstrained optimum. The constraint becomes binding, PV increases and storage appears.</div>', unsafe_allow_html=True)


def render_traceability(st) -> None:
    st.markdown("### Model knows · assumes · does not know")
    for card in TRACEABILITY_CARDS:
        with st.expander(card["result"]):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="od-card od-green"><b>MODEL KNOWS</b><br>{card["knows"]}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="od-card od-amber"><b>MODEL ASSUMES</b><br>{card["assumes"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="od-card od-red"><b>MODEL DOES NOT KNOW</b><br>{card["does_not_know"]}</div>', unsafe_allow_html=True)


def render_screening_vs_feasibility(st) -> None:
    st.markdown("### Screening result ≠ build-ready design")
    df = pd.DataFrame(SCREENING_VS_FEASIBILITY, columns=["Topic", "Screening can use", "Feasibility should validate"])
    st.dataframe(df, hide_index=True, use_container_width=True)


def render_transfer_case(st) -> None:
    st.markdown("### Unseen transfer case")
    st.caption(TRANSFER_CASE["label"])
    st.markdown(f"**{TRANSFER_CASE['title']}**")
    for fact in TRANSFER_CASE["facts"]:
        st.write(f"- {fact}")
    st.markdown("**Try before opening the solution:**")
    for i, q in enumerate(TRANSFER_CASE["questions"], 1):
        st.write(f"{i}. {q}")
    st.text_area("Your reasoning", key="transfer_case_reasoning", height=120)
    with st.expander("Worked reasoning"):
        for i, a in enumerate(TRANSFER_CASE["worked"], 1):
            st.write(f"**{i}.** {a}")


def render_interview_defence(st) -> None:
    st.markdown("### Can you defend the energy model?")
    st.caption("Answer aloud first. These are technical-energy questions, not generic HR preparation.")
    for q, a in INTERVIEW_DEFENCE:
        with st.expander(q):
            st.write(a)


def render_session_review(st) -> None:
    review = list(st.session_state.get("advanced_energy_review", []))
    st.markdown("### Review before finishing")
    if not review:
        st.success("No review items have been recorded in this session yet. Keep predicting before revealing answers.")
        return
    st.warning("Revisit these concepts before ending the session:")
    for item in review[:5]:
        st.write(f"- {item}")
    if st.button("Clear session review", key="clear_advanced_review"):
        st.session_state["advanced_energy_review"] = []
        st.rerun()
