"""Semantic search engine using SentenceTransformers and pgvector."""
from typing import List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.postgres import ContextObjectORM
import structlog

logger = structlog.get_logger()

_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading embedding model", model=settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


class SemanticSearchEngine:
    """
    Generates dense vector embeddings for semantic similarity search.

    Uses cosine similarity via pgvector. Semantic score is ONE component
    of the composite DCAE score — not the sole ranking criterion.
    """

    def embed(self, text: str) -> List[float]:
        model = get_model()
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()

    def search(
        self,
        query: str,
        db: Session,
        top_k: int = 20,
        project_filter: Optional[str] = None,
    ) -> List[Tuple[ContextObjectORM, float]]:
        query_embedding = self.embed(query)
        embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        filters = "WHERE co.embedding IS NOT NULL"
        if project_filter:
            filters += f" AND LOWER(co.project) LIKE LOWER('%{project_filter}%')"

        sql = text(f"""
            SELECT co.id,
                   1 - (co.embedding <=> '{embedding_str}'::vector) AS similarity
            FROM context_objects co
            {filters}
            ORDER BY co.embedding <=> '{embedding_str}'::vector
            LIMIT :top_k
        """)

        result = db.execute(sql, {"top_k": top_k})
        rows = result.fetchall()

        id_score_map = {row[0]: max(0.0, float(row[1])) for row in rows}
        if not id_score_map:
            return []

        orm_objects = (
            db.query(ContextObjectORM)
            .filter(ContextObjectORM.id.in_(id_score_map.keys()))
            .all()
        )

        return sorted(
            [(obj, id_score_map[obj.id]) for obj in orm_objects],
            key=lambda x: x[1],
            reverse=True,
        )

    def update_embedding(self, context_id: str, content: str, db: Session) -> None:
        embedding = self.embed(content)
        obj = db.query(ContextObjectORM).filter(ContextObjectORM.id == context_id).first()
        if obj:
            obj.embedding = embedding
            db.commit()
