"""Composite relevance scorer — combines all dimensions into final rank score."""
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime

from app.models.domain import SourceType, RiskLevel, UserProfile
from app.engines.temporal import TemporalRelevanceEngine
from app.engines.halflife import ContextHalfLifeEngine
from app.engines.authority import AuthorityScorer
from app.engines.risk import RiskScorer
from app.engines.project_relevance import ProjectRelevanceScorer
from app.engines.behavioral import BehavioralOverlayEngine


@dataclass
class CompositeScore:
    semantic: float = 0.0
    temporal: float = 0.0
    half_life: float = 0.0
    authority: float = 0.0
    risk: float = 0.0
    project: float = 0.0
    behavioral_multiplier: float = 1.0
    final: float = 0.0
    explanations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "semantic": round(self.semantic, 4),
            "temporal": round(self.temporal, 4),
            "half_life": round(self.half_life, 4),
            "authority": round(self.authority, 4),
            "risk": round(self.risk, 4),
            "project": round(self.project, 4),
            "behavioral_multiplier": round(self.behavioral_multiplier, 4),
            "final": round(self.final, 4),
        }


@dataclass
class ScoringWeights:
    semantic: float = 0.30
    temporal: float = 0.25
    authority: float = 0.15
    risk: float = 0.20
    project: float = 0.10


class CompositeRelevanceScorer:
    """
    Orchestrates all scoring dimensions into a single weighted relevance score.

    Final Score = (
        semantic  * w_semantic  +
        temporal  * w_temporal  +
        authority * w_authority +
        risk      * w_risk      +
        project   * w_project
    ) * behavioral_multiplier

    Half-life score is folded into temporal as a geometric mean to avoid
    double-counting while preserving the decay shape difference.
    """

    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.temporal_engine = TemporalRelevanceEngine()
        self.halflife_engine = ContextHalfLifeEngine()
        self.authority_scorer = AuthorityScorer()
        self.risk_scorer = RiskScorer()
        self.project_scorer = ProjectRelevanceScorer()
        self.behavioral_engine = BehavioralOverlayEngine()

    def score(
        self,
        semantic_score: float,
        source_type: SourceType,
        created_at: datetime,
        owner_role: str,
        risk_level: str,
        context_project: str,
        detected_project: Optional[str],
        user_profile: Optional[UserProfile] = None,
    ) -> CompositeScore:
        result = CompositeScore()
        result.semantic = semantic_score

        temp, temp_exp = self.temporal_engine.score(source_type, created_at)
        hl, hl_exp = self.halflife_engine.score(source_type, created_at)
        import math
        combined_temporal = math.sqrt(temp * hl)
        result.temporal = combined_temporal
        result.half_life = hl
        result.explanations["temporal"] = temp_exp
        result.explanations["half_life"] = hl_exp

        auth, auth_exp = self.authority_scorer.score(owner_role)
        result.authority = auth
        result.explanations["authority"] = auth_exp

        risk, risk_exp = self.risk_scorer.score(risk_level)
        result.risk = risk
        result.explanations["risk"] = risk_exp

        proj, proj_exp = self.project_scorer.score(context_project, detected_project)
        result.project = proj
        result.explanations["project"] = proj_exp

        behavioral_mult = self.behavioral_engine.apply_source_preference_boost(
            source_type, user_profile
        )
        result.behavioral_multiplier = behavioral_mult

        w = self.weights
        weighted = (
            result.semantic * w.semantic
            + combined_temporal * w.temporal
            + result.authority * w.authority
            + result.risk * w.risk
            + result.project * w.project
        )
        result.final = min(1.0, weighted * behavioral_mult)
        result.explanations["final"] = (
            f"({result.semantic:.3f}×{w.semantic} + "
            f"{combined_temporal:.3f}×{w.temporal} + "
            f"{result.authority:.3f}×{w.authority} + "
            f"{result.risk:.3f}×{w.risk} + "
            f"{result.project:.3f}×{w.project}) × {behavioral_mult:.2f}"
            f" = {result.final:.4f}"
        )
        return result
