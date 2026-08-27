from industrial_energy_lab.explainability.glossary import (
    GLOSSARY,
    REQUIRED_ACRONYMS,
    get_term,
    term_help,
    validate_glossary,
)


def test_glossary_is_complete_and_internally_valid():
    validate_glossary()
    assert len(GLOSSARY) >= 30


def test_required_acronyms_have_expanded_names():
    for term_id in REQUIRED_ACRONYMS:
        term = get_term(term_id)
        assert term.full_name
        assert term.term != term.full_name


def test_key_learning_concepts_are_available():
    required = {
        "power", "energy", "pv", "soc", "cyclic_soc", "capex", "opex",
        "annualized_capex", "wacc", "crf", "npv", "payback", "baseline",
        "lp", "decision_variable", "objective_function", "constraint", "binding",
        "infeasible", "self_consumption", "self_sufficiency", "carbon_target",
        "abatement_cost", "sensitivity", "proxy", "derived_value", "model_assumption",
        "prefeasibility", "hours8760", "public_data", "representative_model",
        "real_plant_data",
    }
    assert required <= set(GLOSSARY)


def test_help_explains_wacc_without_assuming_prior_knowledge():
    text = term_help("wacc")
    assert "Weighted Average Cost of Capital" in text
    assert "electricity price" in text
    assert "annualized" in text


def test_power_energy_example_is_explicit():
    assert "1 MW for 1 hour = 1 MWh" in get_term("energy").example
