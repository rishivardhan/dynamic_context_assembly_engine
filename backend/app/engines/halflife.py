"""Context half-life decay engine."""
from datetime import datetime, timezone
from typing import Dict
from app.models.domain import SourceType


_HALF_LIFE_DAYS: Dict[str, float] = {
    SourceType.STANDUP: 7.0,
    SourceType.MEETING_NOTE: 14.0,
    SourceType.SPRINT_REPORT: 30.0,
    SourceType.EMAIL: 21.0,
    SourceType.GIT_COMMIT: 60.0,
    SourceType.JIRA_STORY: 90.0,
    SourceType.INCIDENT: 90.0,
    SourceType.ARCHITECTURE_DECISION: 1095.0,
    SourceType.ARCHITECTURE_DOCUMENT: 730.0,
    SourceType.SECURITY_POLICY: 1825.0,
}


class ContextHalfLifeEngine:
    """
    Models information decay using radioactive half-life analogy.

    Formula: relevance = InitialWeight * (0.5 ^ (age_days / half_life_days))

    At age == half_life_days, the score halves.
    At age == 2 * half_life_days, the score is 25% of initial.
    """

    def score(
        self, source_type: SourceType, created_at: datetime, initial_weight: float = 1.0
    ) -> tuple[float, str]:
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
        half_life = _HALF_LIFE_DAYS.get(source_type, 30.0)

        score = initial_weight * (0.5 ** (age_days / half_life))

        explanation = (
            f"Half-life: {half_life}d | Age: {age_days:.1f}d | "
            f"Halvings: {age_days/half_life:.2f} → score={score:.4f}"
        )
        return min(1.0, score), explanation

    def get_half_life(self, source_type: SourceType) -> float:
        return _HALF_LIFE_DAYS.get(source_type, 30.0)
