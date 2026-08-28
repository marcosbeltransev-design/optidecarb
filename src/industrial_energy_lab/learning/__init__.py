"""Active-learning helpers for OptiDecarb."""
from .catalog import CASTELLON_WALKTHROUGH, COMMON_TRAPS, CONCEPT_DEPENDENCIES, GUIDED_EXPERIMENTS, LEARNING_PATH, QUESTIONS, TERM_DIFFICULTY
from .examples import battery_duration_hours, co2_from_grid_energy_tco2, crf_learning_example, energy_from_power, three_hour_battery_lab
from .experiments import compare_prediction, experiment_by_id, modified_parameters, result_comparison
from .hourly import energy_balance_residual_kwh, explain_dispatch_hour

__all__ = [
    "CASTELLON_WALKTHROUGH", "COMMON_TRAPS", "CONCEPT_DEPENDENCIES", "GUIDED_EXPERIMENTS", "LEARNING_PATH", "QUESTIONS", "TERM_DIFFICULTY",
    "battery_duration_hours", "co2_from_grid_energy_tco2", "crf_learning_example", "energy_from_power", "three_hour_battery_lab",
    "compare_prediction", "experiment_by_id", "modified_parameters", "result_comparison", "energy_balance_residual_kwh", "explain_dispatch_hour",
]
