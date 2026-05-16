from uuid import UUID

from neo4j import AsyncGraphDatabase

from app.core.config import Settings


class Neo4jService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    async def close(self) -> None:
        await self.driver.close()

    async def upsert_profile(self, entity_type: str, entity_id: UUID, name: str, short_bio: str, skills: list[str]) -> None:
        label = self._label(entity_type)
        async with self.driver.session() as session:
            await session.run(
                f"MERGE (n:{label} {{id: $id}}) SET n.name = $name, n.short_bio = $short_bio",
                id=str(entity_id),
                name=name,
                short_bio=short_bio,
            )
            for skill in skills:
                await session.run(
                    f"""
                    MATCH (n:{label} {{id: $id}})
                    MERGE (s:Skill {{normalized_name: $normalized}})
                    SET s.id = $normalized, s.name = $skill
                    MERGE (n)-[:{self._skill_relationship(entity_type)}]->(s)
                    """,
                    id=str(entity_id),
                    skill=skill,
                    normalized=skill.lower().strip(),
                )

    async def link_participant_company(self, participant_id: UUID, company_id: UUID) -> None:
        await self._link("Participant", participant_id, "Company", company_id, "WORKS_FOR")

    async def link_company_program(self, company_id: UUID, program_id: UUID) -> None:
        await self._link("Company", company_id, "Program", program_id, "ENROLLED_IN")

    async def link_participant_program(self, participant_id: UUID, program_id: UUID) -> None:
        await self._link("Participant", participant_id, "Program", program_id, "PARTICIPATES_IN")

    async def upsert_match(
        self,
        source_type: str,
        source_id: UUID,
        target_type: str,
        target_id: UUID,
        rel_type: str,
        score: float,
    ) -> None:
        source_label = self._label(source_type)
        target_label = self._label(target_type)
        relationship = self._safe_relationship(rel_type)
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (source:{source_label} {{id: $source_id}})
                MATCH (target:{target_label} {{id: $target_id}})
                MERGE (source)-[r:{relationship}]->(target)
                SET r.score = $score, r.created_at = datetime()
                """,
                source_id=str(source_id),
                target_id=str(target_id),
                score=score,
            )

    async def read_graph(self) -> dict[str, list[dict]]:
        async with self.driver.session() as session:
            nodes_result = await session.run(
                """
                MATCH (n)
                WHERE n:Mentor OR n:Company OR n:Participant OR n:Program OR n:Skill
                RETURN n.id AS id, coalesce(n.name, n.normalized_name) AS label, labels(n)[0] AS type
                LIMIT 250
                """
            )
            rels_result = await session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE (a:Mentor OR a:Company OR a:Participant OR a:Program)
                RETURN a.id AS source, b.id AS target, type(r) AS type, r.score AS score
                LIMIT 500
                """
            )
            nodes = [record.data() async for record in nodes_result]
            edges = [record.data() async for record in rels_result if record["source"] and record["target"]]
            return {"nodes": nodes, "edges": edges}

    async def _link(self, left_label: str, left_id: UUID, right_label: str, right_id: UUID, rel_type: str) -> None:
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (a:{left_label} {{id: $left_id}})
                MATCH (b:{right_label} {{id: $right_id}})
                MERGE (a)-[:{rel_type}]->(b)
                """,
                left_id=str(left_id),
                right_id=str(right_id),
            )

    def _label(self, entity_type: str) -> str:
        return {
            "mentor": "Mentor",
            "company": "Company",
            "participant": "Participant",
            "program": "Program",
        }[entity_type]

    def _skill_relationship(self, entity_type: str) -> str:
        return "FOCUSES_ON" if entity_type == "program" else "HAS_SKILL"

    def _safe_relationship(self, rel_type: str) -> str:
        return "".join(char for char in rel_type if char.isalnum() or char == "_") or "MATCHED_WITH"
