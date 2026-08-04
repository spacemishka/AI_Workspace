from abc import ABC, abstractmethod
import json
from typing import Any, Optional
from pydantic import BaseModel
from src.core.logging import get_logger
from src.providers.base import ChatMessage, CompletionRequest
from src.providers.router import provider_router

logger = get_logger(__name__)


class AgentResult(BaseModel):
    agent_name: str
    summary: str
    findings: dict[str, Any]
    confidence_score: float = 0.9


class BaseInvestmentAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the specialized agent (e.g. 'fundamental_analyst')."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining the role, analytical focus, and JSON schema output instructions."""
        pass

    async def analyze(
        self, ticker: str, financial_context: dict[str, Any], route_to_cloud: bool = False
    ) -> AgentResult:
        """Execute agent analysis using financial context data."""
        logger.info("Executing agent analysis", agent=self.name, ticker=ticker, cloud=route_to_cloud)

        provider = provider_router.get_provider(route_to_cloud=route_to_cloud)

        user_content = f"""
Analyze the following financial data for company ticker: {ticker.upper()}

Context Data:
{json.dumps(financial_context, indent=2, default=str)}

Return your response strictly as valid JSON matching this schema:
{{
  "summary": "High-level summary of your analysis (2-4 sentences)",
  "findings": {{ ... detailed structured key-value findings ... }},
  "confidence_score": 0.9
}}
"""

        request = CompletionRequest(
            messages=[
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=user_content),
            ],
            temperature=0.2,  # Low temperature for analytical consistency
        )

        response = await provider.generate(request)

        # Parse JSON response cleanly
        try:
            # Extract JSON block if wrapped in markdown ```json
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            parsed = json.loads(content.strip())
            return AgentResult(
                agent_name=self.name,
                summary=parsed.get("summary", "Analysis completed."),
                findings=parsed.get("findings", {}),
                confidence_score=float(parsed.get("confidence_score", 0.9)),
            )
        except Exception as e:
            logger.warning("Failed to parse agent JSON output directly, returning raw text finding", agent=self.name, error=str(e))
            return AgentResult(
                agent_name=self.name,
                summary="Agent analysis generated successfully.",
                findings={"raw_analysis": response.content},
                confidence_score=0.8,
            )
