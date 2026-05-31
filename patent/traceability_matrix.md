# Patent Traceability Matrix: DCAE

**Reference:** DCAE-PAT-001  
**Date:** 2026-05-31

This matrix traces each implemented system feature to the corresponding patent claim(s) and the source code implementing it.

---

## Feature to Claim Traceability

| Feature | Patent Claim(s) | Implementation File | Key Method / Class |
|---------|----------------|--------------------|--------------------|
| Multi-dimensional composite scoring | Claim 1 (independent) | `engines/composite.py` | `CompositeRelevanceScorer.score()` |
| Temporal exponential decay | Claims 1(c)(i), 2 | `engines/temporal.py` | `TemporalRelevanceEngine.score()` |
| Source-type decay constants (λ map) | Claim 2 | `engines/temporal.py` | `_DECAY_MAP` dict |
| Context half-life decay | Claims 1(c)(ii), 3 | `engines/halflife.py` | `ContextHalfLifeEngine.score()` |
| Source-type half-life periods | Claim 3 | `engines/halflife.py` | `_HALF_LIFE_DAYS` dict |
| Geometric mean temporal combination | Claim 4 | `engines/composite.py` | `math.sqrt(temp * hl)` |
| Organisational authority weighting | Claims 1(c)(iii), 12 | `engines/authority.py` | `AuthorityScorer.score()` |
| Role hierarchy weight map | Claim 12 | `engines/authority.py` | `_AUTHORITY_WEIGHTS` dict |
| Risk-weighted prioritisation | Claims 1(c)(iv) | `engines/risk.py` | `RiskScorer.score()` |
| Risk level weight map | Claims 1(c)(iv) | `engines/risk.py` | `_RISK_WEIGHTS` dict |
| Project relevance scoring | Claims 1(c)(v), 6 | `engines/project_relevance.py` | `ProjectRelevanceScorer.score()` |
| Natural language project detection | Claim 6 | `engines/project_relevance.py` | `ProjectRelevanceScorer.detect_project()` |
| Fuzzy project matching | Claim 6 | `engines/project_relevance.py` | `SequenceMatcher` |
| Knowledge graph expansion | Claim 5 | `db/neo4j_client.py` | `Neo4jRepository.find_related_context()` |
| Neo4j graph traversal | Claim 5 | `db/neo4j_client.py` | Cypher MATCH … *1..2 |
| Behavioural overlay multiplier | Claims 1(e), 7 | `engines/behavioral.py` | `BehavioralOverlayEngine.apply_source_preference_boost()` |
| User profile source preferences | Claim 7 | `engines/behavioral.py` | `_ROLE_SOURCE_PREFERENCES` |
| Role-based prompt adaptation | Claims 1(h), 8 | `engines/behavioral.py` | `BehavioralOverlayEngine.build_system_prompt()` |
| Verbosity instruction selection | Claim 8 | `engines/behavioral.py` | `_VERBOSITY_INSTRUCTIONS` |
| Risk framing instruction | Claim 8 | `engines/behavioral.py` | `_RISK_FRAMING` |
| Explainable score decomposition | Claim 9 | `models/api.py`, `engines/composite.py` | `ScoreBreakdown.explanation` |
| RAG comparison output | Claim 10 | `services/context_assembler.py` | `_assemble_rag_comparison()` |
| Configurable scoring weights | Claim 11 | `engines/composite.py` | `ScoringWeights` dataclass |
| Weight override per query | Claim 11 | `api/routes.py`, `models/api.py` | `QueryRequest.weights` |
| pgvector relational+vector search | Claim 13 | `engines/semantic.py`, `db/postgres.py` | `SemanticSearchEngine.search()` |
| Composite context object model | Claim 14(a) | `models/domain.py` | `ContextObject` |
| Knowledge graph schema | Claim 14(b) | `db/neo4j_client.py` | Node/relationship creation |
| Scoring engine subsystem | Claim 14(c) | `engines/` | All engine classes |
| Prompt assembly subsystem | Claim 14(d) | `services/context_assembler.py` | `ContextAssembler._assemble_prompt()` |
| REST API | Claim 14(e) | `api/routes.py`, `main.py` | FastAPI endpoints |

---

## Claim to Feature Traceability

| Claim | Feature(s) Covered |
|-------|--------------------|
| Claim 1 (independent) | Complete DCAE pipeline: semantic search → multi-dim scoring → behavioural adaptation → prompt assembly |
| Claim 2 | Source-type-specific λ decay constants in `_DECAY_MAP` |
| Claim 3 | Source-type-specific half-life periods in `_HALF_LIFE_DAYS` |
| Claim 4 | Geometric mean combination of temporal and half-life scores |
| Claim 5 | Neo4j graph traversal for context expansion beyond semantic hits |
| Claim 6 | Three-tier project detection: exact, substring, fuzzy |
| Claim 7 | Profile-based source type preference multipliers |
| Claim 8 | Role/verbosity/risk-adapted system prompt construction |
| Claim 9 | Per-dimension score explanations returned in API response |
| Claim 10 | Parallel RAG baseline ranking returned in `rag_comparison` field |
| Claim 11 | `QueryRequest.weights` dict enabling per-query weight override |
| Claim 12 | Normalised authority score = role_weight / max_role_weight |
| Claim 13 | pgvector `<=>` cosine distance operator in PostgreSQL |
| Claim 14 | Complete system architecture: ingestion, graph, scoring, assembly, API |
| Claim 15 | Entire backend codebase as deployable software |

---

## Evidence of Reduction to Practice

All claimed features are demonstrated in the working proof-of-concept implementation:

- **Backend:** FastAPI application in `backend/` directory
- **Scoring engines:** `backend/app/engines/`
- **Database:** PostgreSQL (pgvector) + Neo4j 5.x
- **Sample data:** 40 enterprise context objects across 5 projects in `sample-data/`
- **Frontend:** React dashboard demonstrating claim 9 (explainable scores) and claim 10 (RAG comparison)
- **Tests:** 50+ unit tests in `tests/` validating scoring engine behaviour
- **Deployment:** Docker Compose configuration for reproducible local deployment

---

## Prior Art Distinction Summary

| DCAE Feature | Nearest Prior Art | Distinguishing Feature |
|-------------|-------------------|----------------------|
| Temporal decay scoring | Time-filtered RAG (binary cutoff) | Continuous exponential decay with source-type-specific constants |
| Half-life scoring | None identified | Novel radioactive decay analogy applied to enterprise knowledge types |
| Authority weighting | None in RAG literature | Organisational hierarchy as retrieval signal |
| Risk prioritisation | Risk-based filtering (binary) | Continuous risk weighting as scoring dimension |
| Project relevance | Metadata filtering | Fuzzy project detection + continuous relevance score |
| Behavioural overlay | Prompt personalisation (post-retrieval) | Re-weights retrieval at scoring time, not just prompt formatting |
| Graph expansion | Graph-RAG (Microsoft, 2024) | Combined with multi-dimensional scoring; Graph-RAG uses community summaries, DCAE uses relational context expansion |
| Composite scoring | Learning-to-rank (offline) | Online, configurable, real-time weighted combination |
| Explainability | Attention visualisation | Per-dimension score decomposition with natural language explanations |
