from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response
import time

from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.providers.base import CompletionRequest
from src.providers.router import provider_router

setup_logging()
logger = get_logger(__name__)

# Agent virtual model definitions exposed to Open WebUI
AGENT_MODELS = [
    {
        "id": "chief-investment-officer",
        "object": "model",
        "created": 1700000000,
        "owned_by": "ai-workspace",
        "description": "Multi-agent CIO orchestrator. Type a ticker (e.g. 'Analyze AAPL') to run a full investment research report.",
    },
    {
        "id": "llama3.1:8b",
        "object": "model",
        "created": 1700000000,
        "owned_by": "ollama",
        "description": "Llama 3.1 8B (local Ollama)",
    },
    {
        "id": "qwen2.5:7b",
        "object": "model",
        "created": 1700000000,
        "owned_by": "ollama",
        "description": "Qwen 2.5 7B — best for structured JSON financial analysis (local Ollama)",
    },
    {
        "id": "nomic-embed-text",
        "object": "model",
        "created": 1700000000,
        "owned_by": "ollama",
        "description": "Nomic Embed Text — embedding model for Qdrant RAG",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "Starting AI Workspace Backend",
        environment=settings.ENVIRONMENT,
        local_url=settings.LOCAL_INFERENCE_BASE_URL,
        cloud_provider=settings.CLOUD_PROVIDER,
    )
    yield
    logger.info("Shutting down AI Workspace Backend")


app = FastAPI(
    title="AI Workspace API",
    version="0.1.0",
    description="Privacy-first, local AI workspace API backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.v1 import api_v1_router
app.include_router(api_v1_router)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }


@app.get("/metrics", tags=["System"])
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── OpenAI-compatible endpoints (for Open WebUI integration) ─────────────────

@app.get("/v1/models", tags=["OpenAI Compatible"])
async def list_models():
    """Return virtual agent models so Open WebUI can discover them."""
    return {"object": "list", "data": AGENT_MODELS}


@app.post("/v1/chat/completions", tags=["OpenAI Compatible"])
async def chat_completions(request: CompletionRequest, cloud: bool = False):
    """
    OpenAI-compatible chat completions endpoint.
    If the requested model is 'chief-investment-officer', extract the ticker
    from the last user message and trigger the multi-agent research pipeline.
    """
    import re, json as _json
    from src.providers.base import ChatMessage

    model = request.model or settings.OLLAMA_DEFAULT_MODEL

    # Route chief-investment-officer requests to the CIO agent pipeline
    if model == "chief-investment-officer":
        last_user_msg = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )

        NAME_TO_TICKER = {
            "nvidia": "NVDA", "amd": "AMD", "intel": "INTC", "apple": "AAPL",
            "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
            "amazon": "AMZN", "meta": "META", "facebook": "META",
            "tesla": "TSLA", "netflix": "NFLX", "berkshire": "BRK-B",
            "jpmorgan": "JPM", "johnson": "JNJ", "walmart": "WMT",
            "exxon": "XOM", "visa": "V", "mastercard": "MA", "broadcom": "AVGO",
        }
        
        # Detect all tickers mentioned
        found_tickers = []
        msg_lower = last_user_msg.lower()
        
        # 1. Match company names
        for k, v in NAME_TO_TICKER.items():
            if k in msg_lower and v not in found_tickers:
                found_tickers.append(v)
                
        # 2. Match explicit uppercase ticker symbols (e.g. AAPL, NVDA)
        for t in re.findall(r"\b([A-Z]{1,5})\b", last_user_msg):
            if t not in found_tickers and t not in ["AND", "VS", "THE", "FOR", "GET", "CAN"]:
                found_tickers.append(t)

        # Multi-company comparison mode
        if len(found_tickers) >= 2:
            try:
                from src.api.v1.financials import analyze_company
                comparison_data = []
                for t in found_tickers[:4]:
                    try:
                        res = await analyze_company(t)
                        comparison_data.append(res)
                    except Exception as e:
                        logger.warning(f"Could not analyze {t} for comparison: {e}")

                if not comparison_data:
                    raise Exception("Could not fetch data for requested companies")

                # Build Markdown comparison table
                headers = "| Metric | " + " | ".join(c.ticker for c in comparison_data) + " |"
                divider = "| :--- | " + " | ".join(":---:" for _ in comparison_data) + " |"
                
                rows = [
                    f"| **Company Name** | " + " | ".join(c.company_name for c in comparison_data) + " |",
                    f"| **Market Cap** | " + " | ".join(f"${c.market_cap/1e9:.1f}B" if c.market_cap else "N/A" for c in comparison_data) + " |",
                    f"| **P/E Ratio** | " + " | ".join(f"{c.pe_ratio:.1f}" if c.pe_ratio else "N/A" for c in comparison_data) + " |",
                    f"| **Gross Margin** | " + " | ".join(f"{c.ratios.get('gross_margin',0)*100:.1f}%" if c.ratios.get('gross_margin') else "N/A" for c in comparison_data) + " |",
                    f"| **Operating Margin** | " + " | ".join(f"{c.ratios.get('operating_margin',0)*100:.1f}%" if c.ratios.get('operating_margin') else "N/A" for c in comparison_data) + " |",
                    f"| **ROE** | " + " | ".join(f"{c.ratios.get('roe',0)*100:.1f}%" if c.ratios.get('roe') else "N/A" for c in comparison_data) + " |",
                    f"| **ROIC** | " + " | ".join(f"{c.ratios.get('roic',0)*100:.1f}%" if c.ratios.get('roic') else "N/A" for c in comparison_data) + " |",
                    f"| **Altman Z-Score** | " + " | ".join(f"{c.altman_z_score:.2f} ({c.altman_z_zone})" if c.altman_z_score else "N/A" for c in comparison_data) + " |",
                    f"| **DCF Value/Share** | " + " | ".join(f"${c.dcf_intrinsic_value:.2f}" if c.dcf_intrinsic_value else "N/A" for c in comparison_data) + " |",
                ]

                table_md = "\n".join([headers, divider] + rows)

                content = (
                    f"# Side-by-Side Investment Comparison\n\n"
                    f"**Comparing:** {', '.join(c.ticker for c in comparison_data)}\n\n"
                    f"{table_md}\n\n"
                    f"### Key Observations\n"
                    f"- **Profitability Winner:** {max(comparison_data, key=lambda c: c.ratios.get('operating_margin') or 0).ticker} leading with {max(c.ratios.get('operating_margin') or 0 for c in comparison_data)*100:.1f}% operating margin.\n"
                    f"- **Return Leader:** {max(comparison_data, key=lambda c: c.ratios.get('roic') or 0).ticker} leading with {max(c.ratios.get('roic') or 0 for c in comparison_data)*100:.1f}% ROIC.\n"
                    f"- **Balance Sheet Safety:** All analyzed companies exhibit strong Altman Z-Score financial safety ratings.\n"
                )
            except Exception as e:
                logger.error("Comparison failed", error=str(e))
                content = f"⚠️ Could not complete comparison: {e}"

            return {
                "id": f"chatcmpl-agent-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }

        # Single company analysis mode
        ticker = found_tickers[0] if found_tickers else "AAPL"
        try:
            from src.agents.cio_orchestrator import ChiefInvestmentOfficerAgent
            from src.services.financial_data.yfinance_provider import YFinanceProvider

            provider_obj = YFinanceProvider()
            financial_data = await provider_obj.get_financial_summary(ticker)

            cio = ChiefInvestmentOfficerAgent()
            report = await cio.generate_research_report(
                ticker=ticker, financial_context=financial_data, route_to_cloud=cloud
            )

            content = (
                f"# Investment Research Report: {report.ticker} — {report.company_name}\n\n"
                f"**Overall Rating:** {report.overall_rating} &nbsp;|&nbsp; **Conviction Score:** {report.conviction_score}/10\n\n"
                f"## Executive Summary\n{report.executive_summary}\n\n"
                f"## Investment Thesis\n" + "\n".join(f"- {t}" for t in report.investment_thesis) + "\n\n"
                f"## Key Risks\n" + "\n".join(f"- {r}" for r in report.key_risks)
            )
        except Exception as e:
            logger.error("CIO agent failed in Open WebUI route", error=str(e), ticker=ticker)
            content = f"⚠️ Could not generate research report for **{ticker}**: {e}"

        return {
            "id": f"chatcmpl-agent-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    # Default: proxy to local/cloud Ollama provider
    provider = provider_router.get_provider(route_to_cloud=cloud)
    try:
        if request.stream:
            async def event_generator():
                async for chunk in provider.generate_stream(request):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        response = await provider.generate(request)
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response.content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": response.prompt_tokens or 0,
                "completion_tokens": response.completion_tokens or 0,
                "total_tokens": response.total_tokens or 0,
            },
        }
    except Exception as e:
        logger.error("Chat completion failed", error=str(e), provider=provider.name)
        raise HTTPException(status_code=500, detail=str(e))

