"""PostgreSQL Service — CRUD operations for EcosystemGraph AI."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings
from app.models.postgres import Base, Startup, Mentor, MatchLog, Feedback
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=(settings.app_env == "development"),
    pool_size=10, max_overflow=20, pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("postgres_tables_ready")


async def check_health() -> str:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return "healthy"
    except Exception as exc:
        logger.error("postgres_health_failed", error=str(exc))
        return f"unhealthy: {exc}"


# ─── Startup CRUD ─────────────────────────────────────────────────────────────

async def create_startup(
    name: str, industry: Optional[str], stage: Optional[str], description: Optional[str]
) -> Startup:
    async with AsyncSessionLocal() as session:
        startup = Startup(name=name, industry=industry, stage=stage, description=description)
        session.add(startup)
        await session.commit()
        await session.refresh(startup)
        logger.info("startup_created", startup_id=startup.id, name=name)
        return startup


async def update_startup_enrichment(
    startup_id: int,
    industry: str,
    tags: List[str],
    clean_description: str,
    confidence: float,
) -> Optional[Startup]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Startup).where(Startup.id == startup_id))
        startup = result.scalar_one_or_none()
        if not startup:
            return None
        startup.industry = industry
        startup.tags = tags
        startup.clean_description = clean_description
        startup.ai_confidence = confidence
        startup.enriched_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(startup)
        logger.info("startup_enriched", startup_id=startup_id)
        return startup


async def get_startup_by_id(startup_id: int) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Startup).where(Startup.id == startup_id))
        s = result.scalar_one_or_none()
        if not s:
            return None
        return _startup_to_dict(s)


async def get_all_startups() -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Startup).order_by(Startup.created_at.desc()))
        return [_startup_to_dict(s) for s in result.scalars().all()]


def _startup_to_dict(s: Startup) -> Dict[str, Any]:
    return {
        "id": s.id,
        "name": s.name,
        "industry": s.industry,
        "stage": s.stage,
        "description": s.description,
        "tags": s.tags or [],
        "clean_description": s.clean_description,
        "ai_confidence": float(s.ai_confidence) if s.ai_confidence else 0.0,
        "enriched_at": s.enriched_at,
        "created_at": s.created_at,
    }


# ─── Mentor CRUD ──────────────────────────────────────────────────────────────

async def create_mentor(
    name: str, expertise_tags: List[str], experience_years: int, bio: Optional[str]
) -> Mentor:
    async with AsyncSessionLocal() as session:
        mentor = Mentor(name=name, expertise_tags=expertise_tags, experience_years=experience_years, bio=bio)
        session.add(mentor)
        await session.commit()
        await session.refresh(mentor)
        logger.info("mentor_created", mentor_id=mentor.id, name=name)
        return mentor


async def update_mentor_enrichment(
    mentor_id: int, expertise_tags: List[str], clean_bio: str,
) -> Optional[Mentor]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Mentor).where(Mentor.id == mentor_id))
        mentor = result.scalar_one_or_none()
        if not mentor:
            return None
        mentor.expertise_tags = expertise_tags
        mentor.clean_bio = clean_bio
        mentor.enriched_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(mentor)
        return mentor


async def get_mentor_by_id(mentor_id: int) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Mentor).where(Mentor.id == mentor_id))
        m = result.scalar_one_or_none()
        return _mentor_to_dict(m) if m else None


async def get_all_mentors() -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Mentor).where(Mentor.available == True).order_by(Mentor.created_at.desc())
        )
        return [_mentor_to_dict(m) for m in result.scalars().all()]


def _mentor_to_dict(m: Mentor) -> Dict[str, Any]:
    return {
        "id": m.id,
        "name": m.name,
        "expertise_tags": m.expertise_tags or [],
        "experience_years": m.experience_years,
        "bio": m.bio,
        "clean_bio": m.clean_bio,
        "rating": float(m.rating) if m.rating else 0.0,
        "available": m.available,
        "enriched_at": m.enriched_at,
        "created_at": m.created_at,
    }


# ─── Match Logging ────────────────────────────────────────────────────────────

async def log_match(startup_id: int, mentor_id: int, score: float, reason: str) -> MatchLog:
    async with AsyncSessionLocal() as session:
        log = MatchLog(startup_id=startup_id, mentor_id=mentor_id, score=score, reason=reason, status="pending")
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log


async def update_match_status(startup_id: int, mentor_id: int, status: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(MatchLog)
            .where(MatchLog.startup_id == startup_id, MatchLog.mentor_id == mentor_id)
            .values(status=status)
        )
        await session.commit()


# ─── Feedback ─────────────────────────────────────────────────────────────────

async def store_feedback(startup_id: int, mentor_id: int, action: str, comments: Optional[str]) -> None:
    async with AsyncSessionLocal() as session:
        session.add(Feedback(startup_id=startup_id, mentor_id=mentor_id, action=action, comments=comments))
        await session.commit()
    logger.info("feedback_stored", startup_id=startup_id, mentor_id=mentor_id, action=action)
