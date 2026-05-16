"""GET /graph — Return ecosystem graph data for visualization."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException

from app.models.schemas import GraphResponse, GraphNode, GraphEdge
from app.services import neo4j_service as neo4j
from app.utils.logger import get_logger

router = APIRouter(prefix="/graph", tags=["Graph"])
logger = get_logger(__name__)


@router.get("", response_model=GraphResponse, summary="Get the full ecosystem relationship graph")
async def get_graph() -> GraphResponse:
    """Return all nodes (Startup, Mentor) and edges (MATCHED_WITH) for graph visualization."""
    try:
        data = await neo4j.get_graph_data()
    except Exception as exc:
        logger.error("graph_data_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve graph data: {exc}")

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    for s in data.get("startups", []):
        nodes.append(GraphNode(
            id=f"startup_{s['id']}",
            label=s["name"],
            type="startup",
            properties={"industry": s.get("industry", ""), "stage": s.get("stage", ""), "tags": s.get("tags") or []},
        ))

    for m in data.get("mentors", []):
        nodes.append(GraphNode(
            id=f"mentor_{m['id']}",
            label=m["name"],
            type="mentor",
            properties={"expertise_tags": m.get("expertise_tags") or [], "experience_years": m.get("experience_years", 0)},
        ))

    for e in data.get("edges", []):
        edges.append(GraphEdge(
            source=f"startup_{e['startup_id']}",
            target=f"mentor_{e['mentor_id']}",
            score=float(e.get("score", 0)),
            status=e.get("status", "pending"),
            reason=e.get("reason"),
        ))

    logger.info("graph_data_returned", nodes=len(nodes), edges=len(edges))
    return GraphResponse(nodes=nodes, edges=edges, node_count=len(nodes), edge_count=len(edges))
