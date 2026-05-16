from dataclasses import dataclass
from uuid import UUID

from app.graph.neo4j_service import Neo4jService
from app.repositories.ecosystem import EcosystemRepository
from app.services.embedding_service import EmbeddingService


@dataclass
class MatchCandidate:
    match_type: str
    source_type: str
    source_id: UUID
    source_name: str
    target_type: str
    target_id: UUID
    target_name: str
    score: float
    shared_skills: list[str]
    explanation: list[str]


class MatchingService:
    def __init__(
        self,
        repository: EcosystemRepository,
        embedding_service: EmbeddingService,
        graph_service: Neo4jService | None = None,
    ):
        self.repository = repository
        self.embedding_service = embedding_service
        self.graph_service = graph_service

    async def generate(self) -> list[MatchCandidate]:
        import asyncio

        mentors = await self.repository.list_mentors_with_skills()
        companies = await self.repository.list_companies_with_skills()
        participants = await self.repository.list_participants_with_skills()
        programs = await self.repository.list_programs_with_skills()

        tasks = []
        for company in companies:
            for mentor in mentors:
                tasks.append(self._score("company_mentor", company, "company", mentor, "mentor", "Startup company needs a mentor whose skills can guide business growth."))
            for program in programs:
                tasks.append(self._score("company_program", company, "company", program, "program", "Company can use this program to grow participant skills.", bonus=self._linked_program_bonus(company, program)))

        for program in programs:
            for company in companies:
                tasks.append(self._score("program_company", program, "program", company, "company", "Program can recruit companies whose teams match its focus areas.", bonus=self._linked_program_bonus(company, program)))

        for participant in participants:
            for program in programs:
                tasks.append(self._score("participant_program", participant, "participant", program, "program", "Participant can join this program to improve relevant professional skills."))

        candidates: list[MatchCandidate] = await asyncio.gather(*tasks)

        saved_matches = []
        for candidate in candidates:
            saved = await self.repository.upsert_match(
                candidate.match_type,
                candidate.source_type,
                candidate.source_id,
                candidate.source_name,
                candidate.target_type,
                candidate.target_id,
                candidate.target_name,
                candidate.score,
                candidate.explanation,
                candidate.shared_skills,
            )
            saved_matches.append(candidate)
            if self.graph_service:
                await self.graph_service.upsert_match(
                    candidate.source_type,
                    saved.source_id,
                    candidate.target_type,
                    saved.target_id,
                    candidate.match_type.upper(),
                    float(saved.score),
                )
        return sorted(saved_matches, key=lambda item: item.score, reverse=True)

    async def _score(
        self,
        match_type: str,
        source: dict,
        source_type: str,
        target: dict,
        target_type: str,
        story: str,
        bonus: float = 0.0,
    ) -> MatchCandidate:
        source_profile = source["profile"]
        target_profile = target["profile"]
        source_skills = source["normalized_skills"]
        target_skills = target["normalized_skills"]

        shared_normalized = source_skills.intersection(target_skills)
        shared_skills = [
            skill for skill in source["skills"] if self.repository.skill_service.normalize(skill) in shared_normalized
        ]

        skill_union = source_skills.union(target_skills)
        skill_overlap = len(shared_normalized) / len(skill_union) if skill_union else 0.0
        semantic = self.embedding_service.cosine(source_profile.embedding, target_profile.embedding)
        
        # If no explicit skill overlap exists, zero out the semantic score to prevent hallucinated matches
        if skill_overlap == 0:
            semantic = 0.0

        # 50% Skill Overlap + 50% Semantic Similarity (plus existing relationship bonus)
        base_score = (0.5 * skill_overlap) + (0.5 * semantic)
        score = base_score + (0.15 * bonus)

        explanation = [story]
        if shared_skills:
            explanation.append("Shared explicit skills: " + ", ".join(shared_skills[:5]))

        # AI Reason generation for high-confidence matches (>= 0.75)
        if score >= 0.75:
            gemini = self.repository.skill_service.gemini
            ai_reason = await gemini.generate_matching_reason(
                source_profile.short_bio or source_profile.raw_bio,
                target_profile.short_bio or target_profile.raw_bio,
                score
            )
            if ai_reason:
                explanation.append(f"AI Insight: {ai_reason}")

        if bonus > 0:
            explanation.append("Existing relationship increases match confidence.")

        return MatchCandidate(
            match_type=match_type,
            source_type=source_type,
            source_id=source_profile.id,
            source_name=source_profile.name,
            target_type=target_type,
            target_id=target_profile.id,
            target_name=target_profile.name,
            score=round(score, 4),
            shared_skills=shared_skills,
            explanation=explanation,
        )

    def _linked_program_bonus(self, company: dict, program: dict) -> float:
        return 1.0 if program["profile"].id in company.get("program_ids", []) else 0.0
