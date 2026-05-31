"""Unit tests for the behavioral overlay engine."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.engines.behavioral import BehavioralOverlayEngine
from app.models.domain import UserProfile, PersonRole, SourceType


@pytest.fixture
def engine():
    return BehavioralOverlayEngine()


def make_profile(**kwargs) -> UserProfile:
    defaults = dict(
        id="p1", name="Test User", role=PersonRole.ENGINEER,
        verbosity="medium", output_style="technical", risk_tolerance="medium",
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


class TestBehavioralOverlayEngine:

    def test_no_profile_returns_default_prompt(self, engine):
        prompt = engine.build_system_prompt(None)
        assert 'enterprise AI assistant' in prompt

    def test_director_profile_executive_style(self, engine):
        profile = make_profile(role=PersonRole.DIRECTOR, output_style="executive")
        prompt = engine.build_system_prompt(profile)
        assert 'Director' in prompt or 'executive' in prompt.lower()

    def test_low_verbosity_concise_instruction(self, engine):
        profile = make_profile(verbosity="low")
        prompt = engine.build_system_prompt(profile)
        assert 'concise' in prompt.lower() or 'bullet' in prompt.lower()

    def test_high_verbosity_comprehensive_instruction(self, engine):
        profile = make_profile(verbosity="high")
        prompt = engine.build_system_prompt(profile)
        assert 'comprehensive' in prompt.lower() or 'analysis' in prompt.lower()

    def test_risk_framing_low_tolerance(self, engine):
        profile = make_profile(risk_tolerance="low")
        prompt = engine.build_system_prompt(profile)
        assert 'risk' in prompt.lower()

    def test_preferred_source_gets_boost(self, engine):
        profile = make_profile(
            preferred_sources=[SourceType.INCIDENT],
        )
        boost = engine.apply_source_preference_boost(SourceType.INCIDENT, profile)
        assert boost > 1.0

    def test_non_preferred_source_reduced(self, engine):
        profile = make_profile(role=PersonRole.DIRECTOR)
        mult = engine.apply_source_preference_boost(SourceType.GIT_COMMIT, profile)
        assert mult <= 1.0

    def test_no_profile_neutral_multiplier(self, engine):
        mult = engine.apply_source_preference_boost(SourceType.INCIDENT, None)
        assert mult == 1.0

    def test_profile_adaptation_summary_no_profile(self, engine):
        summary = engine.get_profile_adaptation_summary(None)
        assert 'Default' in summary

    def test_profile_adaptation_summary_with_profile(self, engine):
        profile = make_profile(role=PersonRole.ARCHITECT, verbosity="high")
        summary = engine.get_profile_adaptation_summary(profile)
        assert 'Architect' in summary
        assert 'high' in summary
