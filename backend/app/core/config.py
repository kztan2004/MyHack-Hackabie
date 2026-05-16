from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "EcosystemGraph AI"
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://ecosystem:ecosystem@localhost:5432/ecosystem_graph"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ecosystem_graph_password"
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    jwt_secret: str = Field(default="change-me-before-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    admin_username: str = "admin"
    admin_password: str = "admin"
    disable_auth: bool = True

    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
