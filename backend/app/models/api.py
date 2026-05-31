"""API request/response models."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .domain import SourceType, PersonRole, RiskLevel, UserProfile


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    user_profile_id: Optional[str] = None
    project_filter: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)
    weights: Optional[Dict[str, float]] = None
    include_rag_comparison: bool = True


class ScoreBreakdown(BaseModel):
    semantic: float
    temporal: float
    authority: float
    risk: float
    project: float
    final: float
    explanation: Dict[str, str] = Field(default_factory=dict)


class ScoredContext(BaseModel):
    id: str
    title: str
    content: str
    source_type: SourceType
    owner: str
    project: str
    risk_level: RiskLevel
    age_days: float
    created_at: datetime
    scores: ScoreBreakdown
    rank: int
    tags: List[str] = Field(default_factory=list)


class RAGResult(BaseModel):
    """Traditional RAG result using only semantic similarity."""
    id: str
    title: str
    content: str
    source_type: SourceType
    semantic_score: float
    rank: int


class AssembledPrompt(BaseModel):
    system_prompt: str
    user_prompt: str
    context_window_used: int
    context_items_count: int
    profile_adaptation: str


class QueryResponse(BaseModel):
    query: str
    query_id: str
    project_detected: Optional[str]
    selected_context: List[ScoredContext]
    assembled_prompt: AssembledPrompt
    rag_comparison: Optional[List[RAGResult]] = None
    processing_time_ms: float
    total_candidates: int


class ScoreRequest(BaseModel):
    context_id: str
    query: str
    user_profile_id: Optional[str] = None
    project: Optional[str] = None


class GraphNodeResponse(BaseModel):
    id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float = 1.0


class GraphResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]
    node_count: int
    edge_count: int


class ContextDetail(BaseModel):
    id: str
    title: str
    content: str
    source_type: SourceType
    created_at: datetime
    updated_at: datetime
    owner: str
    project: str
    importance: int
    risk_level: RiskLevel
    tags: List[str]
    related_nodes: List[GraphNodeResponse] = Field(default_factory=list)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    context_count: int = 0


class UserProfileResponse(BaseModel):
    id: str
    name: str
    role: PersonRole
    verbosity: str
    output_style: str
    risk_tolerance: str
