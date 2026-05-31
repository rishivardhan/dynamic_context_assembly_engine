# Novelty Analysis: Dynamic Context Assembly Engine (DCAE)

**Prepared for:** European Patent Prosecution  
**Date:** 2026-05-31  
**Reference:** DCAE-PAT-001

---

## 1. Field of Invention

The invention relates to methods and systems for dynamic, multi-dimensional context assembly for large language model (LLM) prompt construction in enterprise knowledge management systems. More specifically, the invention pertains to a scoring architecture that combines semantic similarity, temporal relevance decay, organisational authority weighting, risk prioritisation, project relevance mapping, and behavioural user profiling to produce an explainable, ranked context set for AI-assisted enterprise query resolution.

---

## 2. Background: Limitations of Prior Art

### 2.1 Retrieval Augmented Generation (RAG)

The current state of the art for providing external knowledge to large language models is Retrieval Augmented Generation (RAG), as described in Lewis et al. (2020) "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (arXiv:2005.11401) and subsequently implemented in systems such as LangChain, LlamaIndex, and numerous commercial products.

**Core limitation of RAG:** Context retrieval in RAG systems is performed exclusively through semantic vector similarity (cosine similarity of dense embeddings). Documents or knowledge objects are ranked by how closely their vector representation matches the query vector.

### 2.2 Specific Limitations of Semantic-Only Retrieval

**2.2.1 Temporal blindness:** RAG treats a 5-year-old deprecated architecture document identically to a meeting note recorded yesterday. In enterprise environments, recency is often as important as semantic relevance. A security policy superseded 3 years ago may score highly on semantic similarity while being entirely obsolete.

**2.2.2 Organisational authority ignorance:** RAG assigns equal weight to a junior engineer's comment and a Principal Architect's architectural decision record, even when those documents are semantically equivalent. Enterprise decision-making requires understanding the organisational authority behind information.

**2.2.3 Risk indifference:** RAG does not differentiate between low-risk informational documents and critical production incident reports. When querying about system stability, a critical incident from last week should rank higher than semantically similar but low-risk documentation.

**2.2.4 Project context blindness:** RAG does not understand that a query about "the migration" is most relevantly answered by documents associated with the specific active migration project, rather than any historically similar migration.

**2.2.5 User context ignorance:** RAG generates identical context sets regardless of whether the recipient is a software engineer, an engineering director, or a security architect, each of whom requires fundamentally different information granularity, framing, and source types.

**2.2.6 No information half-life modelling:** RAG has no model of information decay — the concept that the relevance of operational knowledge (meeting notes, sprint reports) decays rapidly, while architectural knowledge (architecture decision records, security policies) retains relevance over years.

### 2.3 Existing Multi-Criteria Retrieval Approaches

Prior work on multi-criteria retrieval (e.g., BM25 hybrid retrieval, ColBERT reranking, HyDE hypothetical document embeddings) addresses vocabulary mismatch and retrieval precision but remains confined to lexical and semantic dimensions. None of the prior art addresses the enterprise-specific dimensions of temporal decay, authority hierarchy, risk classification, or behavioural user profiling as described herein.

---

## 3. The Inventive Step: Dynamic Context Assembly Engine

### 3.1 Core Innovation

The DCAE introduces a **multi-dimensional composite relevance scoring architecture** wherein context objects from an enterprise knowledge graph are scored across seven independent dimensions, and the resulting weighted composite score determines context assembly for LLM prompt construction.

The composite relevance formula is:

```
FinalScore = (
    SemanticScore    × w_semantic    +
    TemporalScore    × w_temporal    +
    AuthorityScore   × w_authority   +
    RiskScore        × w_risk        +
    ProjectScore     × w_project
) × BehaviouralMultiplier
```

Where all weights are configurable per deployment and query context.

### 3.2 Novel Sub-Components

#### 3.2.1 Temporal Relevance Engine (Novel)

Applies source-type-specific exponential decay to model information freshness:

```
TemporalScore = BaseWeight × exp(−λ × age_days)
```

