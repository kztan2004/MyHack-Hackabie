"""POST /feedback — Accept or reject a match."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.services import postgres_service as pg, neo4j_service as neo4j
from app.utils.logger import get_logger

router = APIRouter(prefix="/feedback", tags=["Feedback"])
logger = get_logger(__name__)


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_200_OK,
             summary="Accept or reject a mentor match")
async def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """
    Store accept/reject feedback and update match status in Neo4j and PostgreSQL.
    """
    if payload.action not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="action must be 'accepted' or 'rejected'")

    startup = await pg.get_startup_by_id(payload.startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail=f"Startup {payload.startup_id} not found")

    mentor = await pg.get_mentor_by_id(payload.mentor_id)
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor {payload.mentor_id} not found")

    # Store feedback
    await pg.store_feedback(
        startup_id=payload.startup_id,
        mentor_id=payload.mentor_id,
        action=payload.action,
        comments=payload.comments,
    )

    # Update match status in both stores
    await pg.update_match_status(payload.startup_id, payload.mentor_id, payload.action)
    await neo4j.update_match_status(payload.startup_id, payload.mentor_id, payload.action)

    logger.info("feedback_processed", startup_id=payload.startup_id,
                mentor_id=payload.mentor_id, action=payload.action)

    return FeedbackResponse(
        success=True,
        message=f"Match between {startup['name']} and {mentor['name']} marked as '{payload.action}'.",
    )
