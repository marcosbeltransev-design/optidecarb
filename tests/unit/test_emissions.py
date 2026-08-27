import pytest

from industrial_energy_lab.economics.emissions import (
    abatement_cost_eur_per_tco2,
    emissions_reduction,
    grid_emissions_tco2,
)


def test_grid_emissions_simple_known_case() -> None:
    assert grid_emissions_tco2(1000.0, 200.0) == pytest.approx(200.0)


def test_emissions_reduction() -> None:
    absolute, fraction = emissions_reduction(100.0, 65.0)
    assert absolute == pytest.approx(35.0)
    assert fraction == pytest.approx(0.35)


def test_abatement_cost_sign_convention() -> None:
    assert abatement_cost_eur_per_tco2(20_000.0, 100.0) == pytest.approx(200.0)
    assert abatement_cost_eur_per_tco2(-20_000.0, 100.0) == pytest.approx(-200.0)
    assert abatement_cost_eur_per_tco2(1.0, 0.0) is None
