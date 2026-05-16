"""
Neo4j Graph Service — EcosystemGraph AI
Graph model: (:Startup)-[:MATCHED_WITH {score, reason, status}]->(:Mentor)
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
_driver: Optional[AsyncDriver] = None


async def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def check_health() -> str:
    try:
        driver = await get_driver()
        async with driver.session() as session:
            await session.run("RETURN 1")
        return "healthy"
    except Exception as exc:
        logger.error("neo4j_health_check_failed", error=str(exc))
        return f"unhealthy: {exc}"


async def create_constraints() -> None:
    driver = await get_driver()
    async with driver.session() as session:
        for q in [
            "CREATE CONSTRAINT startup_id_unique IF NOT EXISTS FOR (s:Startup) REQUIRE s.startup_id IS UNIQUE",
            "CREATE CONSTRAINT mentor_id_unique  IF NOT EXISTS FOR (m:Mentor)  REQUIRE m.mentor_id  IS UNIQUE",
        ]:
            try:
                await session.run(q)
            except Exception as exc:
                logger.warning("constraint_warning", error=str(exc))
    logger.info("neo4j_constraints_ready")


async def upsert_startup_node(startup: Dict[str, Any]) -> None:
    driver = await get_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (s:Startup {startup_id: $startup_id})
            SET s.name=$name, s.industry=$industry, s.stage=$stage, s.tags=$tags
            """,
            startup_id=startup["id"], name=startup["name"],
            industry=startup.get("industry") or "",
            stage=startup.get("stage") or "",
            tags=startup.get("tags") or [],
        )
    logger.info("neo4j_startup_upserted", startup_id=startup["id"])


async def upsert_mentor_node(mentor: Dict[str, Any]) -> None:
    driver = await get_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (m:Mentor {mentor_id: $mentor_id})
            SET m.name=$name, m.expertise_tags=$expertise_tags, m.experience_years=$experience_years
            """,
            mentor_id=mentor["id"], name=mentor["name"],
            expertise_tags=mentor.get("expertise_tags") or [],
            experience_years=mentor.get("experience_years", 0),
        )
    logger.info("neo4j_mentor_upserted", mentor_id=mentor["id"])


async def upsert_mentor_nodes(mentors: List[Dict[str, Any]]) -> None:
    for m in mentors:
        await upsert_mentor_node(m)
    logger.info("neo4j_mentors_synced", count=len(mentors))


async def store_match_relationship(
    startup_id: int, mentor_id: int, score: float, reason: str, status: str = "pending",
) -> None:
    driver = await get_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (s:Startup {startup_id: $startup_id})
            MATCH (m:Mentor  {mentor_id:  $mentor_id})
            MERGE (s)-[r:MATCHED_WITH]->(m)
            SET r.score=$score, r.reason=$reason, r.status=$status, r.updated_at=datetime()
            """,
            startup_id=startup_id, mentor_id=mentor_id,
            score=score, reason=reason, status=status,
        )
    logger.info("neo4j_match_stored", startup_id=startup_id, mentor_id=mentor_id)


async def update_match_status(startup_id: int, mentor_id: int, status: str) -> None:
    driver = await get_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (s:Startup {startup_id: $startup_id})-[r:MATCHED_WITH]->(m:Mentor {mentor_id: $mentor_id})
            SET r.status=$status, r.updated_at=datetime()
            """,
            startup_id=startup_id, mentor_id=mentor_id, status=status,
        )
    logger.info("neo4j_status_updated", startup_id=startup_id, mentor_id=mentor_id, status=status)


async def get_graph_data() -> Dict[str, Any]:
    driver = await get_driver()
    async with driver.session() as session:
        s_res = await session.run(
            "MATCH (s:Startup) RETURN s.startup_id AS id, s.name AS name, s.industry AS industry, s.stage AS stage, s.tags AS tags"
        )
        startups = await s_res.data()

        m_res = await session.run(
            "MATCH (m:Mentor) RETURN m.mentor_id AS id, m.name AS name, m.expertise_tags AS expertise_tags, m.experience_years AS experience_years"
        )
        mentors = await m_res.data()

        e_res = await session.run(
            """
            MATCH (s:Startup)-[r:MATCHED_WITH]->(m:Mentor)
            RETURN s.startup_id AS startup_id, m.mentor_id AS mentor_id,
                   r.score AS score, r.status AS status, r.reason AS reason
            """
        )
        edges = await e_res.data()

    return {"startups": startups, "mentors": mentors, "edges": edges}
