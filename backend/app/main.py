from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.db.session import engine
from app.graph.neo4j_service import Neo4jService
from app.models.entities import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        app.state.graph = Neo4jService(settings)
    except Exception:
        app.state.graph = None
    yield
    graph = getattr(app.state, "graph", None)
    if graph:
        await graph.close()


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
# IMPORTANT: Starlette inserts middleware at position 0 on each add_middleware call,
# so the LAST one added becomes the OUTERMOST (first to handle every request).
# CORSMiddleware must be outermost so it intercepts OPTIONS preflight requests
# before RateLimitMiddleware counts them or rejects them.
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "ngrok-skip-browser-warning"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router, prefix=settings.api_prefix)
