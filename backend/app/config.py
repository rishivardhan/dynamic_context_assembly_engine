from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class ScoringWeights(BaseSettings):
    semantic: float = 0.30
    temporal: float = 0.25
    authority: float = 0.15
    risk: float = 0.20
    project: float = 0.10

    model_config = {"env_prefix": "WEIGHT_"}


class TemporalDecayConfig(BaseSettings):
    standup: float = 0.30
    meeting_note: float = 0.15
    sprint_report: float = 0.05
    email: float = 0.10
    git_commit: float = 0.08
    jira_story: float = 0.04
    incident: float = 0.03
    architecture_decision: float = 0.002
    architecture_document: float = 0.002
    security_policy: float = 0.001

    model_config = {"env_prefix": "DECAY_"}


class HalfLifeConfig(BaseSettings):
    meeting_note: float = 14.0
    sprint_report: float = 30.0
    email: float = 21.0
    git_commit: float = 60.0
    jira_story: float = 90.0
    incident: float = 90.0
    architecture_decision: float = 1095.0
    architecture_document: float = 730.0
    security_policy: float = 1825.0

    model_config = {"env_prefix": "HALFLIFE_"}


class Settings(BaseSettings):
    database_url: str = "postgresql://dcae:dcae_secret@localhost:5432/dcae_db"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "dcae_neo4j_secret"
    environment: str = "development"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    log_level: str = "INFO"
    top_k_semantic: int = 20
    top_k_final: int = 10
    max_prompt_tokens: int = 4096

    model_config = {"env_file": ".env", "extra": "allow"}

    @property
    def weights(self) -> ScoringWeights:
        return ScoringWeights()

    @property
    def temporal_decay(self) -> TemporalDecayConfig:
        return TemporalDecayConfig()

    @property
    def half_life(self) -> HalfLifeConfig:
        return HalfLifeConfig()


settings = Settings()
