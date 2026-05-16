"""
EcosystemGraph AI — FastAPI Application Entry Point
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import HealthStatus
from app.routers import startups, mentors, matching, feedback, graph
from app.services import postgres_service as pg, neo4j_service as neo4j
from app.utils.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger("lifespan")
    logger.info("ecosystem_startup_begin")

    # Initialize PostgreSQL
    try:
        await pg.init_db()
        logger.info("postgres_ready")
    except Exception as exc:
        logger.error("postgres_init_failed", error=str(exc))

    # Initialize Neo4j constraints
    try:
        await neo4j.create_constraints()
        logger.info("neo4j_ready")
    except Exception as exc:
        logger.error("neo4j_init_failed", error=str(exc))

    # Pre-load existing mentors into Neo4j graph
    try:
        mentors_list = await pg.get_all_mentors()
        await neo4j.upsert_mentor_nodes(mentors_list)
        logger.info("neo4j_mentors_preloaded", count=len(mentors_list))
    except Exception as exc:
        logger.warning("neo4j_preload_warning", error=str(exc))

    # Pre-load existing startups into Neo4j graph
    try:
        startups_list = await pg.get_all_startups()
        for s in startups_list:
            await neo4j.upsert_startup_node(s)
        logger.info("neo4j_startups_preloaded", count=len(startups_list))
    except Exception as exc:
        logger.warning("neo4j_startup_preload_warning", error=str(exc))

    logger.info("ecosystem_startup_complete")
    yield

    await neo4j.close_driver()
    logger.info("ecosystem_shutdown_complete")


settings = get_settings()

app = FastAPI(
    title="EcosystemGraph AI",
    description=(
        "AI-Driven Automation of Innovation Ecosystem Relationships "
        "using Google Gemini + Neo4j Graph Intelligence. "
        "Match startups with mentors, enrich profiles, and visualize the ecosystem graph."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(startups.router)
app.include_router(mentors.router)
app.include_router(matching.router)
app.include_router(feedback.router)
app.include_router(graph.router)


@app.get("/health", response_model=HealthStatus, tags=["System"])
async def health_check() -> HealthStatus:
    """Check connectivity of all backend services."""
    postgres_status = await pg.check_health()
    neo4j_status = await neo4j.check_health()
    overall = "healthy" if all(s == "healthy" for s in [postgres_status, neo4j_status]) else "degraded"
    return HealthStatus(
        status=overall,
        postgres=postgres_status,
        neo4j=neo4j_status,
        timestamp=datetime.utcnow(),
    )


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "EcosystemGraph AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "create_startup": "POST /startup",
            "list_startups": "GET /startups",
            "create_mentor": "POST /mentor",
            "list_mentors": "GET /mentors",
            "generate_matches": "POST /match/{startup_id}",
            "submit_feedback": "POST /feedback",
            "get_graph": "GET /graph",
        },
    }
