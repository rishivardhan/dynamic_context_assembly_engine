"""Unit tests for the context half-life decay engine."""
import pytest
from datetime import datetime, timezone, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.halflife import ContextHalfLifeEngine
from app.models.domain import SourceType


@pytest.fixture
def engine():
    return ContextHalfLifeEngine()


def ts_days_ago(days):
    return datetime.now(timezone.utc) - timedelta(days=days)


class TestContextHalfLifeEngine:

    def test_at_creation_score_is_initial_weight(self, engine):
        score, _ = engine.score(SourceType.MEETING_NOTE, ts_days_ago(0), initial_weight=1.0)
        assert score > 0.99

    def test_at_half_life_score_is_half(self, engine):
        half_life = engine.get_half_life(SourceType.MEETING_NOTE)  # 14 days
        score, _ = engine.score(SourceType.MEETING_NOTE, ts_days_ago(half_life))
        assert abs(score - 0.5) < 0.02

    def test_at_double_half_life_score_is_quarter(self, engine):
        hl = engine.get_half_life(SourceType.SPRINT_REPORT)  # 30 days
        score, _ = engine.score(SourceType.SPRINT_REPORT, ts_days_ago(hl * 2))
        assert abs(score - 0.25) < 0.02

    def test_security_policy_long_half_life(self, engine):
        hl = engine.get_half_life(SourceType.SECURITY_POLICY)
        assert hl == 1825.0

    def test_adr_half_life_three_years(self, engine):
        hl = engine.get_half_life(SourceType.ARCHITECTURE_DECISION)
        assert hl == 1095.0

    def test_score_not_above_initial_weight(self, engine):
        score, _ = engine.score(SourceType.INCIDENT, ts_days_ago(0), initial_weight=0.8)
        assert score <= 0.8

    def test_explanation_contains_halflife(self, engine):
        _, explanation = engine.score(SourceType.MEETING_NOTE, ts_days_ago(7))
        assert 'Half-life' in explanation
