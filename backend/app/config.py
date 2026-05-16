"""Application configuration — reads from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-3-flash-preview"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://ecosystem_user:ecosystem_pass@localhost:5433/ecosystem_db"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7688"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ecosystem_graph_pass"

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    top_k_matches: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
