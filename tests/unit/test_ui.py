from pathlib import Path

import pandas as pd
import pytest

from industrial_energy_lab.explainability.metrics import METRICS
from industrial_energy_lab.ui import APP_VERSION
from industrial_energy_lab.ui.charts import load_duration_curve, monthly_consumption
from industrial_energy_lab.ui.formatting import (
    format_energy_kwh,
    format_eur,
    format_percent,
    format_power_kw,
    metric_help,
)
from industrial_energy_lab.ui.services import default_parameters, load_demo_bundle, validate_custom_load


def test_app_version_is_separate_from_engine_version():
    assert APP_VERSION == "0.4.0"


def test_metric_help_contains_learning_sections():
    help_text = metric_help("wacc")
    assert "Why it matters" in help_text
    assert "How it is calculated" in help_text
    assert "How to interpret it" in help_text
    assert "Related" in help_text
    assert "Source" in help_text


def test_all_ui_metric_ids_exist_in_registry():
    required = {
        "annual_load", "baseline_cost", "baseline_emissions", "average_import_price",
        "import_price_multiplier", "export_price", "pv_capex_rate", "pv_opex_rate",
        "pv_lifetime", "max_pv_capacity", "battery_energy_capex_rate",
        "battery_power_capex_rate", "max_battery_energy", "max_battery_power",
        "battery_charge_efficiency", "battery_discharge_efficiency", "soc_min_fraction",
        "soc_max_fraction", "soc", "opex", "battery_lifetime", "wacc", "project_life",
        "grid_emission_factor", "carbon_target", "optimal_pv", "battery_energy_capacity",
        "battery_power_capacity", "scenario_cost", "annual_saving", "co2_reduction_fraction",
        "pv_capex", "battery_capex", "initial_capex", "export_revenue", "npv", "payback",
        "abatement_cost",
    }
    assert required <= set(METRICS)


def test_ui_formatters_hide_engine_precision():
    assert format_power_kw(4088.348749) == "4.09 MW"
    assert format_energy_kwh(2595.884) == "2.60 MWh"
    assert format_percent(0.334152) == "33.4%"
    assert format_eur(1_750_018) == "€1.75 M"


def test_default_parameters_are_loaded_from_versioned_assumptions():
    p = default_parameters()
    assert p["model_version"] == "0.3.0"
    assert p["case_version"] == "golden-v3"
    assert p["import_price_multiplier"] == 1.0
    assert p["carbon_target"] == 0.0


def test_custom_load_accepts_demo_and_rejects_timeline_mismatch():
    load, _, _, _ = load_demo_bundle()
    validated = validate_custom_load(load)
    assert len(validated) == 8760
    bad = load.copy()
    bad["timestamp_utc"] = pd.to_datetime(bad["timestamp_utc"], utc=True) + pd.Timedelta(hours=1)
    with pytest.raises(ValueError, match="timestamps"):
        validate_custom_load(bad)


def test_baseline_charts_build_from_demo_data():
    load, _, _, _ = load_demo_bundle()
    assert len(load_duration_curve(load).data) >= 1
    assert len(monthly_consumption(load).data) >= 1
