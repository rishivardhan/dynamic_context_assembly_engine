# Dynamic Context Assembly Engine (DCAE)

**A novel enterprise AI architecture for multi-dimensional, explainable context retrieval — surpassing traditional RAG.**

---

## What is DCAE?

Traditional Retrieval-Augmented Generation (RAG) ranks context purely by semantic vector similarity. DCAE replaces this with a **seven-dimensional composite scoring architecture** that models how enterprise knowledge should actually be weighted:

```
FinalScore = (
  SemanticScore  × 0.30  +
  TemporalScore  × 0.25  +
  RiskScore      × 0.20  +
  AuthorityScore × 0.15  +
  ProjectScore   × 0.10
) × BehaviouralMultiplier
```

Every score is explainable — the system shows *why* each context item was selected.

---

## Architecture Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│  Query Engine (FastAPI)                 │
│  ├─ Intent & Project Classifier         │
│  ├─ Semantic Search (pgvector)          │
│  └─ Graph Expansion (Neo4j)             │
└──────────────┬──────────────────────────┘
               │  Candidate Pool
               ▼
┌─────────────────────────────────────────┐
│  Multi-Dimensional Relevance Engine     │
│  ├─ Temporal Decay  exp(-λ × age_days)  │
│  ├─ Half-Life      0.5^(age/halflife)   │
│  ├─ Authority      Role Weight / Max    │
│  ├─ Risk           Risk Level / Max     │
│  └─ Project        Fuzzy Match Score    │
└──────────────┬──────────────────────────┘
               │  Scored + Ranked Context
               ▼
┌─────────────────────────────────────────┐
│  Behavioural Overlay + Prompt Assembly  │
│  └─ User Profile Adaptation             │
└─────────────────────────────────────────┘
               │
               ▼
      LLM Gateway + Explainable Response
```

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose

### Launch

```bash
git clone <repo>
cd dcae
docker compose up
```

Services start in order (PostgreSQL → Neo4j → Backend → Frontend). The backend automatically initialises the schema and seeds sample enterprise data on first launch.

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

Neo4j credentials: `neo4j` / `dcae_neo4j_secret`

---

## Features

### Query Engine
- Natural language enterprise queries
- Multi-dimensional context scoring with live weight adjustment
- User profile selection for behavioural adaptation
- Example queries for quick demonstration

### Context Explorer
- Ranked context display with score breakdowns
- Per-item radar charts showing all 5 scoring dimensions
- Expandable content view
- Source type, risk level, and age indicators

### Knowledge Graph
- Interactive React Flow graph of 40+ context objects
- Node types: ContextObject, Person, Project
- Edge types: owns, depends_on, related_to, implemented_by, supersedes, blocks, references
- Click-through to node neighbourhood view

### Prompt Viewer
- Assembled system + user prompts
- One-click copy to clipboard
- Context window token estimate

### RAG Comparison
- Side-by-side: Traditional RAG (semantic only) vs DCAE (multi-dimensional)
- Score comparison bar chart
- Demonstrates how DCAE surfaces critical but semantically distant context

---

## Sample Enterprise Data

The PoC includes a realistic 9-month enterprise transformation programme:

| Type | Count | Examples |
|------|-------|---------|
| Jira Stories | 10 | Schema migration, PgBouncer config, cutover runbook |
| Incidents | 7 | DB outage, API memory leak, security breach attempt |
| Architecture Decisions | 5 | ADR-007 (PostgreSQL), ADR-012 (Kong), ADR-015 (Zero Trust) |
| Architecture Documents | 2 | PG migration design, Zero Trust reference architecture |
| Sprint Reports | 5 | Platform, Backend, Security, Data engineering sprints |
| Meeting Notes | 5 | Steering committee, architecture review, go/no-go calls |
| Emails | 2 | Licence escalation, security policy update |
| Git Commits | 2 | PgBouncer fix, Kong JWT plugin |
| Security Policies | 1 | Database access control policy |

Projects covered:
1. **Postgres Migration** — Oracle 19c → PostgreSQL 16
2. **API Gateway Modernisation** — MuleSoft → Kong
3. **Zero Trust Security Framework** — NIST SP 800-207 implementation
4. **Data Platform Modernisation** — Hadoop → Databricks
5. **Customer Portal Redesign** — Angular monolith → React micro-frontends

---

## API Reference

```
POST /api/v1/query          — Main DCAE query endpoint
POST /api/v1/score          — Score a single context item
GET  /api/v1/graph          — Full knowledge graph
GET  /api/v1/graph/node/{id} — Node neighbourhood
GET  /api/v1/projects       — List projects
GET  /api/v1/context        — List context objects
GET  /api/v1/context/{id}   — Context detail
GET  /api/v1/profiles       — List user profiles
GET  /api/v1/health         — Health check
```

Full OpenAPI documentation: http://localhost:8000/docs

### Example Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current status of the Postgres migration?",
    "user_profile_id": "profile-001",
    "top_k": 5,
    "include_rag_comparison": true
  }'
```

