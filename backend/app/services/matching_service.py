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
        mentors = await self.repository.list_mentors_with_skills()
        companies = await self.repository.list_companies_with_skills()
        participants = await self.repository.list_participants_with_skills()
        programs = await self.repository.list_programs_with_skills()

        candidates: list[MatchCandidate] = []
        for company in companies:
            candidates.extend(self._company_mentor_matches(company, mentors))
            candidates.extend(self._company_program_matches(company, programs))
        for program in programs:
            candidates.extend(self._program_company_matches(program, companies))
        for participant in participants:
            candidates.extend(self._participant_program_matches(participant, programs))

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

    def _company_mentor_matches(self, company: dict, mentors: list[dict]) -> list[MatchCandidate]:
        return [
            self._score(
                "company_mentor",
                company,
                "company",
                mentor,
                "mentor",
                "Startup company needs a mentor whose skills can guide business growth.",
                program_bonus=0.0,
            )
            for mentor in mentors
        ]

    def _company_program_matches(self, company: dict, programs: list[dict]) -> list[MatchCandidate]:
        return [
            self._score(
                "company_program",
                company,
                "company",
                program,
                "program",
                "Company can use this program to grow participant skills.",
                program_bonus=self._linked_program_bonus(company, program),
            )
            for program in programs
        ]

    def _program_company_matches(self, program: dict, companies: list[dict]) -> list[MatchCandidate]:
        return [
            self._score(
                "program_company",
                program,
                "program",
                company,
                "company",
                "Program can recruit companies whose teams match its focus areas.",
                program_bonus=self._linked_program_bonus(company, program),
            )
            for company in companies
        ]

    def _participant_program_matches(self, participant: dict, programs: list[dict]) -> list[MatchCandidate]:
        return [
            self._score(
                "participant_program",
                participant,
                "participant",
                program,
                "program",
                "Participant can join this program to improve relevant professional skills.",
                program_bonus=0.0,
            )
            for program in programs
        ]

    def _score(
        self,
        match_type: str,
        source: dict,
        source_type: str,
        target: dict,
        target_type: str,
        story: str,
        program_bonus: float,
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
        score = (0.45 * skill_overlap) + (0.4 * semantic) + (0.15 * program_bonus)

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
            explanation=self._explain(story, shared_skills, semantic, program_bonus),
        )

    def _linked_program_bonus(self, company: dict, program: dict) -> float:
        return 1.0 if program["profile"].id in company.get("program_ids", []) else 0.0

    def _explain(self, story: str, shared_skills: list[str], semantic: float, program_bonus: float) -> list[str]:
        explanation = [story]
        if shared_skills:
            explanation.append("Shared explicit skills: " + ", ".join(shared_skills[:5]))
        if semantic >= 0.35:
            explanation.append("Profile summaries and skill text show semantic alignment.")
        if program_bonus > 0:
            explanation.append("Existing company-program relationship increases confidence.")
        if len(explanation) == 1:
            explanation.append("Low-confidence match generated from limited explicit overlap.")
        return explanation
