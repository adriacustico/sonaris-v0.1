"""Environment-driven backend settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "Sonaris API"
    database_url: str = "postgresql+psycopg2://sonaris:sonaris@db:5432/sonaris"
    cors_origins: list[str] = ["http://localhost:3000"]
    secret_key: str = "change-me-in-production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
