"""POST /mentor — Create and AI-enrich a mentor."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import MentorCreate, MentorResponse
from app.services import postgres_service as pg, neo4j_service as neo4j
from app.services.gemini_service import GeminiService
from app.utils.logger import get_logger

router = APIRouter(prefix="/mentor", tags=["Mentors"])
logger = get_logger(__name__)
_gemini = GeminiService()


@router.post("", response_model=MentorResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a mentor and enrich their profile with AI")
async def create_mentor(payload: MentorCreate) -> MentorResponse:
    """
    1. Save raw mentor to PostgreSQL
    2. Call Gemini to enrich (normalize tags, improve bio)
    3. Update mentor with enriched data
    4. Sync mentor node to Neo4j
    """
    # Step 1: Create
    mentor = await pg.create_mentor(
        name=payload.name,
        expertise_tags=payload.expertise_tags or [],
        experience_years=payload.experience_years or 0,
        bio=payload.bio,
    )
    logger.info("mentor_created_raw", mentor_id=mentor.id)

    # Step 2: AI Enrichment
    enriched = await _gemini.enrich_mentor(
        name=mentor.name,
        expertise_tags=mentor.expertise_tags or [],
        experience_years=mentor.experience_years or 0,
        bio=mentor.bio,
    )

    # Step 3: Update
    await pg.update_mentor_enrichment(
        mentor_id=mentor.id,
        expertise_tags=enriched["expertise_tags"],
        clean_bio=enriched["clean_bio"],
    )

    # Step 4: Neo4j
    mentor_dict = await pg.get_mentor_by_id(mentor.id)
    if mentor_dict:
        await neo4j.upsert_mentor_node(mentor_dict)

    return MentorResponse(**mentor_dict) if mentor_dict else MentorResponse(
        id=mentor.id, name=mentor.name, expertise_tags=mentor.expertise_tags,
        experience_years=mentor.experience_years, bio=mentor.bio,
        clean_bio=None, rating=0.0, available=True, enriched_at=None, created_at=mentor.created_at,
    )


@router.get("s", response_model=list[MentorResponse], summary="List all available mentors")
async def list_mentors():
    mentors = await pg.get_all_mentors()
    return [MentorResponse(**m) for m in mentors]


@router.get("/{mentor_id}", response_model=MentorResponse, summary="Get mentor by ID")
async def get_mentor(mentor_id: int):
    mentor = await pg.get_mentor_by_id(mentor_id)
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor {mentor_id} not found")
    return MentorResponse(**mentor)
