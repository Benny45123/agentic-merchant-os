import os
from functools import lru_cache
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./amos.db",
        description="Async database connection string"
    )

    # Razorpay Test Mode
    RAZORPAY_KEY_ID: str = Field(
        default="rzp_test_placeholder_key_id",
        description="Razorpay test key ID"
    )
    RAZORPAY_KEY_SECRET: str = Field(
        default="placeholder_secret_never_commit",
        description="Razorpay test key secret"
    )
    RAZORPAY_WEBHOOK_SECRET: str = Field(
        default="placeholder_webhook_secret",
        description="Razorpay webhook verification secret"
    )

    # LLM Configuration
    LLM_PROVIDER: Literal["gemini", "groq", "openrouter"] = Field(
        default="gemini",
        description="Active LLM provider"
    )
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Gemini API Key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-3.5-flash-lite",
        description="Gemini Model (e.g. gemini-3.5-flash-lite, gemini-2.5-flash)"
    )
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Groq API Key"
    )
    GROQ_MODEL: str = Field(
        default="qwen/qwen3.8-27b",
        description="Groq Model (e.g. qwen/qwen3.8-27b, llama-3.3-70b-versatile, llama-3.1-8b-instant)"
    )
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenRouter API Key"
    )
    OPENROUTER_MODEL: str = Field(
        default="meta-llama/llama-3.3-70b-instruct:free",
        description="OpenRouter Model (e.g. meta-llama/llama-3.3-70b-instruct:free, deepseek/deepseek-r1:free, qwen/qwen-2.5-72b-instruct:free)"
    )

    # Auth & Security
    JWT_SIGNING_KEY: str = Field(
        default="test_jwt_signing_key_for_local_development_must_override_in_env",
        description="Secret key for signing JWT session tokens"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400 * 7  # 7 days

    # Telegram Bot Gateway
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(
        default=None,
        description="Telegram Bot API Token from @BotFather"
    )
    MERCHANT_API_BASE: str = Field(
        default="http://localhost:8000",
        description="Base URL of the Agentic Merchant OS API"
    )

    # Environment
    ENV: Literal["local", "test", "production"] = Field(
        default="local",
        description="Deployment environment"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite://") and not v.startswith("sqlite+aiosqlite://"):
            return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return v

    def validate_llm_credentials(self) -> None:
        """Fails loudly if active LLM provider is missing its credentials."""
        if self.LLM_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        elif self.LLM_PROVIDER == "groq" and not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        elif self.LLM_PROVIDER == "openrouter" and not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter")


@lru_cache
def get_settings() -> Settings:
    return Settings()
