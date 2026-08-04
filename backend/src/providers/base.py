from abc import ABC, abstractmethod
from typing import AsyncGenerator
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: str | None = None


class CompletionRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    stream: bool = False


class CompletionResponse(BaseModel):
    content: str
    model: str
    provider: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'ollama', 'openrouter', 'openai')."""
        pass

    @abstractmethod
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a complete chat response."""
        pass

    @abstractmethod
    async def generate_stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream a chat response token by token."""
        pass
