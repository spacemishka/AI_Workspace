from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # Database & Cache
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://aiworkspace:change_me_strong_password@localhost:5432/aiworkspace"
    )
    REDIS_URL: str = Field(default="redis://:change_me_redis_password@localhost:6379/0")

    # Vector Database
    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_API_KEY: str | None = Field(default=None)

    # Local Inference
    LOCAL_INFERENCE_BASE_URL: str = Field(default="http://localhost:11434/v1")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_DEFAULT_MODEL: str = Field(default="llama3.1:8b")
    OLLAMA_EMBED_MODEL: str = Field(default="nomic-embed-text")

    # Cloud Provider (OpenRouter / Pluggable)
    CLOUD_PROVIDER: str = Field(default="openrouter")
    OPENROUTER_API_KEY: str | None = Field(default=None)
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")
    OPENROUTER_DEFAULT_MODEL: str = Field(default="anthropic/claude-3.5-sonnet")

    # Security
    JWT_SECRET_KEY: str = Field(default="change_me_generate_a_strong_random_key")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=60)

    # Observability
    LANGFUSE_HOST: str = Field(default="http://localhost:3000")
    LANGFUSE_PUBLIC_KEY: str | None = Field(default=None)
    LANGFUSE_SECRET_KEY: str | None = Field(default=None)


settings = Settings()
