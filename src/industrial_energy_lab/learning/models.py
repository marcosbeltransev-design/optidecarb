"""Data models for deterministic student and junior-engineer learning content."""
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


@dataclass(frozen=True)
class ProfessionalTerm:
    """Professional vocabulary taught with clear international English."""

    term_id: str
    term: str
    full_name: str
    easy_explanation: str
    where_used: str
    example_sentence: str
    difficulty: str = "INTERMEDIATE"
    spanish_clarification: str = ""


@dataclass(frozen=True)
class IndustryCase:
    """A deterministic mini-case for professional judgement practice."""

    case_id: str
    title: str
    situation: str
    available_information: tuple[str, ...]
    question: str
    options: tuple[str, ...]
    correct_option: str
    junior_answer: str
    why_incomplete: str
    better_answer: str
    why_correct: str
    other_options_feedback: tuple[str, ...]
    checks: tuple[str, ...]
    data_to_request: tuple[str, ...]
    main_lesson: str


@dataclass(frozen=True)
class RolePerspective:
    role_id: str
    label: str
    questions: tuple[str, ...]
    junior_lesson: str


@dataclass(frozen=True)
class DecisionStage:
    stage: str
    easy_explanation: str
    reasonable_output: str
