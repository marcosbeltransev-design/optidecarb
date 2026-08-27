"""Simple payback calculations."""


def simple_payback_years(initial_capex_eur: float, annual_net_savings_eur: float) -> float | None:
    """Return simple payback in years, or None when annual savings are non-positive."""

    if initial_capex_eur < 0:
        raise ValueError("Initial CAPEX must be non-negative.")
    if annual_net_savings_eur <= 0:
        return None
    return float(initial_capex_eur / annual_net_savings_eur)
