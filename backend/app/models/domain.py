"""Core domain models for DCAE."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class SourceType(str, Enum):
    JIRA_STORY = "jira_story"
    INCIDENT = "incident"
    ARCHITECTURE_DECISION = "architecture_decision"
    ARCHITECTURE_DOCUMENT = "architecture_document"
    MEETING_NOTE = "meeting_note"
    SPRINT_REPORT = "sprint_report"
    EMAIL = "email"
    GIT_COMMIT = "git_commit"
    SECURITY_POLICY = "security_policy"
    STANDUP = "standup"


class PersonRole(str, Enum):
    ENGINEER = "Engineer"
    LEAD = "Lead"
    ARCHITECT = "Architect"
    DIRECTOR = "Director"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RelationshipType(str, Enum):
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    IMPLEMENTED_BY = "implemented_by"
    CREATED_BY = "created_by"
    SUPERSEDES = "supersedes"
    BLOCKS = "blocks"
    REFERENCES = "references"


class ContextObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source_type: SourceType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: str
    project: str
    importance: int = Field(default=3, ge=1, le=5)
    risk_level: RiskLevel = RiskLevel.LOW
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class Person(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: PersonRole
    email: Optional[str] = None
    department: Optional[str] = None
    projects: List[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: str = "active"
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0
    metadata: dict = Field(default_factory=dict)


class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: PersonRole
    verbosity: str = "medium"  # low | medium | high
    output_style: str = "technical"  # technical | executive | narrative
    risk_tolerance: str = "medium"  # low | medium | high
    preferred_sources: List[SourceType] = Field(default_factory=list)
    current_project: Optional[str] = None
