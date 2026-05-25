from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = (
        "postgresql+asyncpg://library_user:library_pass@localhost:5432/library_db"
    )
    fine_per_day: float = 0.50
    loan_period_days: int = 14
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000


settings = Settings()
