"""Seed the database with sample enterprise data."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import structlog

from app.db.postgres import SessionLocal, ContextObjectORM, PersonORM, ProjectORM, UserProfileORM
from app.db.neo4j_client import Neo4jRepository
from app.engines.semantic import SemanticSearchEngine

logger = structlog.get_logger()

DATA_FILE = Path(__file__).parent.parent.parent / "sample_data" / "enterprise_data.json"

# Fallback to sibling path when running from docker
if not DATA_FILE.exists():
    DATA_FILE = Path("/app/sample_data/enterprise_data.json")


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)


def seed():
    logger.info("Loading sample data", path=str(DATA_FILE))
    data = json.loads(DATA_FILE.read_text())

    db = SessionLocal()
    neo4j = Neo4jRepository()
    semantic = SemanticSearchEngine()

    try:
        # ── Projects ──────────────────────────────────────────────────────────
        logger.info("Seeding projects...")
        for p in data["projects"]:
            existing = db.query(ProjectORM).filter(ProjectORM.id == p["id"]).first()
            if not existing:
                db.add(ProjectORM(
                    id=p["id"],
                    name=p["name"],
                    description=p.get("description"),
                    status=p.get("status", "active"),
                    owner=p.get("owner"),
                    tags=p.get("tags", []),
                ))
                neo4j.create_project_node({
                    "id": p["id"],
                    "name": p["name"],
                    "description": p.get("description", ""),
                    "status": p.get("status", "active"),
                })
        db.commit()
        logger.info("Projects seeded", count=len(data["projects"]))

        # ── Persons ───────────────────────────────────────────────────────────
        logger.info("Seeding persons...")
        for p in data["persons"]:
            existing = db.query(PersonORM).filter(PersonORM.id == p["id"]).first()
            if not existing:
                db.add(PersonORM(
                    id=p["id"],
                    name=p["name"],
                    role=p["role"],
                    email=p.get("email"),
                    department=p.get("department"),
                    projects=p.get("projects", []),
                ))
                neo4j.create_person_node({
                    "id": p["id"],
                    "name": p["name"],
                    "role": p["role"],
                    "email": p.get("email", ""),
                    "department": p.get("department", ""),
                })
        db.commit()
        logger.info("Persons seeded", count=len(data["persons"]))

        # ── User Profiles ─────────────────────────────────────────────────────
        logger.info("Seeding user profiles...")
        for p in data["user_profiles"]:
            existing = db.query(UserProfileORM).filter(UserProfileORM.id == p["id"]).first()
            if not existing:
                db.add(UserProfileORM(
                    id=p["id"],
                    name=p["name"],
                    role=p["role"],
                    verbosity=p.get("verbosity", "medium"),
                    output_style=p.get("output_style", "technical"),
                    risk_tolerance=p.get("risk_tolerance", "medium"),
                    preferred_sources=p.get("preferred_sources", []),
                    current_project=p.get("current_project"),
                ))
        db.commit()
        logger.info("User profiles seeded", count=len(data["user_profiles"]))

        # ── Context Objects ───────────────────────────────────────────────────
        logger.info("Seeding context objects and generating embeddings...")
        texts_to_embed = []
        objects_to_embed = []

        for c in data["context_objects"]:
            existing = db.query(ContextObjectORM).filter(ContextObjectORM.id == c["id"]).first()
            if not existing:
                obj = ContextObjectORM(
                    id=c["id"],
                    title=c["title"],
                    content=c["content"],
                    source_type=c["source_type"],
                    created_at=_parse_dt(c["created_at"]),
                    updated_at=_parse_dt(c.get("updated_at", c["created_at"])),
                    owner=c["owner"],
                    project=c["project"],
                    importance=c.get("importance", 3),
                    risk_level=c.get("risk_level", "LOW"),
                    tags=c.get("tags", []),
                    metadata_={},
                )
                db.add(obj)
                texts_to_embed.append(f"{c['title']} {c['content']}")
                objects_to_embed.append(c["id"])

                neo4j.create_context_node({
                    "id": c["id"],
                    "title": c["title"],
                    "source_type": c["source_type"],
                    "project": c["project"],
                    "owner": c["owner"],
                    "risk_level": c.get("risk_level", "LOW"),
                    "importance": c.get("importance", 3),
                    "created_at": c["created_at"],
                })

        db.commit()

        # Batch embed
        if texts_to_embed:
            logger.info("Generating embeddings...", count=len(texts_to_embed))
            embeddings = semantic.embed_batch(texts_to_embed)
            for ctx_id, emb in zip(objects_to_embed, embeddings):
                obj = db.query(ContextObjectORM).filter(ContextObjectORM.id == ctx_id).first()
                if obj:
                    obj.embedding = emb
            db.commit()
            logger.info("Embeddings stored", count=len(embeddings))

        # ── Relationships ─────────────────────────────────────────────────────
        logger.info("Seeding relationships...")
        for r in data["relationships"]:
            try:
                neo4j.create_relationship(
                    r["source_id"], r["target_id"],
                    r["relationship_type"], r.get("weight", 1.0)
                )
            except Exception as e:
                logger.warning("Relationship creation failed", error=str(e), rel=r)
        logger.info("Relationships seeded", count=len(data["relationships"]))

        # Also link persons to context objects they own
        for c in data["context_objects"]:
            owner_person = next(
                (p for p in data["persons"] if p["name"] == c["owner"]), None
            )
            if owner_person:
                try:
                    neo4j.create_relationship(owner_person["id"], c["id"], "OWNS", 1.0)
                except Exception:
                    pass

        # Link context objects to projects
        for c in data["context_objects"]:
            project = next(
                (p for p in data["projects"] if p["name"] == c["project"]), None
            )
            if project:
                try:
                    neo4j.create_relationship(c["id"], project["id"], "BELONGS_TO", 1.0)
                except Exception:
                    pass

        logger.info("Database seeding complete.")

    except Exception as e:
        logger.error("Seeding failed", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
