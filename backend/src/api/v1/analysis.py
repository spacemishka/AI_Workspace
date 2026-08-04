from fastapi import APIRouter, HTTPException, Query
from src.agents import ChiefInvestmentOfficerAgent, CIOInvestmentReport
from src.analytics import calculate_ratios, calculate_altman_z_score, calculate_dcf
from src.services.financial_data.yfinance_provider import YFinanceProvider

router = APIRouter(prefix="/analysis", tags=["Multi-Agent Research"])
provider = YFinanceProvider()
cio_agent = ChiefInvestmentOfficerAgent()


@router.post("/company/{ticker}", response_model=CIOInvestmentReport)
async def generate_company_research_report(
    ticker: str,
    cloud: bool = Query(False, description="Outsource complex agent reasoning to cloud model (e.g. OpenRouter)"),
):
    """Trigger multi-agent fundamental research workflow on a company ticker."""
    try:
        profile = await provider.get_company_profile(ticker)
        statements = await provider.get_financial_statements(ticker)

        # Assemble rich context dictionary for agents
        context = {
            "company_profile": profile.__dict__,
            "financial_statements": {
                "income_statement": statements.income_statement,
                "balance_sheet": statements.balance_sheet,
                "cash_flow": statements.cash_flow,
            },
        }

        # Run CIO orchestrator workflow
        report = await cio_agent.generate_research_report(ticker, context, route_to_cloud=cloud)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate research report for {ticker}: {str(e)}")
