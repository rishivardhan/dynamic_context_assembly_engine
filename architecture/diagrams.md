# DCAE Architecture Diagrams

All diagrams use Mermaid notation and are rendered by GitHub, GitLab, and most modern documentation platforms.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    User([User / API Client]) --> QC[Query Console]
    QC --> QE[Query Engine\nFastAPI]

    QE --> IC[Intent & Project\nClassifier]
    IC --> SS[Semantic Search\nSentenceTransformers + pgvector]
    IC --> GE[Graph Expansion\nNeo4j Traversal]

    SS --> RE[Relevance Engine\nComposite Scorer]
    GE --> RE

    RE --> TE[Temporal Engine\nexp decay + half-life]
    RE --> AS[Authority Scorer\nRole Hierarchy]
    RE --> RS[Risk Scorer\nRisk Classification]
    RE --> PS[Project Scorer\nFuzzy Matching]
    RE --> BO[Behavioural Overlay\nUser Profile]

    TE --> PA[Prompt Assembler]
    AS --> PA
    RS --> PA
    PS --> PA
    BO --> PA

    PA --> LG[LLM Gateway\nOpenAI / Ollama / Any API]
    LG --> Resp([Response + Explanation])

    style QE fill:#1d4ed8,color:#fff
    style RE fill:#7c3aed,color:#fff
    style PA fill:#059669,color:#fff
```

---

## 2. Data Ingestion Architecture

```mermaid
flowchart LR
    J[Jira] --> ING
    C[Confluence] --> ING
    G[Git] --> ING
    E[Email] --> ING
    M[Meetings] --> ING
    INC[Incidents] --> ING

    ING[Ingestion\nPipeline] --> CS[Context Store\nPostgreSQL + pgvector]
    ING --> KG[Knowledge Graph\nNeo4j]

    CS --> SE[Semantic Engine\nEmbedding Generation]
    SE --> CS

    KG --> RE[Relevance Engine]
    CS --> RE
```

---

## 3. Composite Scoring Pipeline

```mermaid
flowchart TD
    Q[Query] --> EMB[Embed Query\nall-MiniLM-L6-v2]
    EMB --> VS[Vector Search\npgvector cosine]
    VS --> CAND[Candidate Pool\ntop-20 semantic hits]

    CAND --> GX[Graph Expansion\nNeo4j +2 hops]
    GX --> FULL[Full Candidate Set]

    FULL --> TEMP[Temporal Score\nexp−λ×age × √half-life]
    FULL --> AUTH[Authority Score\nRole Weight / Max]
    FULL --> RISK[Risk Score\nRisk Level / Max]
    FULL --> PROJ[Project Score\nFuzzy Match]
    FULL --> SEM[Semantic Score\nCosine Similarity]

    TEMP --> CS[Composite Score\nWeighted Sum]
    AUTH --> CS
    RISK --> CS
    PROJ --> CS
    SEM --> CS

    CS --> BP[Behavioural Profile\nMultiplier]
    BP --> RANK[Ranked Context\ntop-k selection]
    RANK --> ASM[Prompt Assembly\n+ Explanation]
```

---

## 4. Knowledge Graph Schema

```mermaid
graph LR
    C1[ContextObject\nid, title, source_type\nproject, owner, risk_level]
    P1[Person\nid, name, role\nemail, department]
    PR1[Project\nid, name, status]

    P1 -- OWNS --> C1
    C1 -- BELONGS_TO --> PR1
    C1 -- DEPENDS_ON --> C1
    C1 -- RELATED_TO --> C1
    C1 -- SUPERSEDES --> C1
    C1 -- BLOCKS --> C1
    C1 -- REFERENCES --> C1
    C1 -- IMPLEMENTED_BY --> C1
    C1 -- CREATED_BY --> P1
```

---

## 5. Temporal Decay Comparison

```mermaid
xychart-beta
    title "Temporal Score Decay by Source Type"
    x-axis "Age (days)" [0, 7, 14, 30, 60, 90, 180, 365]
    y-axis "Relevance Score" 0 --> 1
    line [1.0, 0.35, 0.12, 0.01, 0.00, 0.00, 0.00, 0.00]
    line [1.0, 0.90, 0.81, 0.61, 0.37, 0.22, 0.05, 0.00]
    line [1.0, 0.97, 0.93, 0.86, 0.74, 0.64, 0.41, 0.17]
    line [1.0, 1.00, 0.99, 0.99, 0.98, 0.96, 0.93, 0.85]
```

*Lines: Standup (fastest decay) → Sprint Report → Incident → ADR (slowest decay)*

---

## 6. Scoring Weight Distribution (Default)

```mermaid
pie title Default DCAE Scoring Weights
    "Semantic (30%)" : 30
    "Temporal (25%)" : 25
    "Risk (20%)" : 20
    "Authority (15%)" : 15
    "Project (10%)" : 10
```

---

## 7. DCAE vs RAG Information Flow

```mermaid
flowchart LR
    subgraph RAG["Traditional RAG"]
        direction TB
        Q1[Query] --> EMB1[Embed]
        EMB1 --> VS1[Vector Search]
        VS1 --> R1[Top-k by\nSemantic Score]
        R1 --> PR1[Prompt]
    end

    subgraph DCAE_Flow["DCAE"]
        direction TB
        Q2[Query] --> EMB2[Embed]
        EMB2 --> VS2[Vector Search]
        VS2 --> GE2[Graph Expand]
        GE2 --> SC2[Multi-Dim Score\nSemantic+Temporal\n+Authority+Risk\n+Project]
        SC2 --> BO2[Behavioural\nAdapt]
        BO2 --> PR2[Prompt\n+ Explanation]
    end

    RAG -. "Better context\nquality" .-> DCAE_Flow
```

---

## 8. Deployment Architecture

```mermaid
C4Context
    title DCAE Docker Compose Deployment

    Person(user, "User", "Enterprise employee")

    System_Boundary(dcae, "DCAE Stack") {
        Container(fe, "Frontend", "React + Vite", "Dashboard, Graph View, Comparison")
        Container(be, "Backend", "Python FastAPI", "DCAE Engine, REST API")
        ContainerDb(pg, "PostgreSQL 16", "pgvector", "Context objects + embeddings")
        ContainerDb(neo, "Neo4j 5", "Graph DB", "Knowledge graph")
    }

    Rel(user, fe, "Uses", "HTTP :3000")
    Rel(fe, be, "API calls", "HTTP :8000")
    Rel(be, pg, "Read/write contexts", "SQL + vector")
    Rel(be, neo, "Graph queries", "Bolt :7687")
```
