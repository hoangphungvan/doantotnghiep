# Candidate–Job Matching — Codex Instructions

## 1. Project Context

This repository is a graduation project implementing a Candidate–Job Matching (CJM) system for Vietnamese IT recruitment.

The system ranks Job Descriptions (JDs) for a Candidate CV using:

* LLM-based entity extraction
* Multilingual Sentence-BERT
* DeepSets pooling
* Candidate–Job graph representation
* Graph Convolutional Network (GCN)
* Semantic similarity
* Hybrid ranking

The primary task is RANKING, not binary classification.

Given a CV `c_i` and candidate jobs:

J = {j_1, j_2, ..., j_n}

the system produces:

score(c_i, j_k)

and ranks the jobs by descending relevance.

Do not redesign the project into a generic classifier.

---

# 2. Existing Architecture Is the Source of Truth

Before modifying code:

1. Inspect the relevant existing files.
2. Trace the current data flow.
3. Check `config.py`.
4. Check tensor dimensions.
5. Check cached artifact compatibility.
6. Check whether the change affects training/evaluation results.

Do NOT assume architecture from general ML conventions when repository code provides the answer.

Prefer modifying the existing implementation instead of replacing it.

---

# 3. Core Pipeline

The current pipeline is:

Raw CV / JD
→ Entity Extraction
→ Entity Cache
→ Sentence-BERT Embedding
→ DeepSets Pooling
→ 14-node Graph Construction
→ GCN
→ GCN Score
→ Semantic Similarity
→ Hybrid Score
→ Per-CV JD Ranking
→ Ranking Evaluation

Preserve this pipeline unless explicitly instructed otherwise.

---

# 4. Entity Schema

Exactly six semantic entity groups are currently used:

```python
ENTITY_TYPES = [
    "role",
    "hard_skills",
    "field_of_education",
    "industry_sector",
    "education",
    "soft_skills",
]
```

Do NOT:

* rename these fields casually
* add new entity types silently
* remove entity types
* change their ordering if downstream code depends on it

Missing entities must be handled gracefully.

---

# 5. Entity Extraction

Entity extraction is implemented in:

`src/extraction/entity_extractor.py`

Current LLM provider:

Groq API

Current model:

`qwen/qwen3.8-27b`

Configuration is provided through `.env` / `config.py`.

The extractor uses a two-layer entity cache based on:

* SHA-256 content identity
* file / JD identity

When changing extraction logic:

* preserve structured JSON output
* validate returned fields
* handle malformed JSON
* handle timeout / rate limits
* do not expose API keys
* do not silently turn failed extraction into valid training data
* preserve cache compatibility where possible

Never hard-code API keys.

---

# 6. Embedding Model

Embedding generation is implemented in:

`src/representation/embedding_generator.py`

Current Sentence-BERT model:

`paraphrase-multilingual-MiniLM-L12-v2`

Base embedding dimension:

`384`

The model supports multilingual text including Vietnamese.

Do not replace the embedding model unless explicitly requested.

Avoid repeatedly loading SentenceTransformer.

Reuse model instances and cached embeddings whenever possible.

---

# 7. DeepSets Representation

Entity collections are aggregated using:

* Mean pooling
* Max pooling
* Sum pooling

Therefore:

`384 × 3 = 1152`

Expected entity/node representation dimension:

`1152`

Conceptually:

```text
Entity strings
      ↓
SBERT
      ↓
[N, 384]
      ↓
Mean ─┐
Max  ─┼─ concatenate → [1152]
Sum  ─┘
```

Before changing pooling code, verify every downstream consumer expecting 1152-dimensional features.

Never casually change this dimension.

---

# 8. Graph Structure

Graph construction is implemented in:

`src/representation/graph_builder.py`

Each Candidate–JD pair is represented by exactly 14 nodes.

Candidate side:

```text
Candidate center
├── role
├── hard_skills
├── field_of_education
├── industry_sector
├── education
└── soft_skills
```

Job side:

```text
JD center
├── role
├── hard_skills
├── field_of_education
├── industry_sector
├── education
└── soft_skills
```

