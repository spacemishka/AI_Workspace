from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialRatiosResult:
    # Profitability Margins
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None

    # Returns
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None # Return on Invested Capital

    # Solvency & Liquidity
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None

    # Efficiency
    asset_turnover: Optional[float] = None


def safe_div(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den is None or den == 0:
        return None
    return num / den


def calculate_ratios(
    revenue: Optional[float] = None,
    gross_profit: Optional[float] = None,
    operating_income: Optional[float] = None,
    net_income: Optional[float] = None,
    operating_cash_flow: Optional[float] = None,
    capex: Optional[float] = None,
    total_assets: Optional[float] = None,
    total_liabilities: Optional[float] = None,
    total_equity: Optional[float] = None,
    total_debt: Optional[float] = None,
    cash_and_equivalents: Optional[float] = None,
    current_assets: Optional[float] = None,
    current_liabilities: Optional[float] = None,
    interest_expense: Optional[float] = None,
    effective_tax_rate: float = 0.21,
) -> FinancialRatiosResult:
    """Calculate standard financial ratios strictly deterministically."""
    
    # Calculate Free Cash Flow (FCF) = OCF - CapEx (capex usually reported positive or negative, handle absolute)
    fcf = None
    if operating_cash_flow is not None and capex is not None:
        fcf = operating_cash_flow - abs(capex)

    # Calculate NOPAT = Operating Income * (1 - Tax Rate)
    nopat = None
    if operating_income is not None:
        nopat = operating_income * (1.0 - effective_tax_rate)

    # Invested Capital = Total Equity + Total Debt - Cash
    invested_capital = None
    if total_equity is not None and total_debt is not None:
        cash_val = cash_and_equivalents if cash_and_equivalents is not None else 0.0
        invested_capital = (total_equity + total_debt) - cash_val

    # Quick Assets = Current Assets - Inventory (approximate as Current Assets - 0.3*Current Assets if inventory missing, or Current Assets directly)
    quick_assets = current_assets  # conservatively using current_assets if inventory line not specified

    return FinancialRatiosResult(
        gross_margin=safe_div(gross_profit, revenue),
        operating_margin=safe_div(operating_income, revenue),
        net_margin=safe_div(net_income, revenue),
        fcf_margin=safe_div(fcf, revenue),
        roe=safe_div(net_income, total_equity),
        roa=safe_div(net_income, total_assets),
        roic=safe_div(nopat, invested_capital),
        current_ratio=safe_div(current_assets, current_liabilities),
        quick_ratio=safe_div(quick_assets, current_liabilities),
        debt_to_equity=safe_div(total_debt, total_equity),
        interest_coverage=safe_div(operating_income, abs(interest_expense) if interest_expense else None),
        asset_turnover=safe_div(revenue, total_assets),
    )
