from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.providers.base import CompletionRequest
from src.providers.router import provider_router

setup_logging()
logger = get_logger(__name__)


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


@app.post("/v1/chat", tags=["AI"])
async def chat_completion(request: CompletionRequest, cloud: bool = False):
    provider = provider_router.get_provider(route_to_cloud=cloud)
    try:
        if request.stream:
            async def event_generator():
                async for chunk in provider.generate_stream(request):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        response = await provider.generate(request)
        return response
    except Exception as e:
        logger.error("Chat completion failed", error=str(e), provider=provider.name)
        raise HTTPException(status_code=500, detail=str(e))
