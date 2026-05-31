"""Unit tests for project relevance scoring."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.project_relevance import ProjectRelevanceScorer


@pytest.fixture
def scorer():
    return ProjectRelevanceScorer()


PROJECTS = [
    "Postgres Migration",
    "API Gateway Modernisation",
    "Zero Trust Security Framework",
    "Data Platform Modernisation",
    "Customer Portal Redesign",
]


class TestProjectRelevanceScorer:

    def test_exact_match_returns_one(self, scorer):
        score, _ = scorer.score("Postgres Migration", "Postgres Migration")
        assert score == 1.0

    def test_no_project_neutral_score(self, scorer):
        score, _ = scorer.score("Postgres Migration", None)
        assert score == 0.5

    def test_no_match_returns_low_score(self, scorer):
        score, _ = scorer.score("Customer Portal Redesign", "Postgres Migration")
        assert score < 0.5

    def test_case_insensitive_match(self, scorer):
        score, _ = scorer.score("postgres migration", "Postgres Migration")
        assert score >= 0.85

    def test_partial_match_scores_above_half(self, scorer):
        score, _ = scorer.score("Postgres Migration", "Postgres")
        assert score >= 0.5

    def test_detect_project_exact(self, scorer):
        detected = scorer.detect_project("What is the status of the Postgres Migration?", PROJECTS)
        assert detected == "Postgres Migration"

    def test_detect_project_api_gateway(self, scorer):
        detected = scorer.detect_project("Any API Gateway incidents this week?", PROJECTS)
        assert detected == "API Gateway Modernisation"

    def test_detect_project_zero_trust(self, scorer):
        detected = scorer.detect_project("Zero Trust security policies?", PROJECTS)
        assert detected == "Zero Trust Security Framework"

    def test_detect_project_none_for_irrelevant(self, scorer):
        detected = scorer.detect_project("What is the weather today?", PROJECTS)
        assert detected is None

    def test_explanation_returned(self, scorer):
        _, explanation = scorer.score("Postgres Migration", "Postgres Migration")
        assert explanation != ""
