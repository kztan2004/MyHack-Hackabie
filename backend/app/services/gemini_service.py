"""
Google Gemini AI Service — EcosystemGraph AI

Responsibilities:
  1. enrich_startup()     — normalize + tag startup profiles
  2. enrich_mentor()      — normalize + tag mentor profiles
  3. match_startup()      — rank top-K mentors for a startup
  4. generate_explanation() — human-readable match justification
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional

from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ─── Prompt Templates ─────────────────────────────────────────────────────────

STARTUP_ENRICHMENT_PROMPT = """You are an ecosystem data enrichment AI.
Given raw startup input, analyze and return ONLY a valid JSON object — no markdown, no explanation.

Input startup:
Name: {name}
Industry: {industry}
Stage: {stage}
Description: {description}

Return exactly this JSON structure:
{{
  "industry": "normalized industry name",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "clean_description": "improved, professional 2-sentence description",
  "confidence": 0.92
}}

Rules:
- industry: normalize to a standard category (Fintech, Healthtech, SaaS, EdTech, CleanTech, Cybersecurity, Logistics, AI/ML, Other)
- tags: 4-6 specific, relevant technology or domain tags
- clean_description: rewrite to be clear, professional, investor-ready
- confidence: float 0-1 indicating how well the profile was understood
"""

MENTOR_ENRICHMENT_PROMPT = """You are an ecosystem data enrichment AI.
Given raw mentor input, analyze and return ONLY a valid JSON object — no markdown, no explanation.

Input mentor:
Name: {name}
Expertise Tags: {expertise_tags}
Experience Years: {experience_years}
Bio: {bio}

Return exactly this JSON structure:
{{
  "expertise_tags": ["tag1", "tag2", "tag3", "tag4"],
  "clean_bio": "improved, professional 2-sentence bio",
  "primary_domain": "main area of expertise"
}}

Rules:
- expertise_tags: normalize and expand to specific, searchable tags
- clean_bio: rewrite to be concise, professional, highlight key achievements
- primary_domain: the single most important domain (Fintech, AI, SaaS, etc.)
"""

MATCHING_PROMPT = """You are an innovation ecosystem matching AI.

Given the startup profile:
{startup}

And these available mentors:
{mentor_list}

Task: Rank the TOP 3 most suitable mentors for this startup.
Consider: industry alignment, tag overlap, experience relevance, stage fit.

Return ONLY a valid JSON array — no markdown, no explanation:
[
  {{
    "mentor_id": 1,
    "score": 0.91,
    "reason": "2-sentence explanation of why this mentor is the best fit"
  }},
  {{
    "mentor_id": 2,
    "score": 0.78,
    "reason": "2-sentence explanation"
  }},
  {{
    "mentor_id": 3,
    "score": 0.65,
    "reason": "2-sentence explanation"
  }}
]

Rules:
- score: float 0.0 to 1.0 (higher = better match)
- reason: specific, actionable reasoning referencing the startup's actual needs
- Return exactly 3 items (or fewer if fewer mentors available)
"""

EXPLANATION_PROMPT = """You are an AI explaining ecosystem matches to startup founders.

Startup: {startup_name} ({startup_industry}, {startup_stage} stage)
Startup description: {startup_description}

Mentor: {mentor_name}
Mentor expertise: {mentor_expertise}
Match score: {score}

Write a 2-3 sentence explanation of WHY this mentor is ideal for this startup.
Be specific about:
1. Which of the startup's challenges the mentor can address
2. What unique experience makes this mentor valuable
3. What the startup can expect to gain