Total:

```text
2 center nodes
+ 6 candidate entity nodes
+ 6 JD entity nodes
= 14 nodes
```

Do not change node ordering without checking saved graph files and model assumptions.

---

# 9. Graph Edges

Two important edge groups exist.

## Star edges

Each center node connects to its own entity nodes.

## Cross edges

Candidate and JD entity representations are connected based on semantic similarity.

Current graph construction uses cosine similarity with k-NN style sharpening.

Current configuration:

```text
k = 10
p = 4.0
```

The project also applies entity importance where conceptually:

```text
role
>
hard_skills
>
field_of_education
>
other entity types
```

Do not convert weighted edges into unweighted edges unless explicitly requested.

Do not remove semantic cross edges without understanding the effect on the GCN.

---

# 10. PyTorch Geometric Data

Graphs must remain compatible with PyTorch Geometric.

Expected objects may include:

```python
Data(
    x=...,
    edge_index=...,
    edge_attr=...,
    y=...
)
```

When modifying graph/model code always inspect:

```python
data.x.shape
data.edge_index.shape
data.edge_attr.shape if applicable
data.y
```

Expected node count per graph:

```text
14
```

Expected base node feature dimension:

```text
1152
```

Do not silently reshape tensors merely to make runtime errors disappear.

Find the actual shape mismatch.

---

# 11. GCN Model

GCN implementation:

`src/modeling/model.py`

Current architecture conceptually follows:

```text
Node Features
     ↓
Pre-Aggregation
     ↓
GCNConv
     ↓
GCNConv
     ↓
GCNConv
     ↓
Global Readout
     ↓
MLP Classifier
     ↓
Matching Logit
```

Current configuration:

```text
GCN layers = 3
hidden dimension = 128
```

Do not replace GCN with:

* GAT
* GraphSAGE
* GIN
* Transformer
* other GNN architectures

unless explicitly requested.

Architectural experiments should be implemented separately rather than silently replacing the baseline/proposed model.

---

# 12. Training Objective

Training is implemented in:

`src/modeling/train.py`

Current loss:

```python
BCEWithLogitsLoss
```

The original relevance grade is:

```text
0
1
2
3
```

Training target:

```python
target = grade / 3
```

Mapping:

```text
grade 0 → 0.00
grade 1 → 0.33
grade 2 → 0.67
grade 3 → 1.00
```

Do not confuse:

* relevance grade
* normalized target
* predicted logit
* sigmoid probability
* ranking score

Do not change the loss function without explicitly explaining the experimental consequences.

---

# 13. Relevance Labels

The project uses graded relevance:

```text
3 = highly relevant
2 = partially relevant
1 = related / hard negative
0 = irrelevant / easy negative
```

Examples:

```text
Java Backend CV
↔ Java Spring Backend JD
= likely grade 3

Java Backend CV
↔ related backend / different stack JD
= potentially grade 2

Java Backend CV
↔ Mobile iOS JD
= hard negative / grade 1

Java Backend CV
↔ unrelated domain
= easy negative / grade 0
```

Do not automatically generate or modify labels without respecting this meaning.

---

# 14. Query-Aware Splitting

Dataset splitting is implemented around:

`src/modeling/dataset.py`

Training/validation splitting must be query-aware.

The same CV/query should not leak across incompatible train/validation/test groups.

This is important because multiple rows can represent:

```text
CV_A → JD_1
CV_A → JD_2
CV_A → JD_3
...
```

Random row-level splitting can cause leakage.

Never replace query-aware splitting with naive random pair splitting unless explicitly requested for an experiment.

---

# 15. Hybrid Ranking

Hybrid evaluation is implemented in:

`src/evaluation/hybrid.py`

Final score:

```text
HybridScore =
    alpha * GCNScore
    + (1 - alpha) * SemanticScore
```

Alpha may be:

* explicitly provided
* tuned using validation data

Do not assume alpha is always 0.5 or 0.7.

Do not tune alpha using the final test set.

The final ranking is performed independently for each CV/query.

