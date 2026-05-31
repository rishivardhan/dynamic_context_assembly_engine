"""Authority scoring engine based on organizational role hierarchy."""
from typing import Dict, Optional
from app.models.domain import PersonRole


_AUTHORITY_WEIGHTS: Dict[str, float] = {
    PersonRole.ENGINEER: 1.0,
    PersonRole.LEAD: 1.5,
    PersonRole.ARCHITECT: 2.0,
    PersonRole.DIRECTOR: 3.0,
}

_MAX_AUTHORITY = max(_AUTHORITY_WEIGHTS.values())


class AuthorityScorer:
    """
    Weights context items by the organizational authority of their owner.

    Rationale: An architectural decision from a Principal Architect carries
    more decision-making authority than an engineer's comment, even if both
    are semantically similar to the query.
    """

    def __init__(self, person_repo: Optional[dict] = None):
        self._person_cache: Dict[str, str] = person_repo or {}

    def score(self, owner_role: Optional[str]) -> tuple[float, str]:
        raw = _AUTHORITY_WEIGHTS.get(owner_role, 1.0)
        normalized = raw / _MAX_AUTHORITY
        explanation = f"Role: {owner_role} | raw={raw} | normalized={normalized:.4f}"
        return normalized, explanation

    def score_from_name(self, owner_name: str, role_lookup: Dict[str, str]) -> tuple[float, str]:
        role = role_lookup.get(owner_name, PersonRole.ENGINEER)
        return self.score(role)

    def get_weight_for_role(self, role: str) -> float:
        return _AUTHORITY_WEIGHTS.get(role, 1.0)
