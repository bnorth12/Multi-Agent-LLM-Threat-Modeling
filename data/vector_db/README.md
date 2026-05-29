# Vector Database Index Storage

**Purpose:** Persistent storage for vector embeddings generated from architecture and threat documentation.

## Structure

- `indexes/`: FAISS or Chroma vector index files (binary, not tracked in git)
- `config.yaml`: Embedding model and index configuration
- `.gitignore`: Excludes binary index files from version control

## Configuration

See `config.yaml` in this directory for embedding model selection, dimensions, and chunk parameters.

## Example Usage (Optional Local Index Workflow)

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = FAISS.load_local("data/vector_db/indexes", embeddings)

# Query for architecture context
results = vector_db.similarity_search("threat to API gateway", k=5)
```

## Maintenance

- **Index size management**: Configure `chunk_size` and `overlap` in `config.yaml`
- **Cleanup**: Delete `indexes/` directory to rebuild (safe due to `.gitignore`)
- **Rebuild**: Re-run ingestion pipeline to regenerate indexes

## See Also

- `data/models/embeddings.yaml` - Available embedding models
- `data/inputs/` - Source documents for indexing