---

# 16. Ranking Evaluation

Primary ranking metrics:

* NDCG@K
* Recall@K
* MRR

Current K values include:

```text
1, 3, 5, 10
```

Additional diagnostic metrics may include:

* MAE
* AUC-ROC

However, this project's main task is ranking.

Do not use classification accuracy as the primary model-quality conclusion.

Correct evaluation flow:

```text
CV/query
   ↓
all candidate JDs
   ↓
predict score for each JD
   ↓
sort descending
   ↓
compare against graded relevance
   ↓
NDCG / Recall / MRR
```

Never create one global ranking across unrelated CVs.

---

# 17. Baselines

Baseline implementations are located in:

`src/evaluation/baselines.py`

Important baselines:

* TF-IDF + cosine similarity
* Sentence-BERT + cosine similarity
* GCN
* Hybrid GCN + semantic

Preserve baseline implementations so experiment results remain comparable.

Do not modify a baseline while simultaneously claiming improvement of the proposed method against the old baseline.

---

# 18. Current Dataset Pipeline

The current dataset pipeline is:

```text
VietJobs.csv
    ↓
extract_vietjobs_it.py
    ↓
~1,906 IT JDs
    ↓
cache_jd_embeddings.py
    ↓
Entity + DeepSets cache
    ↓
cluster_jds.py
    ↓
KMeans K=20
    ↓
generate_training_data.py
    ↓
12 technical CV profiles
    ↓
60 balanced CV–JD pairs
    ↓
prepare_training_data.py
    ↓
60 PyTorch Geometric graphs
```

Treat these numbers as current experiment configuration, not universal constants.

Do not silently change them.

---

# 19. Negative Sampling

Training data intentionally includes:

* positive matches
* partial matches
* hard negatives
* easy negatives

KMeans currently uses approximately:

```text
K = 20
```

Cluster similarity is used to support negative sampling.

Do not replace the negative sampling strategy with random negatives without explicitly discussing the effect on training quality.

---

# 20. Repository Responsibilities

## `src/data_collection/`

Only data acquisition/preparation logic.

Examples:

* VietJobs filtering
* clustering
* sampling
* training pair generation
* graph preprocessing

## `src/extraction/`

Entity extraction and normalization.

## `src/representation/`

Vector and graph representations.

Includes:

* SBERT
* DeepSets
* graph construction

## `src/modeling/`

Model and training logic.

Includes:

* dataset
* GCN
* training loop
* checkpoint handling

## `src/evaluation/`

Evaluation only.

Includes:

* metrics
* hybrid evaluation
* baselines

## `src/inference/`

Production/demo inference logic.

Do not mix responsibilities unnecessarily.

---

# 21. Configuration

Central configuration belongs in:

`config.py`

Secrets belong in:

`.env`

Prefer:

```text
.env
  ↓
config.py
  ↓
application modules
```

Avoid reading the same environment variable independently from many modules.

Hyperparameters should be centralized when practical.

Avoid unexplained magic numbers.

---

# 22. Cache Safety

The project contains expensive caches:

```text
data/cache/entity_cache.json
data/cache/jd_embeddings_cache.pt
data/processed/graphs/*.pt
```

Before changing:

* entity schema
* SBERT model
* embedding dimensions
* DeepSets pooling
* graph topology
* node ordering

consider whether existing caches become invalid.

Do not silently reuse incompatible caches.

If cache invalidation is required, explicitly state it.

---

# 23. Windows / UTF-8

Primary development environment includes Windows.

Use:

```bash
python -X utf8 ...
```

for project commands where Vietnamese output may be printed.

Preserve UTF-8 when reading/writing:

* CV text
* JD text
* CSV
* JSON
* logs

Avoid platform-specific path concatenation.

Prefer `pathlib.Path`.

---

# 24. Code Quality

Prefer:

* small focused functions
* descriptive names
* type hints
* `pathlib.Path`
* reusable helpers
* explicit configuration
* meaningful exceptions

Avoid:

