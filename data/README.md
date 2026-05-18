# Data Infrastructure

**Purpose:** Centralized data layer for threat modeling engine, vector embeddings, and RAG (Retrieval-Augmented Generation) system.

**Status:** Infrastructure scaffold created for Sprint 2026-12 RAG implementation.

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

- **`architecture_docs/`**: System documentation for vector ingestion
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

## Integration with RAG Pipeline

### Expected Flow (Sprint 2026-12+)

1. **Ingest** → Load documents from `inputs/` → Generate embeddings
2. **Store** → Write vectors to `vector_db/indexes/` 
3. **Retrieve** → Query embeddings, retrieve context
4. **Generate** → Output threat models to `outputs/`

### Code Integration Points

```python
# Expected import pattern
from src.threat_modeler.rag import RAGEngine
from data.models import embeddings  # Model configs

engine = RAGEngine(
    vector_db_path="data/vector_db/indexes",
    model_config="data/models/embeddings.yaml",
    input_path="data/inputs",
    output_path="data/outputs"
)

# Run ingestion pipeline
engine.ingest(source="data/inputs/architecture_docs")

# Generate with retrieval
threat_model = engine.generate(prompt=query)
```

---

## Future Expansion

### Planned (2026-12)
- [ ] Vector database initialization and persistence layer
- [ ] Embedding pipeline with batch processing
- [ ] Retrieval context ranking and scoring
- [ ] RAG integration with LangGraph orchestrator

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

### Initialization (Placeholder for 2026-12)
```bash
# Future command to set up vector DB
python scripts/generators/init_vector_db.py --config data/models/embeddings.yaml
```

---

## References

- **RAG Planning**: `planning/Sprints/Sprint_2026_12/` (future)
- **Test Infrastructure**: `Tests/` (uses data/inputs/fixtures for validation)
- **Architecture**: `docs/architecture/` (design decisions documented there)
