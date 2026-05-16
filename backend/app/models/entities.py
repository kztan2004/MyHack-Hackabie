import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Mentor(Base, TimestampMixin):
    __tablename__ = "mentors"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_bio: Mapped[str] = mapped_column(Text, nullable=False)
    short_bio: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_bio: Mapped[str] = mapped_column(Text, nullable=False)
    short_bio: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)


class Participant(Base, TimestampMixin):
    __tablename__ = "participants"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_bio: Mapped[str] = mapped_column(Text, nullable=False)
    short_bio: Mapped[str] = mapped_column(Text, nullable=False)
    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)


class Program(Base, TimestampMixin):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_bio: Mapped[str] = mapped_column(Text, nullable=False)
    short_bio: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class ProfileSkill(Base, TimestampMixin):
    __tablename__ = "profile_skills"
    __table_args__ = (
        CheckConstraint("entity_type IN ('mentor', 'company', 'participant', 'program')"),
        UniqueConstraint("entity_type", "entity_id", "skill_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    skill: Mapped[Skill] = relationship()


class Match(Base, TimestampMixin):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("source_type IN ('mentor', 'company', 'participant', 'program')"),
        CheckConstraint("target_type IN ('mentor', 'company', 'participant', 'program')"),
        UniqueConstraint("match_type", "source_id", "target_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    match_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_name: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    explanation: Mapped[list[str]] = mapped_column(JSONB, default=list)
    shared_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(40), default="recommended")


class CompanyProgram(Base, TimestampMixin):
    __tablename__ = "company_programs"
    __table_args__ = (UniqueConstraint("company_id", "program_id"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    company: Mapped[Company] = relationship()
    program: Mapped[Program] = relationship()


class ParticipantProgram(Base, TimestampMixin):
    __tablename__ = "participant_programs"
    __table_args__ = (UniqueConstraint("participant_id", "program_id"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    participant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    participant: Mapped[Participant] = relationship()
    program: Mapped[Program] = relationship()
