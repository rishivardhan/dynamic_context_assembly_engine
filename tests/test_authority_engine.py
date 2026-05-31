"""Unit tests for the authority scoring engine."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.authority import AuthorityScorer
from app.models.domain import PersonRole


@pytest.fixture
def scorer():
    return AuthorityScorer()


class TestAuthorityScorer:

    def test_director_highest(self, scorer):
        score, _ = scorer.score(PersonRole.DIRECTOR)
        assert score == 1.0

    def test_engineer_lowest(self, scorer):
        eng_score, _ = scorer.score(PersonRole.ENGINEER)
        dir_score, _ = scorer.score(PersonRole.DIRECTOR)
        assert eng_score < dir_score

    def test_architect_above_engineer(self, scorer):
        eng, _ = scorer.score(PersonRole.ENGINEER)
        arch, _ = scorer.score(PersonRole.ARCHITECT)
        assert arch > eng

    def test_lead_above_engineer(self, scorer):
        eng, _ = scorer.score(PersonRole.ENGINEER)
        lead, _ = scorer.score(PersonRole.LEAD)
        assert lead > eng

    def test_hierarchy_order(self, scorer):
        engineer, _ = scorer.score(PersonRole.ENGINEER)
        lead, _ = scorer.score(PersonRole.LEAD)
        architect, _ = scorer.score(PersonRole.ARCHITECT)
        director, _ = scorer.score(PersonRole.DIRECTOR)
        assert engineer < lead < architect < director

    def test_unknown_role_defaults_to_engineer(self, scorer):
        score, _ = scorer.score("UnknownRole")
        eng, _ = scorer.score(PersonRole.ENGINEER)
        assert score == eng / (3.0 / 1.0)  # normalized

    def test_normalized_max_is_one(self, scorer):
        score, _ = scorer.score(PersonRole.DIRECTOR)
        assert score == 1.0

    def test_explanation_contains_role(self, scorer):
        _, explanation = scorer.score(PersonRole.ARCHITECT)
        assert 'Architect' in explanation
