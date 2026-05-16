"""Pydantic schemas for request/response validation — EcosystemGraph AI."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─── Health ──────────────────────────────────────────────────────────────────

class HealthStatus(BaseModel):
    status: str
    postgres: str
    neo4j: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─── Startup Schemas ─────────────────────────────────────────────────────────

class StartupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    stage: Optional[str] = Field(None, description="idea | pre-seed | seed | growth | scale")
    description: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "LendAI",
                "industry": "Fintech",
                "stage": "seed",
                "description": "AI-powered lending platform using alternative data for credit scoring in Southeast Asia",
            }
        }
    }


class StartupResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    stage: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    clean_description: Optional[str]
    ai_confidence: Optional[float]
    enriched_at: Optional[datetime]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─── Mentor Schemas ──────────────────────────────────────────────────────────

class MentorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    expertise_tags: Optional[List[str]] = Field(default=[], description="List of expertise areas")
    experience_years: Optional[int] = Field(default=0, ge=0)
    bio: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sarah Chen",
                "expertise_tags": ["Fintech", "AI", "Credit Scoring"],
                "experience_years": 12,
                "bio": "Serial entrepreneur with 12 years in fintech.",
            }
        }
    }


class MentorResponse(BaseModel):
    id: int
    name: str
    expertise_tags: Optional[List[str]]
    experience_years: Optional[int]
    bio: Optional[str]
    clean_bio: Optional[str]
    rating: Optional[float]
    available: Optional[bool]
    enriched_at: Optional[datetime]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─── Match Schemas ───────────────────────────────────────────────────────────

class MatchResult(BaseModel):
    mentor_id: int
    mentor_name: str
    score: float
    reason: str
    expertise_tags: List[str]
    experience_years: int


class MatchResponse(BaseModel):
    startup_id: int
    startup_name: str
    matches: List[MatchResult]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Feedback Schemas ────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    startup_id: int = Field(..., gt=0)
    mentor_id: int = Field(..., gt=0)
    action: str = Field(..., description="accepted | rejected")
    comments: Optional[str] = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "startup_id": 1,
                "mentor_id": 1,
                "action": "accepted",
                "comments": "Great match for our fintech problem.",
            }
        }
    }


class FeedbackResponse(BaseModel):
    success: bool
    message: str


# ─── Graph Schemas ───────────────────────────────────────────────────────────

class GraphNode(BaseModel):
    id: str
    label: str
    type: str          # "startup" | "mentor"
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    score: float
    status: str
    reason: Optional[str] = None


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    node_count: int
    edge_count: int
