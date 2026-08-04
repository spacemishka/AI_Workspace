from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from src.analytics import (
    calculate_ratios,
    calculate_piotroski_f_score,
    calculate_altman_z_score,
    calculate_beneish_m_score,
    calculate_dcf,
)
from src.services.financial_data.yfinance_provider import YFinanceProvider

router = APIRouter(prefix="/financials", tags=["Financial Analytics"])
provider = YFinanceProvider()


class CompanyAnalysisResponse(BaseModel):
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    ratios: dict
    piotroski_score: Optional[int] = None
    altman_z_score: Optional[float] = None
    altman_z_zone: Optional[str] = None
    dcf_intrinsic_value: Optional[float] = None


@router.get("/{ticker}/profile")
async def get_company_profile(ticker: str):
    """Fetch company profile and high-level metadata."""
    try:
        profile = await provider.get_company_profile(ticker)
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch profile for {ticker}: {str(e)}")


@router.get("/{ticker}/analysis", response_model=CompanyAnalysisResponse)
async def analyze_company(
    ticker: str,
    wacc: float = Query(0.09, ge=0.01, le=0.30, description="Discount rate (WACC)"),
    growth_rate: float = Query(0.10, ge=-0.50, le=1.00, description="5-year expected FCF growth rate"),
):
    """Run full deterministic financial analytics (ratios, Piotroski F-Score, Altman Z-Score, DCF valuation)."""
    try:
        profile = await provider.get_company_profile(ticker)
        statements = await provider.get_financial_statements(ticker)

        # Extract latest income statement & balance sheet metrics if available
        inc = statements.income_statement
        bal = statements.balance_sheet
        cf = statements.cash_flow

        # Get latest available date column
        latest_date = next(iter(inc.keys())) if inc else None
        
        rev = float(inc.get(latest_date, {}).get("Total Revenue", 0) or 0) if latest_date else 0
        gp = float(inc.get(latest_date, {}).get("Gross Profit", 0) or 0) if latest_date else 0
        ebit = float(inc.get(latest_date, {}).get("EBIT", 0) or 0) if latest_date else 0
        net_inc = float(inc.get(latest_date, {}).get("Net Income", 0) or 0) if latest_date else 0
        ocf = float(cf.get(latest_date, {}).get("Operating Cash Flow", 0) or 0) if latest_date else 0
        capex = float(cf.get(latest_date, {}).get("Capital Expenditure", 0) or 0) if latest_date else 0

        total_assets = float(bal.get(latest_date, {}).get("Total Assets", 0) or 0) if latest_date else 0
        total_liab = float(bal.get(latest_date, {}).get("Total Liabilities Net Minority Interest", 0) or 0) if latest_date else 0
        total_equity = float(bal.get(latest_date, {}).get("Stockholders Equity", 0) or 0) if latest_date else 0
        total_debt = float(bal.get(latest_date, {}).get("Total Debt", 0) or 0) if latest_date else 0
        cash = float(bal.get(latest_date, {}).get("Cash And Cash Equivalents", 0) or 0) if latest_date else 0
        curr_assets = float(bal.get(latest_date, {}).get("Current Assets", 0) or 0) if latest_date else 0
        curr_liab = float(bal.get(latest_date, {}).get("Current Liabilities", 0) or 0) if latest_date else 0

        # Calculate Ratios
        ratios_res = calculate_ratios(
            revenue=rev if rev > 0 else None,
            gross_profit=gp if gp > 0 else None,
            operating_income=ebit if ebit > 0 else None,
            net_income=net_inc if net_inc != 0 else None,
            operating_cash_flow=ocf if ocf != 0 else None,
            capex=capex if capex != 0 else None,
            total_assets=total_assets if total_assets > 0 else None,
            total_equity=total_equity if total_equity > 0 else None,
            total_debt=total_debt if total_debt > 0 else None,
            cash_and_equivalents=cash if cash > 0 else None,
            current_assets=curr_assets if curr_assets > 0 else None,
            current_liabilities=curr_liab if curr_liab > 0 else None,
        )

        # Calculate Altman Z-Score if assets available
        z_res = None
        if total_assets > 0 and total_liab > 0:
            wc = curr_assets - curr_liab
            retained_earn = float(bal.get(latest_date, {}).get("Retained Earnings", 0) or 0) if latest_date else 0
            mcap = profile.market_cap or (total_equity * 1.5)
            z_res = calculate_altman_z_score(
                working_capital=wc,
                retained_earnings=retained_earn,
                ebit=ebit,
                market_cap=mcap,
                revenue=rev,
                total_assets=total_assets,
                total_liabilities=total_liab,
            )

        # Calculate DCF Valuation if FCF available
        dcf_val = None
        fcf = ocf - abs(capex)
        if fcf > 0 and profile.market_cap and profile.pe_ratio:
            # Estimate shares
            shares = profile.market_cap / (rev / (profile.pe_ratio or 15)) if rev > 0 else 1e8
            try:
                dcf_res = calculate_dcf(
                    current_fcf=fcf,
                    shares_outstanding=shares,
                    total_debt=total_debt,
                    cash_and_equivalents=cash,
                    growth_rate_5yr=growth_rate,
                    discount_rate_wacc=wacc,
                )
                dcf_val = dcf_res.intrinsic_value_per_share
            except Exception:
                dcf_val = None

        return CompanyAnalysisResponse(
            ticker=ticker.upper(),
            company_name=profile.name,
            sector=profile.sector,
            industry=profile.industry,
            market_cap=profile.market_cap,
            pe_ratio=profile.pe_ratio,
            ratios=ratios_res.__dict__,
            altman_z_score=z_res.score if z_res else None,
            altman_z_zone=z_res.zone if z_res else None,
            dcf_intrinsic_value=dcf_val,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing {ticker}: {str(e)}")
