# Patent Claims: Dynamic Context Assembly Engine (DCAE)

**Reference:** DCAE-PAT-001  
**Jurisdiction:** European Patent Office (EPO)  
**Format:** European Patent Convention, Rule 43

---

## Independent Claim

**Claim 1**

A computer-implemented method for assembling context for large language model prompt construction in an enterprise knowledge management system, comprising:

(a) receiving a natural language query from a user;

(b) retrieving, from a vector database, a plurality of candidate context objects by computing semantic similarity between a dense vector embedding of the natural language query and pre-computed dense vector embeddings of said context objects;

(c) for each of said candidate context objects, computing a multi-dimensional composite relevance score comprising:

  (i) a temporal relevance score derived by applying a source-type-specific exponential decay function to the age of the context object, wherein different source types are assigned different decay rate constants reflecting the characteristic information lifespan of each source type;

  (ii) a context half-life score derived by computing the remaining relevance fraction of the context object based on a source-type-specific half-life period, wherein the half-life period represents the time for the relevance of the context object to reduce to fifty percent of its initial value;

  (iii) an organisational authority score derived from a role hierarchy associated with the creator of the context object, wherein roles at higher levels of organisational authority produce higher authority scores;

  (iv) a risk priority score derived from a risk classification label associated with the context object, wherein higher-risk classifications produce higher priority scores;

  (v) a project relevance score derived by measuring the degree of correspondence between a project identity detected from the natural language query and the project identity associated with the context object;

(d) computing a weighted composite relevance score for each candidate context object as a linear combination of the scores computed in step (c), wherein the weights of said linear combination are configurable;

(e) applying a behavioural multiplier to the composite relevance score of each candidate context object based on a user profile associated with the querying user, said user profile comprising at least a role designation, a verbosity preference, and a risk tolerance level;

(f) ranking the candidate context objects in descending order of the multiplier-adjusted composite relevance score;

(g) selecting a top-ranked subset of the candidate context objects; and

(h) assembling a prompt for a large language model comprising the natural language query and the selected context objects, wherein the system prompt of said assembled prompt is adapted based on the user profile.

---

## Dependent Claims

**Claim 2 — Temporal Decay Specificity**

The method of claim 1, wherein the source-type-specific exponential decay function in step (c)(i) assigns a decay rate constant (λ) according to a mapping wherein:
- standup notes and real-time operational artefacts are assigned λ ≥ 0.20;
- meeting notes and email communications are assigned 0.05 ≤ λ < 0.20;
- sprint reports and project management artefacts are assigned 0.01 ≤ λ < 0.05;
- architecture decision records and formal design documents are assigned λ ≤ 0.005;
- security policies and compliance documents are assigned λ ≤ 0.002.

**Claim 3 — Half-Life Mapping**

The method of claim 1, wherein the source-type-specific half-life period in step (c)(ii) assigns a half-life according to a mapping wherein:
- meeting notes are assigned a half-life of less than 30 days;
- sprint reports and project management artefacts are assigned a half-life between 14 and 60 days;
- incident reports and operational event records are assigned a half-life between 60 and 180 days;
- architecture decision records are assigned a half-life exceeding 1000 days;
- security policies are assigned a half-life exceeding 1800 days.

**Claim 4 — Combined Temporal Scoring**

The method of claims 2 and 3, wherein the temporal relevance score used in computing the composite relevance score is derived by combining the exponential decay score and the half-life score using a geometric mean, thereby producing a composite temporal score that reflects both the instantaneous freshness and the long-term decay characteristic of the source type.

**Claim 5 — Knowledge Graph Expansion**

The method of claim 1, further comprising:

(a) identifying the top-ranked context objects from the semantic retrieval stage;

(b) traversing a knowledge graph to identify context objects that are within a configurable graph distance of said top-ranked context objects, connected by semantic, ownership, dependency, or reference relationships;

(c) including said graph-adjacent context objects as additional candidates in the multi-dimensional scoring stage;