Be encouraging, specific, and avoid generic statements.
"""


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        self.model = self.settings.gemini_model

    # ─── Startup Enrichment ───────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def enrich_startup(
        self,
        name: str,
        industry: Optional[str],
        stage: Optional[str],
        description: Optional[str],
    ) -> Dict[str, Any]:
        """Enrich a startup profile using Gemini."""
        prompt = STARTUP_ENRICHMENT_PROMPT.format(
            name=name,
            industry=industry or "Unknown",
            stage=stage or "Unknown",
            description=description or "No description provided",
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            raw = response.text.strip()
            logger.info("gemini_startup_enrichment_raw", startup=name, raw=raw[:300])
            data = self._parse_json(raw)
            return {
                "industry": data.get("industry", industry or "Other"),
                "tags": data.get("tags", []),
                "clean_description": data.get("clean_description", description or ""),
                "confidence": float(data.get("confidence", 0.5)),
            }
        except Exception as exc:
            logger.error("gemini_startup_enrichment_failed", error=str(exc))
            return {
                "industry": industry or "Other",
                "tags": [],
                "clean_description": description or "",
                "confidence": 0.0,
            }

    # ─── Mentor Enrichment ────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def enrich_mentor(
        self,
        name: str,
        expertise_tags: List[str],
        experience_years: int,
        bio: Optional[str],
    ) -> Dict[str, Any]:
        """Enrich a mentor profile using Gemini."""
        prompt = MENTOR_ENRICHMENT_PROMPT.format(
            name=name,
            expertise_tags=", ".join(expertise_tags) if expertise_tags else "Not specified",
            experience_years=experience_years,
            bio=bio or "No bio provided",
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            raw = response.text.strip()
            data = self._parse_json(raw)
            return {
                "expertise_tags": data.get("expertise_tags", expertise_tags),
                "clean_bio": data.get("clean_bio", bio or ""),
                "primary_domain": data.get("primary_domain", ""),
            }
        except Exception as exc:
            logger.error("gemini_mentor_enrichment_failed", error=str(exc))
            return {
                "expertise_tags": expertise_tags,
                "clean_bio": bio or "",
                "primary_domain": "",
            }

    # ─── Matching ─────────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def match_startup_to_mentors(
        self,
        startup: Dict[str, Any],
        mentors: List[Dict[str, Any]],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """Use Gemini to rank mentors for a startup. Returns list of {mentor_id, score, reason}."""
        if not mentors:
            return []

        startup_str = (
            f"Name: {startup.get('name')}\n"
            f"Industry: {startup.get('industry')}\n"
            f"Stage: {startup.get('stage')}\n"
            f"Description: {startup.get('clean_description') or startup.get('description')}\n"
            f"Tags: {', '.join(startup.get('tags') or [])}"
        )

        mentor_list_str = "\n".join([
            f"- ID: {m['id']}, Name: {m['name']}, "
            f"Expertise: {', '.join(m.get('expertise_tags') or [])}, "
            f"Experience: {m.get('experience_years', 0)} years"
            for m in mentors
        ])

        prompt = MATCHING_PROMPT.format(
            startup=startup_str,
            mentor_list=mentor_list_str,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            raw = response.text.strip()
            logger.info("gemini_matching_raw", startup=startup.get("name"), raw=raw[:400])
            data = self._parse_json_array(raw)
            return data[:top_k]
        except Exception as exc:
            logger.error("gemini_matching_failed", error=str(exc))
            return []

    # ─── Explanation ──────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    async def generate_explanation(
        self,
        startup: Dict[str, Any],
        mentor: Dict[str, Any],
        score: float,
    ) -> str:
        """Generate a rich human-readable explanation for a match."""
        prompt = EXPLANATION_PROMPT.format(
            startup_name=startup.get("name", ""),
            startup_industry=startup.get("industry", ""),
            startup_stage=startup.get("stage", ""),
            startup_description=startup.get("clean_description") or startup.get("description", ""),
            mentor_name=mentor.get("name", ""),
            mentor_expertise=", ".join(mentor.get("expertise_tags") or []),
            score=score,
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as exc:
            logger.error("gemini_explanation_failed", error=str(exc))
            tags = mentor.get("expertise_tags") or []
            return (
                f"{mentor.get('name')} is highly recommended for {startup.get('name')} "
                f"based on strong alignment in {', '.join(tags[:3])}. "
                f"With {mentor.get('experience_years', 0)} years of experience, "
                f"they can provide valuable guidance for your {startup.get('stage', '')} stage journey."
            )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        """Strip markdown fences and parse a JSON object."""
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning("json_parse_failed", error=str(exc), raw=raw[:100])
            return {}

    def _parse_json_array(self, raw: str) -> List[Dict[str, Any]]:
        """Strip markdown fences and parse a JSON array."""
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError as exc:
            logger.warning("json_array_parse_failed", error=str(exc), raw=raw[:100])
            return []
