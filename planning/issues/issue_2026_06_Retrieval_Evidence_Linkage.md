# Issue: Sprint 2026-06 Retrieval Evidence Linkage

## Sprint
2026-06

## GitHub Issue
GH #20

## Owner Role
Data and Parsing Engineer and Validation and Schema Engineer

## Description
Add source identifier and confidence metadata fields to threat and mitigation output schemas, wire the
existing `Retriever` abstraction to a ChromaDB vector store adapter, and validate the retrieval path
with a fixture corpus. Full live retrieval during threat generation is out of scope for this sprint
(deferred to S07); this sprint establishes the schema contract and one working adapter.

## Scope

### Schema Fields
- Add `source_ids: list[str]` and `confidence: float | None` to the canonical graph threat and
  mitigation output structures.
- Update `docs/schemas/canonical_graph.schema.json` to include these fields.
- Fields are optional (nullable/empty-list) when retrieval is disabled.

### ChromaDB Adapter
- Add `src/threat_modeler/retrieval_adapters/chroma_adapter.py` implementing the `Retriever`
  interface using ChromaDB as the backing store.
- Adapter wraps ChromaDB `Collection` for `retrieve()` and corpus ingest.
- `set_provider("chroma")` activates the adapter; default/naive keyword provider remains unchanged.
- ChromaDB dependency added to `requirements.txt` (or `pyproject.toml`).

### Fixture Corpus Ingest
- Add `Tests/fixtures/retrieval/fixture_corpus.json` with at least five sample documents
  (id, text, metadata fields).
- Integration test ingests fixture corpus into ChromaDB in-memory mode and validates retrieval
  returns source IDs and confidence values.

## Acceptance Criteria
- Canonical graph schema includes `source_ids` and `confidence` fields with correct types.
- When retrieval is enabled, threat and mitigation outputs carry non-empty `source_ids` and
  a `confidence` value in `[0.0, 1.0]`.
- When retrieval is disabled, `source_ids` is an empty list and `confidence` is null/None.
- `chroma_adapter.py` passes `Retriever` interface contract: `retrieve(query, top_k)` returns
  records with `source_id` and `confidence`.
- Fixture corpus integration test passes without requiring a running ChromaDB server
  (in-memory ephemeral client).
- All retrieval paths are covered by unit and integration tests.

## Requirement Links
- PRJ-010
- INT-008

## Dependencies
- S06-01 (Agent Pipeline Completeness) — threat/mitigation output structures are produced by agents
  05 and 07.

## Implementation Notes
- ChromaDB supports an in-memory ephemeral client (`chromadb.EphemeralClient()`) with no server
  required — use this for all tests.
- Do not implement live retrieval injection into agent LLM calls this sprint; that is S07 scope.
- `retrieval.py` already contains `CorpusIngestor`, `Retriever`, and `add_citation_metadata` stubs;
  extend rather than replace.

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- `source_ids: list[str]` and `confidence: float | None` added to canonical graph schema; `docs/schemas/canonical_graph.schema.json` updated.
- `src/threat_modeler/retrieval_adapters/chroma_adapter.py` implements `Retriever` interface using ChromaDB ephemeral client.
- `Tests/fixtures/retrieval/fixture_corpus.json` contains 5 sample documents.
- Integration test `Tests/integration/test_retrieval_evidence_linkage.py` passes without a running server (in-memory).
- Unit tests in `Tests/unit/test_chroma_adapter.py` cover adapter contract.
- CI test run: 240 passed, 1 deselected (llm_live), 0 failures.
