import json
from typing import AsyncGenerator
import httpx
from src.core.logging import get_logger
from src.providers.base import CompletionRequest, CompletionResponse, LLMProvider

logger = get_logger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        default_model: str = "llama3.1:8b",
        provider_name: str = "openai_compatible",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "not-needed"
        self.default_model = default_model
        self._provider_name = provider_name
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    @property
    def name(self) -> str:
        return self._provider_name

    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "messages": [msg.model_dump(exclude_none=True) for msg in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        logger.info(
            "Sending completion request",
            provider=self.name,
            model=model,
            message_count=len(request.messages),
        )

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})

        return CompletionResponse(
            content=content,
            model=model,
            provider=self.name,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
        )

    async def generate_stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "messages": [msg.model_dump(exclude_none=True) for msg in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        logger.info(
            "Sending streaming completion request",
            provider=self.name,
            model=model,
        )

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk_data = json.loads(data_str)
                    delta = chunk_data["choices"][0].get("delta", {})
                    content_chunk = delta.get("content", "")
                    if content_chunk:
                        yield content_chunk
                except json.JSONDecodeError:
                    continue
