# Data Infrastructure

**Purpose:** Centralized data layer for threat modeling engine, vector embeddings, and RAG (Retrieval-Augmented Generation) system.

**Status:** Active data workspace with seeded corpora, manifests, and retrieval-support assets.

Sprint-2026-12 planning references in this file are historical context. Current implementation includes
retrieval MVP components under `src/threat_modeler/retrieval.py` and `src/threat_modeler/retrieval_adapters/`.

---

## Directory Structure

```
data/
├── vector_db/       Vector embeddings, indexes, and models
├── inputs/          Ingestion sources (documents, threat data, test fixtures)
├── models/          ML model configurations and artifacts
├── outputs/         Generated data (threat models, reports, embeddings)
└── README.md        This file
```

## Overview

| Directory | Purpose | Contents | .gitignore |
|-----------|---------|----------|-----------|
| `vector_db/` | Persistent embedding indexes | FAISS/Chroma indexes, config | ✅ Indexes |
| `inputs/` | Ingestion sources | Architecture docs, threats, fixtures | ✅ Fetched data |
| `models/` | ML model references | Embedding models, configs | ❌ Keep configs |
| `outputs/` | Generated artifacts | Threat models, embeddings | ✅ All outputs |

---

## Subdirectory Details

### `vector_db/`

Vector embedding storage and management.

- `indexes/`: Persistent FAISS or Chroma vector indexes (not tracked in git)
- `config.yaml`: Embedding model configuration, dimensions, chunk size
- `.gitignore`: Excludes large binary indexes

**Example config.yaml:**
```yaml
embedding_model: "all-MiniLM-L6-v2"
dimension: 384
chunk_size: 512
overlap: 50
index_type: "faiss"  # or "chroma"
```

---

### `inputs/`

Data sources for ingestion and processing.

- **`Aerospace_Architecture/`**: Aerospace system documentation for vector ingestion
  - Operational architecture diagrams
  - API specifications
  - Design documents

- **`threat_libraries/`**: Reference threat catalogs
  - STRIDE threat templates
  - OWASP Top 10 mappings
  - Common vulnerability patterns

- **`fixtures/`**: Test and validation data
  - Sample threat models
  - Reference documents for RAG validation
  - Test cases for embedding pipeline

- **`.gitignore`**: Tracks `fetched/` subdirectory (downloaded remote content)

---

### `models/`

Machine learning model configurations and metadata.

- `embeddings.yaml`: Catalog of available embedding models with performance metrics
- Model-specific configs (fine-tuned weights metadata, normalization parameters)

**Example embeddings.yaml:**
```yaml
models:
  - name: "all-MiniLM-L6-v2"
    dimension: 384
    speed: "fast"
    accuracy: "good"
    provider: "huggingface"

  - name: "all-mpnet-base-v2"
    dimension: 768
    speed: "medium"
    accuracy: "excellent"
    provider: "huggingface"
```

---

### `outputs/`

Generated data and artifacts (not tracked in git).

- Serialized threat models (STIX, JSON)
- Embedding outputs
- Retrieved context from vector DB
- Performance metrics

**Note:** All contents ignored via `.gitignore` to avoid bloating repository.

---

## Integration with Retrieval and RAG Pipeline

### Current Baseline Flow

1. **Ingest** → Load/normalize source material from `inputs/`
1. **Store** → Maintain retrieval-ready corpora and optional vector index artifacts in `vector_db/`
1. **Retrieve** → Query corpus/indexes and attach citation metadata
1. **Generate** → Feed retrieved context into pipeline outputs under governed runtime paths

### Code Integration Notes

```python
from threat_modeler.retrieval import CorpusIngestor, Retriever

ingestor = CorpusIngestor()
retriever = Retriever()

ingestor.ingest([
  {"id": "doc-1", "text": "Sample architecture context"},
])
retriever.corpus = ingestor.corpus
results = retriever.retrieve("architecture", top_k=3)
```

---

## Forward Roadmap

### Prioritized Follow-On Items

- [ ] Vector database initialization and persistence hardening
- [ ] Embedding pipeline with batch processing
- [ ] Retrieval context ranking and scoring
- [ ] Deeper retrieval integration with LangGraph stage prompts

### Roadmap (2026-13+)

- [ ] Fine-tuning pipeline for domain-specific embeddings
- [ ] Multi-modal embeddings (text + diagrams)
- [ ] Cache management and index optimization
- [ ] Monitoring and evaluation metrics

---

## Environment Setup

### Adding data/ to PYTHONPATH (if needed)

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/repo/data"
```

### Initialization Example

```bash
python scripts/generators/init_vector_db.py --config data/models/embeddings.yaml
```

---

## References

- **RAG Planning (historical baseline)**: `planning/Sprint_2026_12_Planning.md`
- **Test Infrastructure**: `Tests/` (uses data/inputs/fixtures for validation)
- **Architecture**: `docs/architecture/` (design decisions documented there)
