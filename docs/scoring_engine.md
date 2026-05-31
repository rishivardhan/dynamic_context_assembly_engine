# DCAE Scoring Engine Reference

## Overview

The DCAE scoring engine replaces single-dimension semantic ranking with a multi-dimensional composite score that models how enterprise knowledge should be weighted across five independent dimensions.

---

## 1. Composite Score Formula

```
FinalScore = (
    SemanticScore    × w_semantic    +
    TemporalScore    × w_temporal    +
    AuthorityScore   × w_authority   +
    RiskScore        × w_risk        +
    ProjectScore     × w_project
) × BehaviouralMultiplier
```

**Default weights:**

| Dimension   | Default Weight | Rationale |
|-------------|---------------|-----------|
| Semantic    | 0.30          | Most direct measure of query relevance |
| Temporal    | 0.25          | Recency is critical in operational enterprise context |
| Risk        | 0.20          | Risk-critical items must surface, even if not top semantic match |
| Authority   | 0.15          | Architectural decisions from senior roles carry more weight |
| Project     | 0.10          | Project scoping as a tiebreaker |

---

## 2. Temporal Relevance Engine

### Formula
```python
score = BaseWeight × exp(-λ × age_days)
```

### Decay Constants (λ)

| Source Type | λ (decay rate) | Half-score age |
|-------------|---------------|---------------|
| Standup | 0.30 | 2.3 days |
| Meeting Note | 0.15 | 4.6 days |
| Email | 0.10 | 6.9 days |
| Git Commit | 0.08 | 8.7 days |
| Sprint Report | 0.05 | 13.9 days |
| Jira Story | 0.04 | 17.3 days |
| Incident | 0.03 | 23.1 days |
| Architecture Decision | 0.002 | 347 days |
| Architecture Document | 0.002 | 347 days |
| Security Policy | 0.001 | 693 days |

**Key insight:** An ADR from 6 months ago still retains >70% of its temporal score, while a meeting note from 6 months ago scores near zero. This correctly models enterprise knowledge lifecycle.

---

## 3. Context Half-Life Engine

### Formula
```python
relevance = initial_weight × (0.5 ** (age_days / half_life_days))
```

### Half-Life Periods

| Context Type | Half-Life |
|-------------|-----------|
| Standup | 7 days |
| Meeting Note | 14 days |
| Email | 21 days |
| Sprint Report | 30 days |
| Git Commit | 60 days |
| Jira Story | 90 days |
| Incident | 90 days |
| Architecture Document | 730 days |
| Architecture Decision | 1095 days (3 years) |
| Security Policy | 1825 days (5 years) |

### Combination with Temporal Score
The two decay models are combined via geometric mean to produce a single temporal component:
```python
combined_temporal = math.sqrt(temporal_score × half_life_score)
```

This prevents double-penalisation while preserving the shape differences between the models.

---

## 4. Authority Scoring

### Role Weights

| Role | Raw Weight | Normalised Score |
|------|-----------|-----------------|
| Engineer | 1.0 | 0.333 |
| Lead | 1.5 | 0.500 |
| Architect | 2.0 | 0.667 |
| Director | 3.0 | 1.000 |

**Rationale:** An architectural decision record authored by a Principal Architect carries greater epistemic authority for architectural questions than the same document authored by a junior engineer, even if semantically identical.

---

## 5. Risk Scoring

### Risk Level Weights

| Risk Level | Raw Weight | Normalised Score |
|-----------|-----------|-----------------|
| LOW | 1.0 | 0.10 |
| MEDIUM | 3.0 | 0.30 |
| HIGH | 5.0 | 0.50 |
| CRITICAL | 10.0 | 1.00 |

**Effect:** A CRITICAL production incident from 2 weeks ago will score 10× higher on the risk dimension than a LOW-risk informational document, ensuring safety-critical information surfaces even if its semantic similarity is lower.

---

## 6. Project Relevance Scoring

### Matching Strategy

1. **Exact match** → 1.0 (case-insensitive)
2. **Substring match** (detected project ⊂ context project or vice versa) → 0.85
3. **Fuzzy match** above threshold (SequenceMatcher ratio ≥ 0.6) → 0.5–0.85 (scaled)
4. **No project detected** (query is project-agnostic) → 0.5 (neutral)
5. **No match** → 0.1

### Project Detection

The system detects the project from the query using the same three-tier matching strategy against all known project names. Example:
- Query: "What is the status of the Postgres migration?" → Detects: "Postgres Migration"
- Query: "Zero Trust network segmentation?" → Detects: "Zero Trust Security Framework"

---

## 7. Behavioural Overlay

### Source Preference Multipliers

| Condition | Multiplier |
|-----------|-----------|
| Source type in profile's preferred_sources | 1.2 |
| Source type in role's default preferences | 1.1 |
| Other source types | 0.9 |

### Role Source Preferences

| Role | Preferred Sources |
|------|-----------------|
| Engineer | git_commit, jira_story, incident, architecture_decision |
| Lead | sprint_report, jira_story, incident, meeting_note, architecture_decision |
| Architect | architecture_decision, architecture_document, incident, security_policy |
| Director | sprint_report, incident, architecture_document, meeting_note |

---

## 8. Explainability Output

Every scoring response includes per-dimension explanations:

```json
{
  "scores": {
    "semantic": 0.7823,
    "temporal": 0.4312,
    "authority": 0.6667,
    "risk": 0.5000,
    "project": 1.0000,
    "final": 0.6541,
    "explanation": {
      "temporal": "Age: 10.3 days | λ=0.03 | base=1.0 → score=0.7340",
      "half_life": "Half-life: 90.0d | Age: 10.3d | Halvings: 0.11 → score=0.9261",
      "authority": "Role: Architect | raw=2.0 | normalized=0.6667",
      "risk": "Risk: HIGH | raw=5.0 | normalized=0.5000",
      "project": "Exact match: 'Postgres Migration'",
      "final": "(0.782×0.30 + 0.431×0.25 + 0.667×0.15 + 0.500×0.20 + 1.000×0.10) × 1.10 = 0.6541"
    }
  }
}
```
