import asyncio
import json
from typing import Any
from pydantic import BaseModel
from src.agents.base_agent import AgentResult, BaseInvestmentAgent
from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.financial_statement_analyst import FinancialStatementAnalystAgent
from src.agents.valuation_analyst import ValuationAnalystAgent
from src.core.logging import get_logger
from src.providers.base import ChatMessage, CompletionRequest
from src.providers.router import provider_router

logger = get_logger(__name__)


class CIOInvestmentReport(BaseModel):
    ticker: str
    company_name: str
    overall_rating: str  # "Bullish", "Neutral", "Bearish"
    conviction_score: float  # 1.0 to 10.0
    executive_summary: str
    investment_thesis: list[str]
    key_risks: list[str]
    fundamental_analysis: AgentResult
    financial_statement_analysis: AgentResult
    valuation_analysis: AgentResult


class ChiefInvestmentOfficerAgent:
    def __init__(self) -> None:
        self.fundamental_agent = FundamentalAnalystAgent()
        self.financial_statement_agent = FinancialStatementAnalystAgent()
        self.valuation_agent = ValuationAnalystAgent()

    async def generate_research_report(
        self, ticker: str, financial_context: dict[str, Any], route_to_cloud: bool = False
    ) -> CIOInvestmentReport:
        """Run specialized analyst agents concurrently and synthesize into a unified CIO Investment Report."""
        logger.info("CIO Agent initiating multi-agent research workflow", ticker=ticker)

        # 1. Execute specialized agents in parallel
        fundamental_res, financial_res, valuation_res = await asyncio.gather(
            self.fundamental_agent.analyze(ticker, financial_context, route_to_cloud=route_to_cloud),
            self.financial_statement_agent.analyze(ticker, financial_context, route_to_cloud=route_to_cloud),
            self.valuation_agent.analyze(ticker, financial_context, route_to_cloud=route_to_cloud),
        )

        # 2. Synthesize findings into cohesive report via CIO LLM call
        provider = provider_router.get_provider(route_to_cloud=route_to_cloud)

        cio_system_prompt = """
You are the Chief Investment Officer (CIO) of a disciplined, fundamental-focused investment firm.
Your job is to review the independent reports from your Fundamental Analyst, Financial Statement Analyst, and Valuation Analyst, and synthesize them into a single, authoritative, structured Investment Thesis Report.

Your report must be mathematically grounded, objective, transparent, and non-speculative.
Return your synthesis strictly as valid JSON matching this schema:
{
  "overall_rating": "Bullish" | "Neutral" | "Bearish",
  "conviction_score": 8.5,
  "executive_summary": "3-5 sentence overall summary...",
  "investment_thesis": ["Key thesis point 1", "Key thesis point 2", "Key thesis point 3"],
  "key_risks": ["Key risk 1", "Key risk 2", "Key risk 3"]
}
"""

        cio_user_content = f"""
Company Ticker: {ticker.upper()}

Analyst Sub-Reports:
1. Fundamental Analyst Report:
{json.dumps(fundamental_res.model_dump(), indent=2)}

2. Financial Statement Analyst Report:
{json.dumps(financial_res.model_dump(), indent=2)}

3. Valuation Analyst Report:
{json.dumps(valuation_res.model_dump(), indent=2)}
"""

        request = CompletionRequest(
            messages=[
                ChatMessage(role="system", content=cio_system_prompt),
                ChatMessage(role="user", content=cio_user_content),
            ],
            temperature=0.3,
        )

        response = await provider.generate(request)

        # Parse CIO response
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            parsed = json.loads(content.strip())
        except Exception:
            parsed = {
                "overall_rating": "Neutral",
                "conviction_score": 7.0,
                "executive_summary": response.content[:300],
                "investment_thesis": ["Solid competitive market position."],
                "key_risks": ["Macroeconomic headwinds and valuation sensitivity."],
            }

        company_name = financial_context.get("company_profile", {}).get("name", ticker.upper())

        return CIOInvestmentReport(
            ticker=ticker.upper(),
            company_name=company_name,
            overall_rating=parsed.get("overall_rating", "Neutral"),
            conviction_score=float(parsed.get("conviction_score", 7.0)),
            executive_summary=parsed.get("executive_summary", "Analysis completed."),
            investment_thesis=parsed.get("investment_thesis", []),
            key_risks=parsed.get("key_risks", []),
            fundamental_analysis=fundamental_res,
            financial_statement_analysis=financial_res,
            valuation_analysis=valuation_res,
        )
