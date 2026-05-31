"""Unit tests for the composite relevance scorer."""
import pytest
from datetime import datetime, timezone, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.composite import CompositeRelevanceScorer, ScoringWeights
from app.models.domain import SourceType, RiskLevel, PersonRole


@pytest.fixture
def scorer():
    return CompositeRelevanceScorer()


def ts_days_ago(days):
    return datetime.now(timezone.utc) - timedelta(days=days)


class TestCompositeRelevanceScorer:

    def test_returns_composite_score(self, scorer):
        result = scorer.score(
            semantic_score=0.8,
            source_type=SourceType.INCIDENT,
            created_at=ts_days_ago(5),
            owner_role=PersonRole.DIRECTOR,
            risk_level=RiskLevel.CRITICAL,
            context_project="Postgres Migration",
            detected_project="Postgres Migration",
        )
        assert 0 <= result.final <= 1.0

    def test_high_risk_critical_incident_ranks_higher_than_low(self, scorer):
        critical = scorer.score(
            semantic_score=0.5,
            source_type=SourceType.INCIDENT,
            created_at=ts_days_ago(2),
            owner_role=PersonRole.DIRECTOR,
            risk_level=RiskLevel.CRITICAL,
            context_project="Postgres Migration",
            detected_project="Postgres Migration",
        )
        low_risk = scorer.score(
            semantic_score=0.5,
            source_type=SourceType.MEETING_NOTE,
            created_at=ts_days_ago(100),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.LOW,
            context_project="Customer Portal",
            detected_project="Postgres Migration",
        )
        assert critical.final > low_risk.final

    def test_project_match_boosts_score(self, scorer):
        matched = scorer.score(
            semantic_score=0.6,
            source_type=SourceType.JIRA_STORY,
            created_at=ts_days_ago(10),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.MEDIUM,
            context_project="Postgres Migration",
            detected_project="Postgres Migration",
        )
        unmatched = scorer.score(
            semantic_score=0.6,
            source_type=SourceType.JIRA_STORY,
            created_at=ts_days_ago(10),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.MEDIUM,
            context_project="Customer Portal Redesign",
            detected_project="Postgres Migration",
        )
        assert matched.final > unmatched.final

    def test_architect_authority_boosts_over_engineer(self, scorer):
        architect = scorer.score(
            semantic_score=0.6,
            source_type=SourceType.ARCHITECTURE_DECISION,
            created_at=ts_days_ago(30),
            owner_role=PersonRole.ARCHITECT,
            risk_level=RiskLevel.LOW,
            context_project="X",
            detected_project=None,
        )
        engineer = scorer.score(
            semantic_score=0.6,
            source_type=SourceType.ARCHITECTURE_DECISION,
            created_at=ts_days_ago(30),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.LOW,
            context_project="X",
            detected_project=None,
        )
        assert architect.final > engineer.final

    def test_custom_weights_applied(self):
        weights = ScoringWeights(semantic=1.0, temporal=0.0, authority=0.0, risk=0.0, project=0.0)
        scorer = CompositeRelevanceScorer(weights=weights)
        result = scorer.score(
            semantic_score=0.9,
            source_type=SourceType.EMAIL,
            created_at=ts_days_ago(500),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.LOW,
            context_project="X",
            detected_project=None,
        )
        assert result.final > 0.8  # semantic dominated

    def test_all_score_components_present(self, scorer):
        result = scorer.score(
            semantic_score=0.7,
            source_type=SourceType.SPRINT_REPORT,
            created_at=ts_days_ago(14),
            owner_role=PersonRole.LEAD,
            risk_level=RiskLevel.MEDIUM,
            context_project="API Gateway Modernisation",
            detected_project="API Gateway Modernisation",
        )
        assert result.semantic > 0
        assert result.temporal >= 0
        assert result.authority > 0
        assert result.risk > 0
        assert result.project > 0
        assert result.final > 0

    def test_to_dict_returns_all_keys(self, scorer):
        result = scorer.score(
            semantic_score=0.5,
            source_type=SourceType.GIT_COMMIT,
            created_at=ts_days_ago(1),
            owner_role=PersonRole.ENGINEER,
            risk_level=RiskLevel.LOW,
            context_project="X",
            detected_project=None,
        )
        d = result.to_dict()
        for key in ("semantic", "temporal", "authority", "risk", "project", "final"):
            assert key in d
