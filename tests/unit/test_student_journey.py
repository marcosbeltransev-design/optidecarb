from industrial_energy_lab.explainability.glossary import GLOSSARY, get_term
from industrial_energy_lab.learning import CASTELLON_WALKTHROUGH, GUIDED_EXPERIMENTS, LEARNING_PATH
from industrial_energy_lab.learning.examples import crf_learning_example
from industrial_energy_lab.learning.experiments import modified_parameters
from industrial_energy_lab.ui.streamlit_app import SECTIONS


def test_learning_lab_is_part_of_main_navigation_without_replacing_engine_sections():
    assert "Learning Lab" in SECTIONS
    for required in ("Inputs", "Optimized system", "Hourly results", "Economics", "Decarbonization", "Sensitivity"):
        assert required in SECTIONS


def test_wacc_learning_chain_is_complete():
    wacc = get_term("wacc")
    assert wacc.full_name == "Weighted Average Cost of Capital"
    assert "crf" in wacc.related_terms
    assert wacc.example and wacc.why_it_matters and wacc.common_confusion
    low = crf_learning_example(0.05, 25, 1_000_000)
    high = crf_learning_example(0.06, 25, 1_000_000)
    assert high["crf"] > low["crf"]
    exp = next(x for x in GUIDED_EXPERIMENTS if x.experiment_id == "wacc_up")
    assert {"wacc", "crf", "annualized_capex"} <= set(exp.concept_ids)
    params = {"wacc": 0.05, "import_price_multiplier": 1.0, "pv_capex_eur_per_kw": 700.0,
              "battery_energy_capex_eur_per_kwh": 240.0, "battery_power_capex_eur_per_kw": 120.0,
              "carbon_target": 0.0}
    assert modified_parameters(params, "wacc_up")["wacc"] == 0.06


def test_student_journey_covers_foundations_to_real_application():
    names = [name for name, _ in LEARNING_PATH]
    assert names == ["FOUNDATIONS", "ENERGY SYSTEM", "ECONOMICS", "OPTIMIZATION", "DECARBONIZATION", "REAL APPLICATION"]
    covered = {term_id for _, ids in LEARNING_PATH for term_id in ids}
    for required in ("power", "energy", "pv", "soc", "wacc", "crf", "npv", "lp", "binding", "carbon_target", "proxy", "prefeasibility"):
        assert required in covered
    assert len(CASTELLON_WALKTHROUGH) == 10


def test_required_student_terms_exist_in_single_glossary_source():
    required = {"wacc", "crf", "soc", "npv", "capex", "lp", "capacity_factor", "self_consumption", "self_sufficiency", "abatement_cost"}
    assert required <= set(GLOSSARY)
