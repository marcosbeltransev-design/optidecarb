"""Active-learning and junior-engineer helpers for OptiDecarb."""
from .catalog import CASTELLON_WALKTHROUGH, COMMON_TRAPS, CONCEPT_DEPENDENCIES, GUIDED_EXPERIMENTS, LEARNING_PATH, QUESTIONS, TERM_DIFFICULTY
from .examples import battery_duration_hours, co2_from_grid_energy_tco2, crf_learning_example, energy_from_power, three_hour_battery_lab
from .experiments import compare_prediction, experiment_by_id, modified_parameters, result_comparison
from .hourly import energy_balance_residual_kwh, explain_dispatch_hour
from .industry import (
    CHECKLISTS,
    DECISION_STAGES,
    GOOD_JUNIOR_QUESTIONS,
    INDUSTRY_CASES,
    INDUSTRY_CASES_BY_ID,
    PROFESSIONAL_TERMS,
    PROFESSIONAL_TERMS_BY_ID,
    ROLE_PERSPECTIVES,
    WORK_PHRASES,
    validate_industry_catalog,
)
from .models import DecisionStage, GuidedExperiment, IndustryCase, LearningQuestion, PredictionComparison, ProfessionalTerm, RolePerspective

__all__ = [
    "CASTELLON_WALKTHROUGH", "COMMON_TRAPS", "CONCEPT_DEPENDENCIES", "GUIDED_EXPERIMENTS", "LEARNING_PATH", "QUESTIONS", "TERM_DIFFICULTY",
    "battery_duration_hours", "co2_from_grid_energy_tco2", "crf_learning_example", "energy_from_power", "three_hour_battery_lab",
    "compare_prediction", "experiment_by_id", "modified_parameters", "result_comparison", "energy_balance_residual_kwh", "explain_dispatch_hour",
    "CHECKLISTS", "DECISION_STAGES", "GOOD_JUNIOR_QUESTIONS", "INDUSTRY_CASES", "INDUSTRY_CASES_BY_ID",
    "PROFESSIONAL_TERMS", "PROFESSIONAL_TERMS_BY_ID", "ROLE_PERSPECTIVES", "WORK_PHRASES", "validate_industry_catalog",
    "DecisionStage", "GuidedExperiment", "IndustryCase", "LearningQuestion", "PredictionComparison", "ProfessionalTerm", "RolePerspective",
]
