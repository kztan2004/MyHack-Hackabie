"""POST /match/{startup_id} — AI-powered mentor matching."""
from __future__ import annotations
import asyncio
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import MatchResponse, MatchResult
from app.services import postgres_service as pg, neo4j_service as neo4j
from app.services.gemini_service import GeminiService
from app.services import matching_engine as engine
from app.config import get_settings
from app.utils.logger import get_logger

router = APIRouter(prefix="/match", tags=["Matching"])
logger = get_logger(__name__)
settings = get_settings()
_gemini = GeminiService()


@router.post("/{startup_id}", response_model=MatchResponse, status_code=status.HTTP_200_OK,
             summary="Generate AI-powered mentor matches for a startup")
async def match_startup(startup_id: int) -> MatchResponse:
    """
    Full matching pipeline:
    1. Load startup from PostgreSQL
    2. Load all available mentors
    3. Sync nodes to Neo4j
    4. Gemini ranks top-3 mentors
    5. Apply experience bonus (matching engine)
    6. Store MATCHED_WITH relationships in Neo4j
    7. Log matches in PostgreSQL
    8. Return results with AI explanations
    """
    # Step 1: Load startup
    startup = await pg.get_startup_by_id(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail=f"Startup {startup_id} not found")

    # Step 2: Load mentors
    mentors = await pg.get_all_mentors()
    if not mentors:
        raise HTTPException(status_code=404, detail="No mentors available in the system")

    # Step 3: Sync to Neo4j
    await neo4j.upsert_startup_node(startup)
    await neo4j.upsert_mentor_nodes(mentors)

    # Step 4: Gemini AI matching
    ai_matches = await _gemini.match_startup_to_mentors(
        startup=startup,
        mentors=mentors,
        top_k=settings.top_k_matches,
    )

    if not ai_matches:
        raise HTTPException(status_code=422, detail="AI could not generate matches. Please try again.")

    # Step 5: Apply experience bonus
    mentors_by_id = {m["id"]: m for m in mentors}
    ranked = engine.apply_experience_bonus(ai_matches, mentors_by_id)

    # Step 6 & 7: Store in Neo4j + PostgreSQL (parallel)
    neo4j_tasks = [
        neo4j.store_match_relationship(startup_id, m["mentor_id"], m["score"], m["reason"])
        for m in ranked
    ]
    pg_tasks = [
        pg.log_match(startup_id, m["mentor_id"], m["score"], m["reason"])
        for m in ranked
    ]
    await asyncio.gather(*neo4j_tasks, *pg_tasks)

    logger.info("matching_complete", startup_id=startup_id, match_count=len(ranked))

    return MatchResponse(
        startup_id=startup_id,
        startup_name=startup["name"],
        matches=[
            MatchResult(
                mentor_id=m["mentor_id"],
                mentor_name=m["mentor_name"],
                score=m["score"],
                reason=m["reason"],
                expertise_tags=m["expertise_tags"],
                experience_years=m["experience_years"],
            )
            for m in ranked
        ],
    )
