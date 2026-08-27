"""Grid-related greenhouse-gas calculations."""


def grid_emissions_tco2(grid_import_mwh: float, factor_kg_co2_per_mwh: float) -> float:
    """Return grid-related emissions in metric tonnes of CO2."""

    if grid_import_mwh < 0:
        raise ValueError("Grid import must be non-negative.")
    if factor_kg_co2_per_mwh < 0:
        raise ValueError("Emission factor must be non-negative.")
    return float(grid_import_mwh * factor_kg_co2_per_mwh / 1000.0)


def emissions_reduction(base_tco2: float, new_tco2: float) -> tuple[float, float]:
    """Return absolute tCO2 reduction and fractional reduction."""

    if base_tco2 < 0 or new_tco2 < 0:
        raise ValueError("Emissions must be non-negative.")
    absolute = base_tco2 - new_tco2
    fraction = 0.0 if base_tco2 == 0 else absolute / base_tco2
    return float(absolute), float(fraction)


def abatement_cost_eur_per_tco2(delta_cost_eur: float, reduction_tco2: float) -> float | None:
    """Return incremental cost divided by avoided tCO2.

    Positive values mean the lower-emission option costs more. Negative values mean
    the lower-emission option also saves money. Returns None when no CO2 is avoided.
    """

    if reduction_tco2 <= 0:
        return None
    return float(delta_cost_eur / reduction_tco2)
