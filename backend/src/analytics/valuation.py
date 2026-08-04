from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DCFValuationResult:
    intrinsic_value_per_share: float
    equity_value: float
    enterprise_value: float
    present_value_fcf: float
    present_value_terminal_value: float
    wacc_used: float
    terminal_growth_rate_used: float
    projected_fcf: list[float] = field(default_factory=list)


def calculate_dcf(
    current_fcf: float,
    shares_outstanding: float,
    total_debt: float = 0.0,
    cash_and_equivalents: float = 0.0,
    growth_rate_5yr: float = 0.10,        # 10% expected annual FCF growth for 5 years
    terminal_growth_rate: float = 0.025,  # 2.5% perpetual growth rate
    discount_rate_wacc: float = 0.09,     # 9% WACC
    projection_years: int = 5,
) -> DCFValuationResult:
    """Calculate Discounted Cash Flow (DCF) intrinsic valuation."""
    if shares_outstanding <= 0:
        raise ValueError("Shares outstanding must be positive")

    # 1. Project future Free Cash Flows
    projected_fcf: list[float] = []
    fcf = current_fcf
    for _ in range(projection_years):
        fcf *= (1.0 + growth_rate_5yr)
        projected_fcf.append(fcf)

    # 2. Discount projected FCFs to Present Value
    pv_fcf = 0.0
    for year, fcf_val in enumerate(projected_fcf, start=1):
        pv_fcf += fcf_val / ((1.0 + discount_rate_wacc) ** year)

    # 3. Calculate Terminal Value using Gordon Growth Model
    terminal_fcf = projected_fcf[-1] * (1.0 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate_wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1.0 + discount_rate_wacc) ** projection_years)

    # 4. Enterprise Value & Equity Value
    enterprise_value = pv_fcf + pv_terminal_value
    equity_value = enterprise_value + cash_and_equivalents - total_debt
    intrinsic_value_per_share = max(0.0, equity_value / shares_outstanding)

    return DCFValuationResult(
        intrinsic_value_per_share=round(intrinsic_value_per_share, 2),
        equity_value=round(equity_value, 2),
        enterprise_value=round(enterprise_value, 2),
        present_value_fcf=round(pv_fcf, 2),
        present_value_terminal_value=round(pv_terminal_value, 2),
        wacc_used=discount_rate_wacc,
        terminal_growth_rate_used=terminal_growth_rate,
        projected_fcf=[round(f, 2) for f in projected_fcf],
    )
