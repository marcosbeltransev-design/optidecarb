"""Deterministic industrial-energy data-forensics and traceability lessons.

This module contains teaching content only. It does not call the optimizer, alter
engineering equations, or access external services.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ForensicCase:
    case_id: str
    title: str
    context: str
    x: tuple[str, ...]
    y: tuple[float, ...]
    y_label: str
    options: tuple[str, ...]
    correct: str
    why: str
    first_action: str
    professional_decision: str


FORENSIC_CASES = (
    ForensicCase(
        "missing_interval",
        "Missing interval",
        "Illustrative hourly import series. The plant normally reports one value every hour.",
        ("00:00", "01:00", "02:00", "04:00", "05:00", "06:00"),
        (1.62, 1.66, 1.69, 1.71, 1.68, 1.73),
        "Demand (MW)",
        ("Normal variation", "One hourly interval is missing", "The meter must be broken"),
        "One hourly interval is missing",
        "The sequence jumps from 02:00 to 04:00. A visually smooth load curve can still have an incomplete time axis.",
        "Check the timestamp index before interpolating or filling anything. Confirm whether 03:00 is absent in the source export.",
        "Do not silently invent the missing energy. Document whether you recover it, estimate it, or exclude the affected period.",
    ),
    ForensicCase(
        "duplicate_interval",
        "Duplicate timestamp",
        "Illustrative meter export. Two records carry the same timestamp.",
        ("09:00", "10:00", "11:00", "11:00", "12:00", "13:00"),
        (1.58, 1.61, 1.65, 1.67, 1.70, 1.72),
        "Demand (MW)",
        ("A duplicate timestamp exists", "This proves two meters are being added", "Nothing is wrong"),
        "A duplicate timestamp exists",
        "Two different values share 11:00. Summing or averaging them automatically could distort annual energy unless you understand why the duplicate exists.",
        "Identify the source row IDs / meter channels and determine whether this is duplication, revision, or two different measurements.",
        "Resolve the data lineage first; only then decide whether to keep, replace, aggregate, or reject one record.",
    ),
    ForensicCase(
        "flatline",
        "Suspicious flatline",
        "Illustrative industrial demand. Real plants can be steady, but perfectly repeated values deserve a check.",
        ("00", "01", "02", "03", "04", "05", "06", "07", "08", "09"),
        (1.64, 1.64, 1.64, 1.64, 1.64, 1.64, 1.64, 1.64, 1.70, 1.73),
        "Demand (MW)",
        ("Definitely correct because industry is steady", "Potential meter/data freeze", "The units must be MWh"),
        "Potential meter/data freeze",
        "A high-load-factor plant can be stable, but eight exactly identical values may indicate a frozen register, forward-filled export, or rounded data.",
        "Compare with raw meter resolution, neighbouring channels, production logs and the original export before modifying the series.",
        "Flag the interval as suspicious rather than automatically deleting it. Evidence decides whether it is real operation or a data artefact.",
    ),
    ForensicCase(
        "unit_scale",
        "Plausible shape, impossible scale",
        "The file column is labelled 'MW', but the values are around 1,700 for a site believed to consume about 15 GWh/year.",
        ("00", "01", "02", "03", "04", "05"),
        (1680, 1710, 1740, 1705, 1690, 1750),
        "Reported value",
        ("Likely 1,700 MW industrial demand", "Likely kW values with a unit-label problem", "Annual energy does not help"),
        "Likely kW values with a unit-label problem",
        "1,700 MW sustained would imply orders of magnitude more than 15 GWh/year. Around 1,700 kW = 1.7 MW is consistent with the representative scale.",
        "Use annual MWh ÷ hours as an order-of-magnitude check, then confirm the meter/export unit from source documentation.",
        "Never repair units from intuition alone. Use the sanity check to detect the issue, then verify the actual source unit.",
    ),
    ForensicCase(
        "negative_net_meter",
        "Negative midday values",
        "Illustrative net-meter series at a site that may export PV. Sign convention has not yet been documented.",
        ("08", "09", "10", "11", "12", "13", "14", "15"),
        (0.82, 0.51, 0.18, -0.09, -0.24, -0.17, 0.06, 0.39),
        "Net grid power (MW)",
        ("Delete every negative value", "It may represent export; confirm the sign convention", "It proves the PV model is wrong"),
        "It may represent export; confirm the sign convention",
        "Negative net import can be physically valid when onsite generation exceeds load, depending on the meter convention.",
        "Confirm whether positive means import and negative means export, and whether the series is gross import, net exchange, or a submeter.",
        "Meter boundary and sign convention are engineering metadata. Treat them as required inputs, not formatting details.",
    ),
)


TRACE_CHAINS = (
    {
        "title": "Why is representative average demand about 1.71 MW?",
        "steps": (
            ("PUBLIC / SECTOR CONTEXT", "Castellón ceramic-sector public evidence establishes the order of magnitude."),
            ("MODEL ASSUMPTION", "Representative annual electrical scale selected: 15,000 MWh/year."),
            ("CALCULATION", "15,000 MWh ÷ 8,760 h = 1.712 MW average."),
            ("VALIDATION", "Peak ≈ 2.00 MW, so load factor ≈ 85.7%; average < peak is physically consistent."),
            ("USE", "The 8,760-hour load profile becomes the electrical baseline for PV/BESS screening."),
        ),
    },
    {
        "title": "Where does the PV business case come from?",
        "steps": (
            ("PUBLIC EVIDENCE", "PVGIS methodology is used as the solar-resource reference."),
            ("OFFLINE CASE", "A deterministic PVGIS-calibrated 8,760-hour capacity-factor profile is committed in the case."),
            ("CALCULATION", "Installed MWp × hourly capacity factor gives hourly PV availability."),
            ("ENERGY BALANCE", "PV is split between onsite load, battery charging where applicable, and export."),
            ("DECISION", "Avoided grid purchases, export value and CAPEX help determine the economic optimum."),
        ),
    },
    {
        "title": "Why can electricity-price validation change the recommendation?",
        "steps": (
            ("PUBLIC EVIDENCE", "OMIE 2025 day-ahead prices calibrate the wholesale energy-price proxy."),
            ("PROXY", "The proxy is not the complete plant-specific industrial bill."),
            ("MODEL INPUT", "Hourly import price affects the value of every avoided grid MWh."),
            ("SENSITIVITY", "In the frozen +20% price test, optimal PV moves from 2.972 to 3.193 MWp."),
            ("NEXT DATA", "A real tariff / contract and invoices are therefore high-value validation inputs."),
        ),
    },
    {
        "title": "Why does a 40% CO₂ target change the system?",
        "steps": (
            ("PUBLIC EVIDENCE", "Red Eléctrica public generation/emissions data support the representative grid factor."),
            ("MODEL BOUNDARY", "Only modeled grid-import electricity receives the constant factor; export gets no CO₂ credit."),
            ("BASE RESULT", "The economic optimum already achieves about 30.4% electrical CO₂ reduction."),
            ("CONSTRAINT", "A 20% minimum is already met; 40% is not, so the target becomes binding."),
            ("SYSTEM RESPONSE", "The validated 40% case adds more PV and introduces BESS to reduce grid imports further."),
        ),
    },
)


VALIDATION_PRIORITIES = (
    {
        "assumption": "Electricity-price level",
        "tested_change": "+20%",
        "pv_before_mw": 2.972,
        "pv_after_mw": 3.193,
        "next_data": "Real tariff / contract + recent invoices",
        "why": "The price changes the value of avoided grid purchases.",
    },
    {
        "assumption": "PV CAPEX",
        "tested_change": "+20%",
        "pv_before_mw": 2.972,
        "pv_after_mw": 2.788,
        "next_data": "Comparable EPC budget quotations",
        "why": "PV investment cost directly changes the economics of extra MWp.",
    },
    {
        "assumption": "WACC",
        "tested_change": "5% → 6%",
        "pv_before_mw": 2.972,
        "pv_after_mw": 2.870,
        "next_data": "Finance hurdle rate / project WACC",
        "why": "Financing assumptions change annualized CAPEX and discounted value.",
    },
    {
        "assumption": "Battery CAPEX",
        "tested_change": "-20%",
        "pv_before_mw": 2.972,
        "pv_after_mw": 2.972,
        "next_data": "BESS quote only if storage services/constraints justify deeper study",
        "why": "In this tested unconstrained case, cheaper storage still does not enter the optimum.",
    },
)


DATA_CONFIDENCE_LADDER = (
    ("MEASURED SITE DATA", "Interval meter exports, invoices, production records", "Highest relevance when boundary and quality are validated"),
    ("OFFICIAL / PUBLIC DATA", "Grid factors, market data, public sector evidence", "Good external evidence, but may still need site adaptation"),
    ("SUPPLIER / EPC DATA", "Budget quote, datasheet, yield proposal", "Useful when scope, guarantees and exclusions are comparable"),
    ("PROXY / BENCHMARK", "Wholesale price proxy, public CAPEX range", "Useful for screening; must not be presented as plant-specific fact"),
    ("MODEL ASSUMPTION", "Representative scale, export value, WACC where not yet confirmed", "Transparent placeholder that should be challenged by sensitivity"),
)


def forensic_case(case_id: str) -> ForensicCase:
    """Return one deterministic forensic lesson by ID."""
    return next(case for case in FORENSIC_CASES if case.case_id == case_id)
