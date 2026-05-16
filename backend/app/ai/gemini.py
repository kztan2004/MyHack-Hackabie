import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.ai.prompts import SHORT_BIO_SYSTEM_PROMPT, SKILL_EXTRACTION_SYSTEM_PROMPT
from app.core.config import Settings


class SkillExtractionResult(BaseModel):
    skill_tags: list[str] = Field(default_factory=list, max_length=10)


class ShortBioResult(BaseModel):
    short_bio: str = Field(max_length=320)


class GeminiService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def extract_skills(self, name: str, raw_bio: str) -> list[str]:
        if not self.settings.gemini_api_key:
            return self._local_explicit_skill_extraction(raw_bio)
        payload = await self._generate_json(SKILL_EXTRACTION_SYSTEM_PROMPT, self._profile_payload(name, raw_bio))
        try:
            parsed = SkillExtractionResult.model_validate(payload)
        except ValidationError:
            return []
        return [tag.strip() for tag in parsed.skill_tags if tag.strip()][:10]

    async def short_bio(self, name: str, raw_bio: str) -> str:
        if not self.settings.gemini_api_key:
            return self._local_short_bio(raw_bio)
        payload = await self._generate_json(SHORT_BIO_SYSTEM_PROMPT, self._profile_payload(name, raw_bio))
        try:
            parsed = ShortBioResult.model_validate(payload)
        except ValidationError:
            return self._local_short_bio(raw_bio)
        return self._trim_words(parsed.short_bio, 30)

    async def _generate_json(self, system_prompt: str, user_payload: str) -> dict[str, Any]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.settings.gemini_api_key)
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=user_payload,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        text = response.text or "{}"
        return self._strict_json_loads(text)

    def _profile_payload(self, name: str, raw_bio: str) -> str:
        return json.dumps({"name": name, "biography": raw_bio}, ensure_ascii=True)

    def _strict_json_loads(self, text: str) -> dict[str, Any]:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.S)
            if not match:
                return {}
            payload = json.loads(match.group(0))
        return payload if isinstance(payload, dict) else {}

    def _local_explicit_skill_extraction(self, raw_bio: str) -> list[str]:
        taxonomy = [
            "AI",
            "Machine Learning",
            "Data Science",
            "Fintech",
            "Banking Infrastructure",
            "Cybersecurity",
            "Cloud",
            "SaaS",
            "Product Management",
            "Go-To-Market",
            "Fundraising",
            "Venture Capital",
            "Climate Tech",
            "Healthtech",
            "Biotech",
            "Manufacturing",
            "Supply Chain",
            "Robotics",
            "Blockchain",
            "Payments",
            "Regulatory Compliance",
            "UX Research",
            "Software Engineering",
            "Data Analytics",
            "Marketing",
            "Sales",
            "Operations",
            "Strategy",
        ]
        lower = raw_bio.lower()
        tags: list[str] = []
        for tag in taxonomy:
            if tag.lower() in lower:
                tags.append(tag)
        return tags[:10]

    def _local_short_bio(self, raw_bio: str) -> str:
        first_sentence = re.split(r"(?<=[.!?])\s+", raw_bio.strip())[0]
        return self._trim_words(first_sentence, 30)

    def _trim_words(self, value: str, max_words: int) -> str:
        words = value.strip().split()
        if len(words) <= max_words:
            return value.strip()
        return " ".join(words[:max_words]).rstrip(".,;:") + "."
