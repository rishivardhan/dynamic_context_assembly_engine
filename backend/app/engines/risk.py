"""Risk scoring engine — high-risk items are prioritised in context assembly."""
from typing import Dict
from app.models.domain import RiskLevel


_RISK_WEIGHTS: Dict[str, float] = {
    RiskLevel.LOW: 1.0,
    RiskLevel.MEDIUM: 3.0,
    RiskLevel.HIGH: 5.0,
    RiskLevel.CRITICAL: 10.0,
}

_MAX_RISK = max(_RISK_WEIGHTS.values())


class RiskScorer:
    """
    Prioritises context items with higher risk levels.

    Production incidents (CRITICAL/HIGH) surface above low-risk documentation
    when the query concerns system stability or production issues.
    """

    def score(self, risk_level: str) -> tuple[float, str]:
        raw = _RISK_WEIGHTS.get(risk_level, 1.0)
        normalized = raw / _MAX_RISK
        explanation = f"Risk: {risk_level} | raw={raw} | normalized={normalized:.4f}"
        return normalized, explanation

    def get_weight(self, risk_level: str) -> float:
        return _RISK_WEIGHTS.get(risk_level, 1.0)
