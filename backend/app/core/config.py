from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MYRantai"
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://ecosystem:ecosystem@localhost:5432/ecosystem_graph"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ecosystem_graph_password"
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.1-flash-lite-preview"

    jwt_secret: str = Field(default="change-me-before-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    admin_username: str = "admin"
    admin_password: str = "admin"
    disable_auth: bool = True

    # Comma-separated list of allowed CORS origins (read from CORS_ORIGINS env var).
    # Example: CORS_ORIGINS=https://my-app.vercel.app,http://localhost:3000
    # Stored as a plain str because pydantic-settings v2 cannot JSON-parse a
    # bare comma-separated string into list[str]. Use cors_origins_list property.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return cors_origins as a list, split on commas."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
