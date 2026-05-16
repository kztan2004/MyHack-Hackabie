"""POST /startup — Create and AI-enrich a startup."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import StartupCreate, StartupResponse
from app.services import postgres_service as pg, neo4j_service as neo4j
from app.services.gemini_service import GeminiService
from app.utils.logger import get_logger

router = APIRouter(prefix="/startup", tags=["Startups"])
logger = get_logger(__name__)
_gemini = GeminiService()


@router.post("", response_model=StartupResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a startup and enrich its profile with AI")
async def create_startup(payload: StartupCreate) -> StartupResponse:
    """
    1. Save raw startup to PostgreSQL
    2. Call Gemini to enrich (normalize tags, improve description)
    3. Update startup with enriched data
    4. Sync startup node to Neo4j
    """
    # Step 1: Create in DB
    startup = await pg.create_startup(
        name=payload.name,
        industry=payload.industry,
        stage=payload.stage,
        description=payload.description,
    )
    logger.info("startup_created_raw", startup_id=startup.id)

    # Step 2: AI Enrichment
    enriched = await _gemini.enrich_startup(
        name=startup.name,
        industry=startup.industry,
        stage=startup.stage,
        description=startup.description,
    )

    # Step 3: Update with enriched data
    updated = await pg.update_startup_enrichment(
        startup_id=startup.id,
        industry=enriched["industry"],
        tags=enriched["tags"],
        clean_description=enriched["clean_description"],
        confidence=enriched["confidence"],
    )

    # Step 4: Sync to Neo4j
    startup_dict = await pg.get_startup_by_id(startup.id)
    if startup_dict:
        await neo4j.upsert_startup_node(startup_dict)

    return StartupResponse(**startup_dict) if startup_dict else StartupResponse(
        id=startup.id, name=startup.name, industry=startup.industry,
        stage=startup.stage, description=startup.description,
        tags=None, clean_description=None, ai_confidence=None,
        enriched_at=None, created_at=startup.created_at,
    )


@router.get("s", response_model=list[StartupResponse], summary="List all startups")
async def list_startups():
    startups = await pg.get_all_startups()
    return [StartupResponse(**s) for s in startups]


@router.get("/{startup_id}", response_model=StartupResponse, summary="Get startup by ID")
async def get_startup(startup_id: int):
    startup = await pg.get_startup_by_id(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail=f"Startup {startup_id} not found")
    return StartupResponse(**startup)
