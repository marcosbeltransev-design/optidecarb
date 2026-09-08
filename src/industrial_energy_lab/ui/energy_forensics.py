"""Visual industrial-energy forensics and evidence-priority teaching components."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from industrial_energy_lab.learning.energy_forensics import (
    DATA_CONFIDENCE_LADDER,
    FORENSIC_CASES,
    TRACE_CHAINS,
    VALIDATION_PRIORITIES,
)
from industrial_energy_lab.ui.advanced_learning import AMBER, BLUE, GREEN, NAVY, RED


def _record_review(st, concept: str) -> None:
    review = list(st.session_state.get("advanced_energy_review", []))
    if concept not in review:
        review.append(concept)
    st.session_state["advanced_energy_review"] = review


def render_visual_forensics(st) -> None:
    st.markdown("### Energy Data Forensics — spot the problem before cleaning it")
    st.caption("Small illustrative meter snippets. Diagnose first; do not let a cleaning rule make the engineering decision for you.")

    case = st.selectbox("Forensic case", FORENSIC_CASES, format_func=lambda c: c.title, key="forensic_case")
    st.info(case.context)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(case.x),
            y=list(case.y),
            mode="lines+markers",
            name=case.title,
            line={"color": BLUE, "width": 3},
            marker={"size": 9},
        )
    )
    fig.update_layout(
        height=315,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis_title="Interval / timestamp",
        yaxis_title=case.y_label,
        showlegend=False,
        hovermode="x",
    )
    st.plotly_chart(fig, use_container_width=True, key=f"forensic_chart_{case.case_id}")

    answer = st.radio(
        "What is the best first diagnosis?",
        case.options,
        index=None,
        key=f"forensic_answer_{case.case_id}",
    )
    if st.button("Reveal forensic reasoning", key=f"forensic_reveal_{case.case_id}"):
        if answer == case.correct:
            st.success(f"Good diagnosis — **{case.correct}**")
        else:
            _record_review(st, f"Energy data forensics: {case.title}")
            st.warning(f"Better first diagnosis — **{case.correct}**")
        st.markdown(f"**Why:** {case.why}")
        st.markdown(f"**First action:** {case.first_action}")
        st.warning(f"**Professional decision:** {case.professional_decision}")

    st.caption("Important: these snippets are teaching examples, not measured company data and not replacements for the frozen Castellón case.")


def render_confidence_ladder(st) -> None:
    st.markdown("### How strong is this input?")
    st.caption("Source type is not the same as truth. Relevance, boundary and quality still matter.")
    rows = []
    for rank, (level, example, interpretation) in enumerate(DATA_CONFIDENCE_LADDER, 1):
        rows.append({"Evidence type": level, "Typical energy example": example, "How to use it": interpretation, "Screening order": rank})
    st.dataframe(pd.DataFrame(rows).drop(columns=["Screening order"]), hide_index=True, use_container_width=True)
    st.info("**Key habit:** label a proxy as a proxy and an assumption as an assumption. Do not make a weak input look stronger by adding decimal places to the output.")


def render_trace_the_number(st) -> None:
    st.markdown("### Trace the number — source → assumption → calculation → decision")
    st.caption("If someone asks 'Where did this number come from?', you should be able to walk backwards through the chain.")
    chain = st.selectbox("Result to trace", TRACE_CHAINS, format_func=lambda x: x["title"], key="trace_chain")

    labels = [label for label, _ in chain["steps"]]
    explanations = [text for _, text in chain["steps"]]
    colors = [BLUE, AMBER, NAVY, GREEN, RED]
    cols = st.columns(len(labels))
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"<div style='border-top:5px solid {colors[i % len(colors)]};border-radius:10px;padding:.65rem;background:rgba(255,255,255,.75);min-height:155px;border-left:1px solid rgba(15,23,42,.08);border-right:1px solid rgba(15,23,42,.08);border-bottom:1px solid rgba(15,23,42,.08)'><b>{labels[i]}</b><br><span style='font-size:.86rem'>{explanations[i]}</span></div>",
                unsafe_allow_html=True,
            )
    st.markdown("**Reverse-check:** start from the recommendation and ask what would happen if one upstream assumption were wrong.")


def render_validation_priority(st) -> None:
    st.markdown("### Sensitivity → what data should I improve next?")
    st.caption("Use model sensitivity to focus validation effort. The chart shows observed PV-capacity movement in the specific frozen one-at-a-time tests — not a universal ranking of all uncertainty.")

    df = pd.DataFrame(VALIDATION_PRIORITIES)
    df["delta_pv_mw"] = df["pv_after_mw"] - df["pv_before_mw"]
    df["absolute_delta_mw"] = df["delta_pv_mw"].abs()
    df = df.sort_values("absolute_delta_mw", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df["absolute_delta_mw"],
            y=df["assumption"],
            orientation="h",
            marker_color=[GREEN if value == 0 else BLUE for value in df["absolute_delta_mw"]],
            customdata=df[["tested_change", "delta_pv_mw"]],
            hovertemplate="%{y}<br>Test: %{customdata[0]}<br>|Δ PV|: %{x:.3f} MWp<br>Signed Δ: %{customdata[1]:+.3f} MWp<extra></extra>",
        )
    )
    fig.update_layout(
        height=340,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis_title="Absolute change in optimal PV in tested scenario (MWp)",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="validation_priority_chart")

    choice = st.radio(
        "If your immediate question is 'how robust is the ~3 MWp PV sizing?', which tested input produced the largest absolute PV movement?",
        tuple(item["assumption"] for item in VALIDATION_PRIORITIES),
        index=None,
        key="validation_priority_choice",
    )
    if st.button("Reveal validation priority lesson", key="validation_priority_reveal"):
        if choice == "Electricity-price level":
            st.success("Correct for these specific tests: the +20% electricity-price case produced the largest absolute PV-capacity movement.")
        else:
            _record_review(st, "Use sensitivity to prioritize better energy-project data")
            st.warning("For these specific tests, electricity-price level produced the largest absolute PV-capacity movement.")
        st.warning("**Do not over-interpret the ranking.** The perturbations are not normalized to equal uncertainty (20% price, 20% PV CAPEX, +1 percentage point WACC, -20% battery CAPEX). This is a decision-support signal, not a statistical uncertainty analysis.")

    st.markdown("#### Turn sensitivity into a data request")
    table = df.sort_values("absolute_delta_mw", ascending=False)[["assumption", "tested_change", "next_data", "why"]].rename(
        columns={"assumption": "Assumption", "tested_change": "Tested change", "next_data": "Better evidence to request", "why": "Why it matters"}
    )
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.info("**Engineering habit:** do not spend the same effort validating every assumption. Improve the evidence most likely to change the decision, while still checking basic physical/data integrity first.")
