"""
Matching Engine — Hybrid scoring: Gemini AI score + experience bonus.
Gemini provides AI scores; this module applies bonuses and re-normalizes.
"""
from __future__ import annotations
from typing import Any, Dict, List

from app.utils.logger import get_logger

logger = get_logger(__name__)

EXPERIENCE_BONUS_PER_YEAR = 0.005   # +0.5% per year of experience
MAX_EXPERIENCE_BONUS = 0.10          # cap at 10%


def apply_experience_bonus(
    ai_matches: List[Dict[str, Any]],
    mentors_by_id: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Apply experience bonus to Gemini AI scores and re-rank.
    ai_matches: [{mentor_id, score, reason}, ...]
    Returns: [{mentor_id, score, reason, mentor_data}, ...] sorted desc by score
    """
    enriched = []
    for m in ai_matches:
        mentor_id = m.get("mentor_id")
        ai_score = float(m.get("score", 0.0))
        mentor = mentors_by_id.get(mentor_id)
        if not mentor:
            continue

        years = mentor.get("experience_years", 0) or 0
        bonus = min(years * EXPERIENCE_BONUS_PER_YEAR, MAX_EXPERIENCE_BONUS)
        final_score = round(min(ai_score + bonus, 1.0), 4)

        enriched.append({
            "mentor_id": mentor_id,
            "mentor_name": mentor["name"],
            "score": final_score,
            "reason": m.get("reason", ""),
            "expertise_tags": mentor.get("expertise_tags") or [],
            "experience_years": years,
        })

    enriched.sort(key=lambda x: x["score"], reverse=True)
    logger.info("matching_engine_complete", count=len(enriched))
    return enriched
