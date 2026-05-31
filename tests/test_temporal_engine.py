"""Unit tests for the temporal relevance engine."""
import math
import pytest
from datetime import datetime, timezone, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.temporal import TemporalRelevanceEngine
from app.models.domain import SourceType


@pytest.fixture
def engine():
    return TemporalRelevanceEngine()


def ts_days_ago(days: float) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


class TestTemporalRelevanceEngine:

    def test_fresh_meeting_note_scores_high(self, engine):
        score, _ = engine.score(SourceType.MEETING_NOTE, ts_days_ago(1))
        assert score > 0.7

    def test_old_meeting_note_scores_low(self, engine):
        score, _ = engine.score(SourceType.MEETING_NOTE, ts_days_ago(60))
        assert score < 0.1

    def test_adr_retains_relevance_after_one_year(self, engine):
        score, _ = engine.score(SourceType.ARCHITECTURE_DECISION, ts_days_ago(365))
        assert score > 0.48  # lambda=0.002 → exp(-0.002*365) ≈ 0.48

    def test_security_policy_very_slow_decay(self, engine):
        score, _ = engine.score(SourceType.SECURITY_POLICY, ts_days_ago(730))
        assert score > 0.23  # exp(-0.001*730) ≈ 0.48

    def test_score_never_exceeds_one(self, engine):
        score, _ = engine.score(SourceType.JIRA_STORY, ts_days_ago(0))
        assert score <= 1.0

    def test_score_never_negative(self, engine):
        score, _ = engine.score(SourceType.SPRINT_REPORT, ts_days_ago(1000))
        assert score >= 0.0

    def test_explanation_contains_age(self, engine):
        _, explanation = engine.score(SourceType.INCIDENT, ts_days_ago(10))
        assert '10' in explanation or '9' in explanation

    def test_meeting_decays_faster_than_adr(self, engine):
        days = 90
        meeting_score, _ = engine.score(SourceType.MEETING_NOTE, ts_days_ago(days))
        adr_score, _ = engine.score(SourceType.ARCHITECTURE_DECISION, ts_days_ago(days))
        assert meeting_score < adr_score

    def test_get_age_days_correct(self, engine):
        age = engine.get_age_days(ts_days_ago(7))
        assert abs(age - 7.0) < 0.1

    def test_naive_datetime_handled(self, engine):
        naive_dt = datetime.utcnow() - timedelta(days=5)
        score, _ = engine.score(SourceType.EMAIL, naive_dt)
        assert 0 <= score <= 1
