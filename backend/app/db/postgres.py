"""PostgreSQL connection and ORM models."""
from sqlalchemy import (
    create_engine, Column, String, Text, DateTime, Integer,
    Float, JSON, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import Generator
from app.config import settings
from app.models.domain import SourceType, RiskLevel


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class ContextObjectORM(Base):
    __tablename__ = "context_objects"

    id = Column(String, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(SAEnum(SourceType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(200), nullable=False)
    project = Column(String(200), nullable=False)
    importance = Column(Integer, default=3)
    risk_level = Column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    tags = Column(JSON, default=list)
    metadata_ = Column("metadata", JSON, default=dict)
    embedding = Column(Vector(384), nullable=True)


class PersonORM(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)
    email = Column(String(200))
    department = Column(String(200))
    projects = Column(JSON, default=list)


class ProjectORM(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    owner = Column(String(200))
    tags = Column(JSON, default=list)


class UserProfileORM(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)
    verbosity = Column(String(20), default="medium")
    output_style = Column(String(50), default="technical")
    risk_tolerance = Column(String(20), default="medium")
    preferred_sources = Column(JSON, default=list)
    current_project = Column(String(200))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