* giant functions
* duplicated preprocessing
* hidden state
* unexplained constants
* broad exception swallowing
* unnecessary abstractions

Do not perform unrelated refactoring during a focused task.

---

# 25. Reproducibility

This is an academic project.

Reproducibility is mandatory.

When modifying experiments:

* preserve random seeds
* record hyperparameters
* preserve train/validation separation
* preserve baseline comparability
* do not overwrite useful experiment results without reason

Never fabricate:

* metrics
* datasets
* labels
* experimental results
* citations

A performance improvement must be measured before being claimed.

---

# 26. Data Leakage Rules

Always consider data leakage.

Pay particular attention to:

* CV appearing across splits
* JD appearing across splits
* clustering using inappropriate test information
* alpha tuning
* preprocessing fitted globally
* embedding/cache generation assumptions

If a requested implementation risks leakage, explain the risk before changing the experimental pipeline.

---

# 27. Codex Editing Rules

Before editing:

1. Read the target file.
2. Read directly related modules.
3. Read `config.py` when configuration is involved.
4. Trace callers and consumers.
5. Search for the affected symbol.
6. Inspect existing tests if available.

During editing:

1. Make the smallest coherent change.
2. Follow existing project style.
3. Avoid unrelated refactoring.
4. Avoid changing public interfaces unnecessarily.
5. Do not delete working behavior unless required.

After editing:

1. Run syntax/import checks.
2. Run relevant tests.
3. Run the smallest relevant project command.
4. Verify tensor dimensions for ML changes.
5. Verify no NaN/Inf for scoring/model changes.
6. Report what changed.

---

# 28. Verification Commands

Use targeted commands first.

Examples:

```bash
python -X utf8 main.py --mode demo
```

Training:

```bash
python -X utf8 src/modeling/train.py \
    --epochs 60 \
    --batch 16 \
    --lr 0.001 \
    --patience 15
```

Hybrid evaluation:

```bash
python -X utf8 src/evaluation/hybrid.py
```

Baselines:

```bash
python -X utf8 src/evaluation/baselines.py
```

Do not automatically run expensive full training when a smaller verification is sufficient.

---

# 29. Debugging ML Problems

For tensor/graph errors, debug in this order:

```text
raw input
↓
extracted entities
↓
SBERT shape
↓
DeepSets shape
↓
node feature matrix
↓
edge_index
↓
edge weights
↓
PyG batch
↓
GCN output
↓
loss
```

Report ML bugs using:

```text
Cause
→ Input Shape
→ Transformation
→ Output Shape
→ Failure
→ Fix
→ Verification
```

Do not patch shape errors using arbitrary `reshape`, `squeeze`, or `unsqueeze` without understanding the expected representation.

---

# 30. Security

Never:

* commit `.env`
* expose Groq API keys
* print secrets
* hard-code credentials

`.env` must remain ignored by Git.

Example values in documentation must always be placeholders.

---

# 31. Restrictions

Unless explicitly requested, DO NOT:

* change the six entity types
* change the 14-node graph structure
* replace SBERT
* change DeepSets output dimension
* replace GCN with another GNN
* change relevance grades
* change BCEWithLogitsLoss
* change query-aware splitting
* remove semantic hybrid scoring
* modify negative sampling methodology
* invalidate caches silently
* tune against test data
* regenerate the entire dataset
* run expensive training unnecessarily

---

# 32. Response Requirements

When completing a coding task, summarize:

```text
Files changed
What changed
Why
Verification performed
Potential impact
```

For ML architecture changes also include:

```text
Before shape
→ transformation
→ after shape
```

Explain implementation decisions in Vietnamese unless explicitly requested otherwise.

Keep code names, class names, functions, libraries, and standard ML terminology in English.

---

# 33. Guiding Principle

This repository is both:

1. a software system, and
2. a graduation research experiment.

A code change that makes the program run but invalidates the experiment is NOT considered a correct fix.

Prioritize:

Correctness
→ Data leakage prevention
→ Experimental validity
→ Reproducibility
→ Ranking quality
→ Maintainability
→ Performance
