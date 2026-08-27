"""Transparent cash-flow helpers."""

from collections.abc import Iterable


def capital_recovery_factor(discount_rate: float, years: int) -> float:
    """Return the standard capital recovery factor (CRF)."""

    if years <= 0:
        raise ValueError("years must be positive")
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -100%")
    if discount_rate == 0:
        return 1.0 / years
    r = discount_rate
    return r * (1 + r) ** years / ((1 + r) ** years - 1)


def annualized_capex(capex_eur: float, discount_rate: float, years: int) -> float:
    """Convert a non-negative upfront CAPEX into equivalent annual cost."""

    if capex_eur < 0:
        raise ValueError("CAPEX must be non-negative")
    return capex_eur * capital_recovery_factor(discount_rate, years)


def uniform_annual_cashflows(amount_eur: float, years: int) -> list[float]:
    """Create a repeated end-of-year cash-flow vector."""

    if years <= 0:
        raise ValueError("years must be positive")
    return [float(amount_eur)] * years


def total_undiscounted(cashflows_eur: Iterable[float]) -> float:
    return float(sum(cashflows_eur))
