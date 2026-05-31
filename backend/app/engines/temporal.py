"""Temporal relevance engine using exponential decay."""
import math
from datetime import datetime, timezone
from typing import Dict
from app.models.domain import SourceType
from app.config import settings


_DECAY_MAP: Dict[str, float] = {
    SourceType.STANDUP: 0.30,
    SourceType.MEETING_NOTE: 0.15,
    SourceType.SPRINT_REPORT: 0.05,
    SourceType.EMAIL: 0.10,
    SourceType.GIT_COMMIT: 0.08,
    SourceType.JIRA_STORY: 0.04,
    SourceType.INCIDENT: 0.03,
    SourceType.ARCHITECTURE_DECISION: 0.002,
    SourceType.ARCHITECTURE_DOCUMENT: 0.002,
    SourceType.SECURITY_POLICY: 0.001,
}

_BASE_WEIGHT: Dict[str, float] = {
    SourceType.STANDUP: 0.7,
    SourceType.MEETING_NOTE: 0.8,
    SourceType.SPRINT_REPORT: 0.9,
    SourceType.EMAIL: 0.7,
    SourceType.GIT_COMMIT: 0.8,
    SourceType.JIRA_STORY: 1.0,
    SourceType.INCIDENT: 1.0,
    SourceType.ARCHITECTURE_DECISION: 1.0,
    SourceType.ARCHITECTURE_DOCUMENT: 1.0,
    SourceType.SECURITY_POLICY: 1.0,
}


class TemporalRelevanceEngine:
    """
    Scores context items by temporal relevance using exponential decay.

    Formula: score = BaseWeight * exp(-lambda * age_days)

    Higher lambda means faster decay (operational artifacts like standups
    decay quickly; architectural decisions decay very slowly).
    """

    def score(self, source_type: SourceType, created_at: datetime) -> tuple[float, str]:
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)

        lam = _DECAY_MAP.get(source_type, 0.05)
        base = _BASE_WEIGHT.get(source_type, 1.0)
        score = base * math.exp(-lam * age_days)

        explanation = (
            f"Age: {age_days:.1f} days | λ={lam} | "
            f"base={base} → score={score:.4f}"
        )
        return min(1.0, score), explanation

    def get_age_days(self, created_at: datetime) -> float:
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return max(0.0, (now - created_at).total_seconds() / 86400.0)
