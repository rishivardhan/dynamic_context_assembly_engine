"""Unit tests for the risk scoring engine."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.risk import RiskScorer
from app.models.domain import RiskLevel


@pytest.fixture
def scorer():
    return RiskScorer()


class TestRiskScorer:

    def test_critical_highest(self, scorer):
        score, _ = scorer.score(RiskLevel.CRITICAL)
        assert score == 1.0

    def test_low_lowest(self, scorer):
        low, _ = scorer.score(RiskLevel.LOW)
        crit, _ = scorer.score(RiskLevel.CRITICAL)
        assert low < crit

    def test_hierarchy(self, scorer):
        low, _ = scorer.score(RiskLevel.LOW)
        med, _ = scorer.score(RiskLevel.MEDIUM)
        high, _ = scorer.score(RiskLevel.HIGH)
        crit, _ = scorer.score(RiskLevel.CRITICAL)
        assert low < med < high < crit

    def test_unknown_defaults_to_low(self, scorer):
        unk, _ = scorer.score("UNKNOWN")
        low, _ = scorer.score(RiskLevel.LOW)
        assert unk == low

    def test_explanation_contains_risk_level(self, scorer):
        _, explanation = scorer.score(RiskLevel.HIGH)
        assert 'HIGH' in explanation

    def test_score_range_zero_to_one(self, scorer):
        for level in RiskLevel:
            score, _ = scorer.score(level)
            assert 0 <= score <= 1
