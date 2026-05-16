from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini import GeminiService
from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.graph.neo4j_service import Neo4jService
from app.repositories.ecosystem import EcosystemRepository
from app.services.embedding_service import EmbeddingService
from app.services.profile_service import ProfileAIService, ShortBioService, SkillExtractionService


def get_gemini(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(settings)


def get_skill_service(gemini: GeminiService = Depends(get_gemini)) -> SkillExtractionService:
    return SkillExtractionService(gemini)


def get_short_bio_service(gemini: GeminiService = Depends(get_gemini)) -> ShortBioService:
    return ShortBioService(gemini)


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_profile_ai_service(
    skill_service: SkillExtractionService = Depends(get_skill_service),
    short_bio_service: ShortBioService = Depends(get_short_bio_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileAIService:
    return ProfileAIService(skill_service, short_bio_service, embedding_service)


async def get_repository(
    session: AsyncSession = Depends(get_session),
    skill_service: SkillExtractionService = Depends(get_skill_service),
) -> AsyncIterator[EcosystemRepository]:
    yield EcosystemRepository(session, skill_service)


def get_graph_service(request: Request) -> Neo4jService | None:
    return getattr(request.app.state, "graph", None)
