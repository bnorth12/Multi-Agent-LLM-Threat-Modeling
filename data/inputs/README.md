# Ingestion Sources for RAG Pipeline

**Purpose:** Centralized location for documents, threat catalogs, and test data to be ingested into the vector database.

## Subdirectories

### `architecture_docs/`
System and operational documentation for ingestion into RAG pipeline.

**Expected contents:**
- System architecture diagrams and descriptions
- API specifications and contracts
- Design decision records (ADRs)
- Technology stack documentation
- Data flow diagrams

**Usage:** Source documents from this directory will be embedded and stored in `vector_db/indexes/`.

### `threat_libraries/`
Reference threat models, vulnerabilities, and security patterns.

**Expected contents:**
- STRIDE threat templates
- OWASP Top 10 / OWASP API Security mappings
- Common vulnerability patterns (CWE/CVE reference data)
- Threat intelligence feeds (if applicable)
- Custom threat catalogs specific to organization

**Usage:** Provide context for threat generation and validation in RAG pipeline.

### `fixtures/`
Test data and validation fixtures for RAG system.

**Expected contents:**
- Sample threat models for pipeline validation
- Reference architecture documents
- Test cases for embedding quality assurance
- Expected outputs for regression testing

**Usage:** Validate embedding pipeline quality and RAG retrieval accuracy.

## Ingestion Workflow

1. **Place documents** in appropriate subdirectory
2. **Run ingestion script** (future): `python scripts/generators/ingest_data.py`
3. **Embeddings generated** and stored in `data/vector_db/indexes/`
4. **Retrieval enabled** for RAG queries

## Notes

- `.gitignore` excludes `fetched/` subdirectory for downloaded remote content
- Keep source documents organized by category for easier management
- Large PDFs or binary documents should be pre-processed to text format

## See Also

- `data/vector_db/` - Output location for embeddings
- `data/models/embeddings.yaml` - Embedding model configuration
