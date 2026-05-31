"""Behavioral overlay engine — adapts prompt assembly to user profiles."""
from typing import Optional, List
from app.models.domain import UserProfile, PersonRole, SourceType


_VERBOSITY_INSTRUCTIONS = {
    "low": "Be concise. Use bullet points. Omit preamble.",
    "medium": "Provide clear, structured answers with relevant detail.",
    "high": "Provide comprehensive analysis with context, rationale, and implications.",
}

_STYLE_INSTRUCTIONS = {
    "technical": "Use technical terminology. Include implementation details, stack traces, and metrics.",
    "executive": "Focus on business impact, risks, timelines, and resource requirements. Avoid jargon.",
    "narrative": "Explain in flowing paragraphs suitable for documentation or reports.",
}

_RISK_FRAMING = {
    "low": "Present findings neutrally. Highlight opportunities.",
    "medium": "Flag risks but maintain balanced perspective.",
    "high": "Prioritise risk identification and mitigation strategies.",
}

_ROLE_SOURCE_PREFERENCES = {
    PersonRole.ENGINEER: [
        SourceType.GIT_COMMIT, SourceType.JIRA_STORY, SourceType.INCIDENT,
        SourceType.ARCHITECTURE_DECISION,
    ],
    PersonRole.LEAD: [
        SourceType.SPRINT_REPORT, SourceType.JIRA_STORY, SourceType.INCIDENT,
        SourceType.MEETING_NOTE, SourceType.ARCHITECTURE_DECISION,
    ],
    PersonRole.ARCHITECT: [
        SourceType.ARCHITECTURE_DECISION, SourceType.ARCHITECTURE_DOCUMENT,
        SourceType.INCIDENT, SourceType.SECURITY_POLICY,
    ],
    PersonRole.DIRECTOR: [
        SourceType.SPRINT_REPORT, SourceType.INCIDENT, SourceType.ARCHITECTURE_DOCUMENT,
        SourceType.MEETING_NOTE,
    ],
}


class BehavioralOverlayEngine:
    """
    Adjusts context selection and prompt generation based on the user's role,
    communication style, verbosity preference, and risk tolerance.
    """

    def build_system_prompt(self, profile: Optional[UserProfile]) -> str:
        if not profile:
            return (
                "You are an enterprise AI assistant. "
                "Answer based strictly on the provided context. "
                "If information is insufficient, say so explicitly."
            )

        parts = [
            "You are an enterprise AI assistant with deep knowledge of the organization's systems and processes.",
            f"You are responding to a {profile.role.value}.",
            _VERBOSITY_INSTRUCTIONS.get(profile.verbosity, _VERBOSITY_INSTRUCTIONS["medium"]),
            _STYLE_INSTRUCTIONS.get(profile.output_style, _STYLE_INSTRUCTIONS["technical"]),
            _RISK_FRAMING.get(profile.risk_tolerance, _RISK_FRAMING["medium"]),
            "Answer based strictly on the provided context. If information is insufficient, say so explicitly.",
        ]
        return " ".join(parts)

    def get_profile_adaptation_summary(self, profile: Optional[UserProfile]) -> str:
        if not profile:
            return "Default profile — no behavioral adaptation applied."
        return (
            f"Role={profile.role.value} | Verbosity={profile.verbosity} | "
            f"Style={profile.output_style} | Risk tolerance={profile.risk_tolerance}"
        )

    def apply_source_preference_boost(
        self,
        source_type: SourceType,
        profile: Optional[UserProfile],
    ) -> float:
        """Returns a multiplier [0.8, 1.2] based on profile source preferences."""
        if not profile:
            return 1.0
        preferred = _ROLE_SOURCE_PREFERENCES.get(profile.role, [])
        if source_type in (profile.preferred_sources or []):
            return 1.2
        if source_type in preferred:
            return 1.1
        return 0.9