The innovation lies in **source-type-differentiated decay constants (λ)**. Operational artefacts (standups, meeting notes) decay with high λ; architectural artefacts (ADRs, security policies) decay with minimal λ. This accurately models how information ages differently in enterprise environments.

This is fundamentally different from time-filtered retrieval (which binary-excludes documents) — DCAE applies a continuous decay that preserves very recent operational knowledge while retaining long-lived architectural knowledge.

#### 3.2.2 Context Half-Life Engine (Novel)

Models information relevance decay using a radioactive half-life analogy:

```
Relevance = InitialWeight × (0.5 ^ (age_days / HalfLifeDays))
```

The innovation is the **explicit mapping of enterprise knowledge types to information half-lives** derived from organisational knowledge management principles. Meeting notes have a 14-day half-life; architectural decisions have a 3-year half-life. This dual-decay model (combined with the temporal engine via geometric mean) produces more stable scoring than either model alone.

#### 3.2.3 Organisational Authority Weighting (Novel)

Maps the creating role to a normalised authority score:

```
AuthorityScore = RoleWeight / MaxRoleWeight
```

The innovation is the application of **organisational hierarchy as a relevance signal** in AI context retrieval. An architectural decision authored by a Principal Architect is given greater epistemic authority than an equivalent document authored by a junior engineer. This maps the human organisational trust model onto the AI retrieval system.

#### 3.2.4 Risk-Weighted Context Prioritisation (Novel)

Maps document risk classification to a retrieval priority score. Critical production incidents surface above low-risk documentation when queries concern system stability. The innovation is the **automatic, risk-aware context promotion** — ensuring that safety-critical information is never deprioritised by semantic distance alone.

#### 3.2.5 Project Relevance Mapping with Graph-Based Expansion (Novel)

Detects the project context from the natural language query and boosts context objects associated with that project. Combined with Neo4j knowledge graph traversal, the system surfaces **graph-adjacent context objects** not directly reachable by semantic search but relationally connected to the most relevant results. This graph-aware context expansion is not present in any prior RAG implementation.

#### 3.2.6 Behavioural Overlay Engine (Novel)

Adapts both context selection (via source preference multipliers) and prompt assembly (system prompt construction) based on a user profile capturing role, verbosity preference, communication style, and risk tolerance. The innovation is the **integration of user behavioural profiles into context ranking** — not merely prompt formatting, but actual re-weighting of source types based on what the user's role renders most useful.

### 3.3 Explainability

Every scoring decision in DCAE is decomposed and surfaced to the user, including:
- Individual dimension scores
- The explanation for each score (e.g., "Age: 14.3 days | λ=0.15 → score=0.117")
- The final weighted composite

This **explainable context selection** is a distinct departure from black-box RAG retrieval and enables audit trails for regulated industries.

---

## 4. Non-Obvious Nature of the Invention

The combination of the above dimensions is non-obvious for the following reasons:

1. **Cross-disciplinary synthesis:** The invention combines techniques from information retrieval (semantic search), organisational theory (authority hierarchies), reliability engineering (risk classification), knowledge management (information half-life), and human-computer interaction (behavioural adaptation) into a single coherent scoring framework.

2. **Counter-intuitive weighting:** In standard RAG, semantic relevance is the sole determinant. The invention demonstrates cases where a semantically dissimilar but temporally recent, high-risk, authority-backed document is the correct context — a non-obvious outcome.

3. **Geometric mean temporal combination:** The use of geometric mean to combine exponential decay and half-life scores produces a stable composite that neither double-counts temporal factors nor loses the shape differentiation between the two models.

---

## 5. Industrial Applicability

The invention is applicable to any enterprise deploying AI assistants, specifically in domains where:
- Information has heterogeneous temporal validity (consulting, finance, engineering, legal)
- Organisational authority structures determine information trust (healthcare, regulated industries)
- Risk classification affects information priority (cybersecurity, operations, compliance)
- User roles require fundamentally different context presentation (enterprise SaaS, B2B AI)
