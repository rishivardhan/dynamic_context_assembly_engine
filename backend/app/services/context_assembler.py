"""Dynamic Context Assembly Engine — core orchestration service."""
import time
import uuid
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.config import settings
from app.models.domain import UserProfile, SourceType, RiskLevel, PersonRole
from app.models.api import (
    QueryResponse, ScoredContext, ScoreBreakdown, AssembledPrompt,
    RAGResult, QueryRequest,
)
from app.db.postgres import ContextObjectORM, PersonORM, ProjectORM, UserProfileORM
from app.db.neo4j_client import Neo4jRepository
from app.engines.semantic import SemanticSearchEngine
from app.engines.composite import CompositeRelevanceScorer, ScoringWeights
from app.engines.project_relevance import ProjectRelevanceScorer
from app.engines.behavioral import BehavioralOverlayEngine
from app.engines.temporal import TemporalRelevanceEngine
import structlog

logger = structlog.get_logger()


class ContextAssembler:
    """
    Orchestrates the full DCAE pipeline:

    1. Intent + project detection
    2. Semantic candidate retrieval (pgvector)
    3. Graph-based relationship expansion (Neo4j)
    4. Multi-dimensional scoring (composite engine)
    5. Behavioral adaptation
    6. Prompt assembly
    7. Optional RAG comparison
    """

    def __init__(self):
        self.semantic_engine = SemanticSearchEngine()
        self.project_scorer = ProjectRelevanceScorer()
        self.behavioral_engine = BehavioralOverlayEngine()
        self.temporal_engine = TemporalRelevanceEngine()
        self.neo4j = Neo4jRepository()

    def assemble(self, request: QueryRequest, db: Session) -> QueryResponse:
        t_start = time.monotonic()
        query_id = str(uuid.uuid4())

        # 1. Load user profile
        profile = self._load_profile(request.user_profile_id, db)

        # 2. Detect project from query
        known_projects = [p.name for p in db.query(ProjectORM).all()]
        detected_project = request.project_filter or self.project_scorer.detect_project(
            request.query, known_projects
        )
        logger.info("Project detected", project=detected_project, query=request.query[:60])

        # 3. Semantic candidate retrieval
        semantic_hits = self.semantic_engine.search(
            request.query, db, top_k=settings.top_k_semantic
        )
        logger.info("Semantic candidates", count=len(semantic_hits))

        # 4. Graph expansion — include related context not in top semantic hits
        if semantic_hits:
            top_ids = [obj.id for obj, _ in semantic_hits[:5]]
            graph_ids: set = set()
            for ctx_id in top_ids:
                related = self.neo4j.find_related_context(ctx_id)
                graph_ids.update(related)
            graph_ids -= {obj.id for obj, _ in semantic_hits}

            if graph_ids:
                graph_objects = (
                    db.query(ContextObjectORM)
                    .filter(ContextObjectORM.id.in_(graph_ids))
                    .limit(10)
                    .all()
                )
                for go in graph_objects:
                    if go.embedding:
                        q_emb = self.semantic_engine.embed(request.query)
                        import numpy as np
                        sim = float(np.dot(q_emb, go.embedding) /
                                    (np.linalg.norm(q_emb) * np.linalg.norm(go.embedding) + 1e-9))
                    else:
                        sim = 0.1
                    semantic_hits.append((go, sim))

        # 5. Load role lookup for authority scoring
        role_lookup = {
            p.name: p.role for p in db.query(PersonORM).all()
        }

        # 6. Build custom weights if provided
        weights = None
        if request.weights:
            weights = ScoringWeights(**{
                k: v for k, v in request.weights.items()
                if k in ("semantic", "temporal", "authority", "risk", "project")
            })

        scorer = CompositeRelevanceScorer(weights=weights)

        # 7. Score all candidates
        scored: List[tuple] = []
        for obj, sem_score in semantic_hits:
            owner_role = role_lookup.get(obj.owner, PersonRole.ENGINEER)
            composite = scorer.score(
                semantic_score=sem_score,
                source_type=obj.source_type,
                created_at=obj.created_at,
                owner_role=owner_role,
                risk_level=obj.risk_level,
                context_project=obj.project,
                detected_project=detected_project,
                user_profile=profile,
            )
            scored.append((obj, composite))

        # 8. Sort and take top-k
        scored.sort(key=lambda x: x[1].final, reverse=True)
        top_scored = scored[:request.top_k]

        # 9. Build ScoredContext results
        selected_context = []
        for rank, (obj, comp) in enumerate(top_scored, start=1):
            age_days = self.temporal_engine.get_age_days(obj.created_at)
            breakdown = ScoreBreakdown(
                semantic=round(comp.semantic, 4),
                temporal=round(comp.temporal, 4),
                authority=round(comp.authority, 4),
                risk=round(comp.risk, 4),
                project=round(comp.project, 4),
                final=round(comp.final, 4),
                explanation=comp.explanations,
            )
            selected_context.append(ScoredContext(
                id=obj.id,
                title=obj.title,
                content=obj.content,
                source_type=obj.source_type,
                owner=obj.owner,
                project=obj.project,
                risk_level=obj.risk_level,
                age_days=round(age_days, 1),
                created_at=obj.created_at,
                scores=breakdown,
                rank=rank,
                tags=obj.tags or [],
            ))

        # 10. Assemble prompt
        assembled = self._assemble_prompt(request.query, selected_context, profile)

        # 11. RAG comparison (semantic-only baseline)
        rag_results = None
        if request.include_rag_comparison:
            rag_results = [
                RAGResult(
                    id=obj.id,
                    title=obj.title,
                    content=obj.content,
                    source_type=obj.source_type,
                    semantic_score=round(sem_score, 4),
                    rank=rank,
                )
                for rank, (obj, sem_score) in enumerate(
                    sorted(semantic_hits, key=lambda x: x[1], reverse=True)[:request.top_k],
                    start=1,
                )
            ]

        elapsed_ms = (time.monotonic() - t_start) * 1000

        return QueryResponse(
            query=request.query,
            query_id=query_id,
            project_detected=detected_project,
            selected_context=selected_context,
            assembled_prompt=assembled,
            rag_comparison=rag_results,
            processing_time_ms=round(elapsed_ms, 2),
            total_candidates=len(semantic_hits),
        )

    def _load_profile(self, profile_id: Optional[str], db: Session) -> Optional[UserProfile]:
        if not profile_id:
            return None
        orm = db.query(UserProfileORM).filter(UserProfileORM.id == profile_id).first()
        if not orm:
            return None
        return UserProfile(
            id=orm.id,
            name=orm.name,
            role=orm.role,
            verbosity=orm.verbosity,
            output_style=orm.output_style,
            risk_tolerance=orm.risk_tolerance,
            preferred_sources=orm.preferred_sources or [],
            current_project=orm.current_project,
        )

    def _assemble_prompt(
        self,
        query: str,
        context_items: List[ScoredContext],
        profile: Optional[UserProfile],
    ) -> AssembledPrompt:
        system_prompt = self.behavioral_engine.build_system_prompt(profile)
        adaptation_summary = self.behavioral_engine.get_profile_adaptation_summary(profile)

        context_blocks = []
        total_chars = 0
        max_chars = settings.max_prompt_tokens * 4  # rough char estimate

        for item in context_items:
            block = (
                f"[{item.source_type.value.upper()}] {item.title}\n"
                f"Project: {item.project} | Owner: {item.owner} | "
                f"Risk: {item.risk_level.value} | Age: {item.age_days:.0f}d | "
                f"Score: {item.scores.final:.3f}\n"
                f"{item.content}\n"
                f"---"
            )
            if total_chars + len(block) > max_chars:
                break
            context_blocks.append(block)
            total_chars += len(block)

        context_section = "\n\n".join(context_blocks)
        user_prompt = f"""Based on the following enterprise context, answer this question:

QUESTION: {query}

CONTEXT:
{context_section}

Please provide your answer based solely on the context above."""

        return AssembledPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context_window_used=total_chars // 4,
            context_items_count=len(context_blocks),
            profile_adaptation=adaptation_summary,
        )
