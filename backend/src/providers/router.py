from src.core.config import settings
from src.core.logging import get_logger
from src.providers.base import LLMProvider
from src.providers.openai_compatible import OpenAICompatibleProvider

logger = get_logger(__name__)


class ProviderRouter:
    def __init__(self) -> None:
        # Local provider
        self.local_provider = OpenAICompatibleProvider(
            base_url=settings.LOCAL_INFERENCE_BASE_URL,
            default_model=settings.OLLAMA_DEFAULT_MODEL,
            provider_name="local",
        )

        # Cloud provider (e.g. OpenRouter)
        self.cloud_provider = OpenAICompatibleProvider(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            default_model=settings.OPENROUTER_DEFAULT_MODEL,
            provider_name=settings.CLOUD_PROVIDER,
        )

    def get_provider(self, route_to_cloud: bool = False) -> LLMProvider:
        """Select provider based on task routing decision."""
        if route_to_cloud:
            if not settings.OPENROUTER_API_KEY:
                logger.warning("Cloud provider requested but API key is missing, falling back to local")
                return self.local_provider
            return self.cloud_provider
        return self.local_provider


provider_router = ProviderRouter()
