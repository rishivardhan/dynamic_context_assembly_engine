"""Initialize database schema."""
import sys
import structlog
from app.db.postgres import Base, engine
from app.db.neo4j_client import Neo4jRepository

logger = structlog.get_logger()


def init_postgres():
    logger.info("Creating PostgreSQL schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL schema created.")


def init_neo4j():
    logger.info("Creating Neo4j indexes...")
    repo = Neo4jRepository()
    repo.create_schema_indexes()
    logger.info("Neo4j indexes created.")


if __name__ == "__main__":
    init_postgres()
    init_neo4j()
    logger.info("Database initialization complete.")
