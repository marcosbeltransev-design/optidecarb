"""Small, dependency-light data models for the screening engine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GridAssumptions:
    """Grid parameters used by baseline calculations.

    Prices are supplied hourly by dataset. The emissions factor is intentionally
    explicit so it cannot be silently inferred from an external service.
    """

    emissions_factor_kg_co2_per_mwh: float

    def __post_init__(self) -> None:
        if self.emissions_factor_kg_co2_per_mwh < 0:
            raise ValueError("Grid emissions factor must be non-negative.")


@dataclass(frozen=True)
class FinancialAssumptions:
    """Financial inputs shared by economic calculations."""

    discount_rate: float
    project_life_years: int

    def __post_init__(self) -> None:
        if self.discount_rate <= -1:
            raise ValueError("Discount rate must be greater than -100%.")
        if self.project_life_years <= 0:
            raise ValueError("Project life must be a positive integer.")


@dataclass(frozen=True)
class BaselineResult:
    """Annual baseline metrics before adding on-site technologies."""

    annual_consumption_mwh: float
    annual_energy_cost_eur: float
    annual_emissions_tco2: float
    model_version: str
    dataset_version: str
    case_version: str
