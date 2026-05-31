"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.routes import router
from app.config import settings

logger = structlog.get_logger()

app = FastAPI(
    title="Dynamic Context Assembly Engine (DCAE)",
    description=(
        "An enterprise AI architecture that assembles context dynamically "
        "using semantic relevance, temporal decay, organizational authority, "
        "risk weighting, and behavioral overlays — surpassing traditional RAG."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("DCAE Backend starting up", environment=settings.environment)


@app.on_event("shutdown")
async def shutdown_event():
    from app.db.neo4j_client import close_driver
    close_driver()
    logger.info("DCAE Backend shut down")


@app.get("/")
def root():
    return {
        "name": "Dynamic Context Assembly Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
