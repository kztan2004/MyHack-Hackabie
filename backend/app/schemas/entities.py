from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    raw_bio: str = Field(min_length=10, max_length=5000)


class ParticipantCreate(ProfileCreate):
    company_id: UUID | None = None


class CompanyProgramLink(BaseModel):
    company_id: UUID
    program_id: UUID


class ParticipantProgramLink(BaseModel):
    participant_id: UUID
    program_id: UUID


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    raw_bio: str
    short_bio: str
    skills: list[str] = []
    created_at: datetime


class ParticipantRead(ProfileRead):
    company_id: UUID | None = None


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
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
    status: str
    created_at: datetime


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    score: float | None = None


class GraphRead(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class TokenRequest(BaseModel):
    username: str
    password: str
