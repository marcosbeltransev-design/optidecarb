"""Data models for deterministic student-learning content."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class LearningQuestion:
    question_id: str
    prompt: str
    options: tuple[str, ...]
    correct_option: str
    explanation: str
    difficulty: str = "FOUNDATION"


@dataclass(frozen=True)
class GuidedExperiment:
    experiment_id: str
    title: str
    concept_ids: tuple[str, ...]
    question: str
    changed_parameter: str
    base_value: float | None
    experiment_value: float | None
    prediction_options: tuple[str, ...]
    takeaway: str
    uses_full_model: bool = True


@dataclass(frozen=True)
class PredictionComparison:
    metric: str
    prediction: str
    observed_direction: str
    correct: bool
    before: float
    after: float
    unit: str
    explanation: str