---

## Scoring Engine

See [docs/scoring_engine.md](docs/scoring_engine.md) for full scoring reference.

| Engine | Formula | Key Parameters |
|--------|---------|---------------|
| Temporal | `BaseWeight × exp(-λ × age)` | λ per source type (0.001–0.30) |
| Half-Life | `weight × 0.5^(age/halflife)` | half-life per source type (7–1825 days) |
| Authority | `RoleWeight / MaxWeight` | Engineer=1.0, Lead=1.5, Architect=2.0, Director=3.0 |
| Risk | `RiskWeight / MaxWeight` | LOW=1, MEDIUM=3, HIGH=5, CRITICAL=10 |
| Project | Fuzzy string match | Exact=1.0, Partial=0.85, Fuzzy=0.5–0.85, None=0.5 |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
cd ..
pytest tests/ -v
```

Tests do not require live database connections — scoring engine tests are fully unit-testable.

---

## Project Structure

```
dcae/
├── backend/
│   ├── app/
│   │   ├── main.py              — FastAPI app entry point
│   │   ├── config.py            — Settings (weights, decay, half-life)
│   │   ├── models/
│   │   │   ├── domain.py        — Core domain models
│   │   │   └── api.py           — Request/response models
│   │   ├── engines/
│   │   │   ├── temporal.py      — Exponential decay scoring
│   │   │   ├── halflife.py      — Half-life decay scoring
│   │   │   ├── authority.py     — Organisational authority scoring
│   │   │   ├── risk.py          — Risk level scoring
│   │   │   ├── project_relevance.py — Project matching
│   │   │   ├── semantic.py      — pgvector semantic search
│   │   │   ├── behavioral.py    — User profile adaptation
│   │   │   └── composite.py     — Composite score orchestration
│   │   ├── services/
│   │   │   └── context_assembler.py — Main DCAE pipeline
│   │   ├── api/
│   │   │   └── routes.py        — FastAPI routes
│   │   └── db/
│   │       ├── postgres.py      — PostgreSQL ORM models
│   │       ├── neo4j_client.py  — Neo4j repository
│   │       ├── init_db.py       — Schema initialisation
│   │       └── seed.py          — Sample data seeding
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── QueryPage.tsx    — Main query interface
│       │   ├── GraphPage.tsx    — Knowledge graph explorer
│       │   └── ComparisonPage.tsx — RAG vs DCAE comparison
│       └── components/
│           ├── ContextCard.tsx  — Scored context display
│           ├── KnowledgeGraph.tsx — React Flow graph
│           ├── PromptViewer.tsx — Assembled prompt viewer
│           ├── ScoreBar.tsx     — Score visualisation
│           └── SourceBadge.tsx  — Source type badges
├── sample-data/
│   └── enterprise_data.json    — 40 context objects, 5 projects
├── tests/                       — Unit + integration tests
├── architecture/
│   └── diagrams.md             — Mermaid architecture diagrams
├── patent/
│   ├── novelty.md              — Prior art analysis & inventive step
│   ├── claims.md               — 1 independent + 15 dependent claims
│   └── traceability_matrix.md — Feature-to-claim mapping
├── docs/
│   └── scoring_engine.md       — Scoring engine reference
└── docker-compose.yml
```

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python / FastAPI | 3.12 / 0.115 |
| ORM | SQLAlchemy | 2.0 |
| Relational DB | PostgreSQL + pgvector | 16 |
| Graph DB | Neo4j | 5.15 |
| Embeddings | SentenceTransformers | 3.3 |
| Embedding Model | all-MiniLM-L6-v2 | 384 dimensions |
| Frontend | React + TypeScript | 18 / 5.7 |
| Build | Vite | 6.0 |
| Graph Viz | React Flow | 11 |
| Charts | Recharts | 2.13 |
| State | Zustand + React Query | 5.0 / 5.62 |
| Deployment | Docker Compose | 3.9 |

---

## Patent Status

This PoC supports a European patent filing for the DCAE architecture. See:

- [patent/novelty.md](patent/novelty.md) — Novelty analysis vs prior art
- [patent/claims.md](patent/claims.md) — 16 patent claims (EPO format)
- [patent/traceability_matrix.md](patent/traceability_matrix.md) — Feature-to-claim traceability

---

## Configuration

All scoring parameters are configurable via environment variables:

```env
# Scoring weights
WEIGHT_SEMANTIC=0.30
WEIGHT_TEMPORAL=0.25
WEIGHT_AUTHORITY=0.15
WEIGHT_RISK=0.20
WEIGHT_PROJECT=0.10

# Retrieval
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K_SEMANTIC=20
TOP_K_FINAL=10
MAX_PROMPT_TOKENS=4096
```

Weights can also be overridden per-query via the `weights` field in `POST /api/v1/query`.

---

## Licence

Proprietary — All rights reserved. This codebase is provided for evaluation and patent support purposes.
