from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = "Private Medical Center CRM"
    environment: str = Field(default="development", alias="APP_ENVIRONMENT")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    database_url: str = Field(
        default="postgresql+asyncpg://pmc_user:pmc_password@localhost:5432/pmc_crm",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    secret_key: str = Field(
        default="replace-me-with-a-long-random-secret",
        alias="APP_SECRET_KEY",
    )
    encryption_key: str = Field(alias="APP_ENCRYPTION_KEY")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        alias="APP_CORS_ORIGINS",
    )
    secure_cookies: bool = Field(default=False, alias="APP_SECURE_COOKIES")
    seed_demo_data: bool = Field(default=False, alias="APP_SEED_DEMO_DATA")
    sqlalchemy_echo: bool = False
    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    csrf_cookie_name: str = "csrf_token"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    admin_idle_timeout_minutes: int = 30
    default_slot_minutes: int = 30
    reminder_window_minutes: int = 60
    reminder_horizon_hours: int = 24
    request_id_header: str = "X-Request-ID"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
