"""SQLAlchemy async ORM models for EcosystemGraph AI."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, DateTime,
    Float, ForeignKey, Integer, Numeric, String, Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Startup(Base):
    __tablename__ = "startups"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    name              = Column(String(255), nullable=False)
    industry          = Column(String(100), nullable=True)
    stage             = Column(String(50), nullable=True)
    description       = Column(Text, nullable=True)
    tags              = Column(ARRAY(String), nullable=True)
    clean_description = Column(Text, nullable=True)
    ai_confidence     = Column(Numeric(4, 3), default=0)
    enriched_at       = Column(DateTime(timezone=True), nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    match_logs  = relationship("MatchLog", back_populates="startup", cascade="all, delete-orphan")
    feedbacks   = relationship("Feedback", back_populates="startup", cascade="all, delete-orphan")


class Mentor(Base):
    __tablename__ = "mentors"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    name             = Column(String(255), nullable=False)
    expertise_tags   = Column(ARRAY(String), nullable=True)
    experience_years = Column(Integer, default=0)
    bio              = Column(Text, nullable=True)
    clean_bio        = Column(Text, nullable=True)
    enriched_at      = Column(DateTime(timezone=True), nullable=True)
    rating           = Column(Numeric(3, 2), default=0.00)
    total_feedback   = Column(Integer, default=0)
    available        = Column(Boolean, default=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    match_logs  = relationship("MatchLog", back_populates="mentor", cascade="all, delete-orphan")
    feedbacks   = relationship("Feedback", back_populates="mentor", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    focus_areas = Column(ARRAY(String), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class MatchLog(Base):
    __tablename__ = "match_logs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    mentor_id  = Column(Integer, ForeignKey("mentors.id",  ondelete="CASCADE"), nullable=False)
    score      = Column(Numeric(5, 4), nullable=False)
    reason     = Column(Text, nullable=True)
    status     = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    startup = relationship("Startup", back_populates="match_logs")
    mentor  = relationship("Mentor",  back_populates="match_logs")


class Feedback(Base):
    __tablename__ = "feedback"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id", ondelete="CASCADE"), nullable=True)
    mentor_id  = Column(Integer, ForeignKey("mentors.id",  ondelete="CASCADE"), nullable=False)
    action     = Column(String(20), nullable=False)
    comments   = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    startup = relationship("Startup", back_populates="feedbacks")
    mentor  = relationship("Mentor",  back_populates="feedbacks")
