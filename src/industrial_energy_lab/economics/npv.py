"""Net present value calculations."""

from collections.abc import Iterable


def npv(initial_capex_eur: float, annual_cashflows_eur: Iterable[float], discount_rate: float) -> float:
    """Compute NPV with upfront CAPEX at t=0 and end-of-year cash flows.

    Positive cash flow means benefit to the project; positive NPV means benefits
    exceed the discounted upfront investment under the supplied assumptions.
    """

    if initial_capex_eur < 0:
        raise ValueError("Initial CAPEX must be non-negative.")
    if discount_rate <= -1:
        raise ValueError("Discount rate must be greater than -100%.")

    value = -float(initial_capex_eur)
    for year, cashflow in enumerate(annual_cashflows_eur, start=1):
        value += float(cashflow) / (1.0 + discount_rate) ** year
    return value