whereby the assembled context includes knowledge objects that are relationally relevant but may not be directly semantically similar to the query.

**Claim 6 — Project Detection**

The method of claim 1, wherein the project identity detection in step (c)(v) comprises:
- exact string matching against a registry of known project identities;
- substring matching for partial project name references;
- fuzzy string matching using sequence similarity metrics for variant spellings or abbreviations;
wherein the most specific matching strategy producing a result above a configurable confidence threshold is applied.

**Claim 7 — Behavioural Source Preferences**

The method of claim 1, wherein the user profile comprises a list of preferred source types, and the behavioural multiplier in step (e) applies an elevated multiplier to context objects whose source type appears in said list of preferred source types, and a reduced multiplier to context objects whose source type does not correspond to the roles default source preferences.

**Claim 8 — Prompt Adaptation by Role**

The method of claim 1, wherein the adaptation of the system prompt in step (h) comprises selecting, based on the role designation in the user profile, from a plurality of pre-defined instruction templates that differ in:
- technical terminology density;
- level of implementation detail;
- emphasis on business impact versus technical detail;
- risk identification and mitigation framing.

**Claim 9 — Explainable Score Decomposition**

The method of claim 1, further comprising generating, for each selected context object, a human-readable explanation comprising the individual dimensional score, the formula parameters used to derive each score, and the weighted contribution of each dimension to the final composite relevance score.

**Claim 10 — Comparative RAG Output**

The method of claim 1, further comprising, in parallel with the multi-dimensional scoring pipeline, executing a semantic-only retrieval ranking over the same candidate set, and returning both ranked lists to the user to enable direct comparison between traditional retrieval-augmented generation and the multi-dimensional dynamic context assembly method.

**Claim 11 — Configurable Scoring Weights**

The method of claim 1, wherein the weights of the linear combination in step (d) are dynamically configurable per query, enabling a querying user or system administrator to emphasise specific relevance dimensions by adjusting the weighting coefficients at query time without retraining or reindexing.

**Claim 12 — Authority Score Normalisation**

The method of claim 1, wherein the organisational authority score in step (c)(iii) is computed as the ratio of the role weight of the context object creator to the maximum possible role weight, producing a normalised score in the range [0, 1], wherein the role weight is defined by a configurable organisational hierarchy that assigns monotonically increasing weights to progressively senior roles.

**Claim 13 — Vector Database Integration**

The method of claim 1, wherein the vector database stores the dense vector embeddings of context objects as columns in a relational database management system extended with vector similarity operations, enabling joint filtering by relational predicates and vector distance in a single query execution.

**Claim 14 — System Architecture**

A system for dynamic context assembly for large language model prompt construction, comprising:

(a) a context ingestion subsystem configured to receive documents and artefacts from a plurality of enterprise data sources, classify each ingested item by source type, extract or assign metadata comprising owner identity, project association, and risk classification, and generate and store a dense vector embedding for each ingested item;

(b) a knowledge graph subsystem configured to represent context objects, persons, and projects as nodes and to represent semantic, ownership, dependency, and project association relationships as directed, weighted edges between said nodes;

(c) a multi-dimensional scoring engine implementing the method of claim 1;

(d) a prompt assembly subsystem configured to format the selected context objects and the natural language query into a structured prompt for a large language model, and to adapt the system instruction portion of said prompt based on the user profile; and

(e) an application programming interface configured to accept natural language queries with optional user profile identifiers and to return the assembled prompt together with the scored context set and the score breakdown for each selected context object.

**Claim 15 — Computer-Readable Medium**

A non-transitory computer-readable storage medium storing instructions that, when executed by one or more processors, cause the processors to perform the method of claim 1.

---

*These claims are presented in draft form for review by patent counsel. The independent claim and dependent claims are intended to provide a layered protection strategy covering the core method (Claim 1), specific implementation details (Claims 2–13), the overall system (Claim 14), and the software product (Claim 15).*
