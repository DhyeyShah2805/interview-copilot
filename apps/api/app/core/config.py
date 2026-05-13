"""
Application settings loaded from environment variables.

Uses pydantic-settings to validate types at startup — if a required env var is
missing or malformed, the app fails fast instead of breaking at runtime.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Interview Copilot API"
    environment: str = Field(default="development")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://copilot:copilot_dev_password@localhost:5432/interview_copilot"
    )

    # Auth
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 60 * 24  # 1 day
    refresh_token_expire_days: int = 30
    algorithm: str = "HS256"

    # AI providers
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")

    # CORS — comma-separated origins in env, e.g. "http://localhost:3000,https://app.example.com"
    cors_origins_raw: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
