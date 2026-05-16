from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, CompanyProgram, Match, Mentor, Participant, ParticipantProgram, ProfileSkill, Program, Skill
from app.services.profile_service import SkillExtractionService

PROFILE_MODELS = {
    "mentor": Mentor,
    "company": Company,
    "participant": Participant,
    "program": Program,
}


class EcosystemRepository:
    def __init__(self, session: AsyncSession, skill_service: SkillExtractionService):
        self.session = session
        self.skill_service = skill_service

    async def create_profile(
        self,
        entity_type: str,
        name: str,
        raw_bio: str,
        short_bio: str,
        skills: list[str],
        embedding: list[float],
        company_id: UUID | None = None,
    ) -> Any:
        model = PROFILE_MODELS[entity_type]
        values = {
            "name": name,
            "raw_bio": raw_bio,
            "short_bio": short_bio,
            "embedding": embedding,
        }
        if entity_type == "participant":
            values["company_id"] = company_id
        instance = model(**values)
        self.session.add(instance)
        await self.session.flush()
        await self.replace_skills(entity_type, instance.id, skills)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def list_profiles(self, entity_type: str) -> list[Any]:
        model = PROFILE_MODELS[entity_type]
        result = await self.session.execute(select(model).order_by(model.created_at.desc()))
        return list(result.scalars().all())

    async def get_profile(self, entity_type: str, entity_id: UUID) -> Any | None:
        model = PROFILE_MODELS[entity_type]
        return await self.session.get(model, entity_id)

    async def get_skill_names(self, entity_type: str, entity_id: UUID) -> list[str]:
        stmt = (
            select(Skill.name)
            .join(ProfileSkill, ProfileSkill.skill_id == Skill.id)
            .where(ProfileSkill.entity_type == entity_type, ProfileSkill.entity_id == entity_id)
            .order_by(Skill.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def replace_skills(self, entity_type: str, entity_id: UUID, skills: list[str]) -> None:
        await self.session.execute(
            delete(ProfileSkill).where(ProfileSkill.entity_type == entity_type, ProfileSkill.entity_id == entity_id)
        )
        for skill in skills:
            normalized = self.skill_service.normalize(skill)
            if not normalized:
                continue
            skill_obj = await self.upsert_skill(skill, normalized)
            self.session.add(ProfileSkill(entity_type=entity_type, entity_id=entity_id, skill_id=skill_obj.id))

    async def upsert_skill(self, name: str, normalized_name: str) -> Skill:
        stmt = (
            pg_insert(Skill)
            .values(name=name, normalized_name=normalized_name)
            .on_conflict_do_update(
                index_elements=[Skill.normalized_name],
                set_={"name": name},
            )
            .returning(Skill)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_mentors_with_skills(self) -> list[dict[str, Any]]:
        return await self._profiles_with_skills("mentor")

    async def list_companies_with_skills(self) -> list[dict[str, Any]]:
        return await self._profiles_with_skills("company")

    async def list_programs_with_skills(self) -> list[dict[str, Any]]:
        return await self._profiles_with_skills("program")

    async def list_participants_with_skills(self) -> list[dict[str, Any]]:
        return await self._profiles_with_skills("participant")

    async def upsert_match(
        self,
        match_type: str,
        source_type: str,
        source_id: UUID,
        source_name: str,
        target_type: str,
        target_id: UUID,
        target_name: str,
        score: float,
        explanation: list[str],
        shared_skills: list[str],
    ) -> Match:
        stmt = (
            pg_insert(Match)
            .values(
                match_type=match_type,
                source_type=source_type,
                source_id=source_id,
                source_name=source_name,
                target_type=target_type,
                target_id=target_id,
                target_name=target_name,
                score=round(score, 4),
                explanation=explanation,
                shared_skills=shared_skills,
                status="recommended",
            )
            .on_conflict_do_update(
                index_elements=[Match.match_type, Match.source_id, Match.target_id],
                set_={
                    "source_name": source_name,
                    "target_name": target_name,
                    "score": round(score, 4),
                    "explanation": explanation,
                    "shared_skills": shared_skills,
                    "status": "recommended",
                },
            )
            .returning(Match)
        )
        result = await self.session.execute(stmt)
        match = result.scalar_one()
        await self.session.commit()
        return match

    async def list_matches(
        self,
        company_id: UUID | None = None,
        source_type: str | None = None,
        source_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        stmt = select(Match).order_by(Match.match_type, Match.score.desc(), Match.created_at.desc())
        if company_id:
            stmt = stmt.where(
                or_(
                    and_(Match.source_type == "company", Match.source_id == company_id),
                    and_(Match.target_type == "company", Match.target_id == company_id),
                )
            )
        if source_type and source_id:
            stmt = stmt.where(Match.source_type == source_type, Match.source_id == source_id)
        result = await self.session.execute(stmt)
        rows = []
        for match in result.scalars().all():
            rows.append(
                {
                    "id": match.id,
                    "match_type": match.match_type,
                    "source_type": match.source_type,
                    "source_id": match.source_id,
                    "source_name": match.source_name,
                    "target_type": match.target_type,
                    "target_id": match.target_id,
                    "target_name": match.target_name,
                    "score": float(match.score),
                    "shared_skills": match.shared_skills,
                    "explanation": match.explanation,
                    "status": match.status,
                    "created_at": match.created_at,
                }
            )
        return rows

    async def link_company_program(self, company_id: UUID, program_id: UUID) -> bool:
        company = await self.session.get(Company, company_id)
        program = await self.session.get(Program, program_id)
        if not company or not program:
            return False
        await self.session.execute(
            pg_insert(CompanyProgram)
            .values(company_id=company_id, program_id=program_id)
            .on_conflict_do_nothing(index_elements=[CompanyProgram.company_id, CompanyProgram.program_id])
        )
        company_skills = await self.get_skill_names("company", company_id)
        program_skills = await self.get_skill_names("program", program_id)
        await self.replace_skills("company", company_id, sorted(set(company_skills + program_skills)))
        await self.session.commit()
        return True

    async def link_participant_program(self, participant_id: UUID, program_id: UUID) -> bool:
        participant = await self.session.get(Participant, participant_id)
        program = await self.session.get(Program, program_id)
        if not participant or not program:
            return False
        await self.session.execute(
            pg_insert(ParticipantProgram)
            .values(participant_id=participant_id, program_id=program_id)
            .on_conflict_do_nothing(index_elements=[ParticipantProgram.participant_id, ParticipantProgram.program_id])
        )
        await self.session.commit()
        return True

    async def list_company_program_ids(self, company_id: UUID) -> list[UUID]:
        result = await self.session.execute(
            select(CompanyProgram.program_id).where(CompanyProgram.company_id == company_id)
        )
        return list(result.scalars().all())

    async def _profiles_with_skills(self, entity_type: str) -> list[dict[str, Any]]:
        model = PROFILE_MODELS[entity_type]
        result = await self.session.execute(select(model))
        profiles = list(result.scalars().all())
        rows = []
        for profile in profiles:
            skills = await self.get_skill_names(entity_type, profile.id)
            row = {
                "profile": profile,
                "skills": skills,
                "normalized_skills": {self.skill_service.normalize(skill) for skill in skills},
            }
            if entity_type == "company":
                row["program_ids"] = await self.list_company_program_ids(profile.id)
            rows.append(
                row
            )
        return rows
