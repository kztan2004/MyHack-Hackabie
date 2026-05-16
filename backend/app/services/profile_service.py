import re

from app.ai.gemini import GeminiService
from app.services.embedding_service import EmbeddingService


class SkillExtractionService:
    def __init__(self, gemini: GeminiService):
        self.gemini = gemini

    async def extract(self, name: str, raw_bio: str, available_skills: list[str] | None = None) -> list[str]:
        candidate_tags = await self.gemini.extract_skills(name, raw_bio, available_skills)
        supported = [tag for tag in candidate_tags if self._is_supported(tag, raw_bio)]
        return self._dedupe(supported)[:10]

    def normalize(self, skill: str) -> str:
        return re.sub(r"[^a-z0-9+#.]+", " ", skill.lower()).strip()

    def _is_supported(self, tag: str, raw_bio: str) -> bool:
        normalized_tag = self.normalize(tag)
        normalized_bio = self.normalize(raw_bio)
        if not normalized_tag:
            return False
        if normalized_tag in normalized_bio:
            return True
        words = [word for word in normalized_tag.split() if len(word) > 2]
        return bool(words) and all(word in normalized_bio for word in words)

    def _dedupe(self, skills: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for skill in skills:
            key = self.normalize(skill)
            if key and key not in seen:
                seen.add(key)
                result.append(skill.strip())
        return result


class ShortBioService:
    def __init__(self, gemini: GeminiService):
        self.gemini = gemini

    async def compress(self, name: str, raw_bio: str) -> str:
        return await self.gemini.short_bio(name, raw_bio)


class ProfileAIService:
    def __init__(
        self,
        skill_service: SkillExtractionService,
        short_bio_service: ShortBioService,
        embedding_service: EmbeddingService,
    ):
        self.skill_service = skill_service
        self.short_bio_service = short_bio_service
        self.embedding_service = embedding_service

    async def enrich(self, name: str, raw_bio: str, available_skills: list[str] | None = None) -> tuple[str, list[str], list[float]]:
        skills = await self.skill_service.extract(name, raw_bio, available_skills)
        short_bio = await self.short_bio_service.compress(name, raw_bio)
        embedding_text = " ".join([short_bio, *skills])
        embedding = await self.embedding_service.embed(embedding_text)
        return short_bio, skills, embedding
