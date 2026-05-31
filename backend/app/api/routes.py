"""FastAPI route definitions."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.postgres import get_db, ContextObjectORM, ProjectORM, UserProfileORM
from app.db.neo4j_client import Neo4jRepository
from app.models.api import (
    QueryRequest, QueryResponse, GraphResponse, GraphNodeResponse,
    GraphEdgeResponse, ContextDetail, ProjectResponse, UserProfileResponse,
    ScoreRequest,
)
from app.models.domain import SourceType
from app.services.context_assembler import ContextAssembler
from app.engines.composite import CompositeRelevanceScorer
from app.engines.temporal import TemporalRelevanceEngine
import structlog

logger = structlog.get_logger()
router = APIRouter()
assembler = ContextAssembler()
temporal_engine = TemporalRelevanceEngine()


@router.post("/query", response_model=QueryResponse, tags=["DCAE"])
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Main DCAE endpoint. Assembles context using multi-dimensional scoring
    and returns scored context, assembled prompt, and optional RAG comparison.
    """
    try:
        return assembler.assemble(request, db)
    except Exception as e:
        logger.error("Query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score", tags=["DCAE"])
def score_context(request: ScoreRequest, db: Session = Depends(get_db)):
    """Score a single context item against a query."""
    obj = db.query(ContextObjectORM).filter(ContextObjectORM.id == request.context_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Context object not found")

    from app.db.postgres import PersonORM
    role_lookup = {p.name: p.role for p in db.query(PersonORM).all()}

    from app.engines.semantic import SemanticSearchEngine
    sem_engine = SemanticSearchEngine()
    q_emb = sem_engine.embed(request.query)
    if obj.embedding:
        import numpy as np
        sem_score = float(
            np.dot(q_emb, obj.embedding)
            / (np.linalg.norm(q_emb) * np.linalg.norm(obj.embedding) + 1e-9)
        )
    else:
        sem_score = 0.0

    scorer = CompositeRelevanceScorer()
    owner_role = role_lookup.get(obj.owner, "Engineer")
    result = scorer.score(
        semantic_score=sem_score,
        source_type=obj.source_type,
        created_at=obj.created_at,
        owner_role=owner_role,
        risk_level=obj.risk_level,
        context_project=obj.project,
        detected_project=request.project,
        user_profile=None,
    )
    return {
        "context_id": request.context_id,
        "query": request.query,
        "scores": result.to_dict(),
        "explanations": result.explanations,
    }


@router.get("/graph", response_model=GraphResponse, tags=["Graph"])
def get_graph():
    """Retrieve full knowledge graph for visualization."""
    neo4j = Neo4jRepository()
    data = neo4j.get_full_graph()
    nodes = [
        GraphNodeResponse(
            id=n["id"],
            label=n.get("properties", {}).get("title") or n.get("properties", {}).get("name") or n["id"],
            node_type=n["label"],
            properties=n.get("properties", {}),
        )
        for n in data["nodes"]
    ]
    edges = [
        GraphEdgeResponse(
            source=e["source"],
            target=e["target"],
            relationship=e["relationship"],
            weight=e.get("weight", 1.0),
        )
        for e in data["edges"]
    ]
    return GraphResponse(
        nodes=nodes, edges=edges,
        node_count=len(nodes), edge_count=len(edges),
    )


@router.get("/graph/node/{node_id}", response_model=GraphResponse, tags=["Graph"])
def get_node_neighborhood(node_id: str, depth: int = Query(default=2, ge=1, le=4)):
    """Get the subgraph around a specific node."""
    neo4j = Neo4jRepository()
    data = neo4j.get_node_neighborhood(node_id, depth)
    nodes = [
        GraphNodeResponse(
            id=n["id"],
            label=n.get("properties", {}).get("title") or n.get("properties", {}).get("name") or n["id"],
            node_type=n["label"],
            properties=n.get("properties", {}),
        )
        for n in data["nodes"]
    ]
    edges = [
        GraphEdgeResponse(
            source=e["source"],
            target=e["target"],
            relationship=e["relationship"],
            weight=e.get("weight", 1.0),
        )
        for e in data["edges"]
    ]
    return GraphResponse(
        nodes=nodes, edges=edges,
        node_count=len(nodes), edge_count=len(edges),
    )


@router.get("/projects", response_model=List[ProjectResponse], tags=["Data"])
def list_projects(db: Session = Depends(get_db)):
    """List all projects with context counts."""
    projects = db.query(ProjectORM).all()
    result = []
    for p in projects:
        count = db.query(ContextObjectORM).filter(
            ContextObjectORM.project == p.name
        ).count()
        result.append(ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            status=p.status,
            context_count=count,
        ))
    return result


@router.get("/context/{context_id}", response_model=ContextDetail, tags=["Data"])
def get_context(context_id: str, db: Session = Depends(get_db)):
    """Get a specific context object with graph relationships."""
    obj = db.query(ContextObjectORM).filter(ContextObjectORM.id == context_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Context object not found")

    neo4j = Neo4jRepository()
    neighborhood = neo4j.get_node_neighborhood(context_id, depth=1)
    related_nodes = [
        GraphNodeResponse(
            id=n["id"],
            label=n.get("properties", {}).get("title") or n.get("properties", {}).get("name") or n["id"],
            node_type=n["label"],
            properties=n.get("properties", {}),
        )
        for n in neighborhood["nodes"]
        if n["id"] != context_id
    ]

    return ContextDetail(
        id=obj.id,
        title=obj.title,
        content=obj.content,
        source_type=obj.source_type,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
        owner=obj.owner,
        project=obj.project,
        importance=obj.importance,
        risk_level=obj.risk_level,
        tags=obj.tags or [],
        related_nodes=related_nodes,
    )


@router.get("/profiles", response_model=List[UserProfileResponse], tags=["Data"])
def list_profiles(db: Session = Depends(get_db)):
    """List all user profiles."""
    profiles = db.query(UserProfileORM).all()
    return [
        UserProfileResponse(
            id=p.id, name=p.name, role=p.role,
            verbosity=p.verbosity, output_style=p.output_style,
            risk_tolerance=p.risk_tolerance,
        )
        for p in profiles
    ]


@router.get("/context", response_model=List[dict], tags=["Data"])
def list_context(
    source_type: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List context objects with optional filtering."""
    q = db.query(ContextObjectORM)
    if source_type:
        q = q.filter(ContextObjectORM.source_type == source_type)
    if project:
        q = q.filter(ContextObjectORM.project.ilike(f"%{project}%"))
    items = q.limit(limit).all()
    return [
        {
            "id": item.id,
            "title": item.title,
            "source_type": item.source_type,
            "project": item.project,
            "owner": item.owner,
            "risk_level": item.risk_level,
            "importance": item.importance,
            "created_at": item.created_at.isoformat(),
            "tags": item.tags or [],
        }
        for item in items
    ]


@router.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "DCAE Backend"}
