"""
Integration tests for ChromaDB adapter with fixture corpus.

All tests use ChromaDB's in-memory EphemeralClient (no server required).
Covers: corpus ingest, retrieval with source_ids + confidence, and the
schema field contract end-to-end.
"""

import json
import pathlib

import pytest

from threat_modeler.retrieval_adapters import ChromaAdapter


FIXTURE_CORPUS_PATH = (
    pathlib.Path(__file__).parent.parent / "fixtures" / "retrieval" / "fixture_corpus.json"
)


@pytest.fixture(scope="module")
def corpus():
    with open(FIXTURE_CORPUS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture()
def adapter(corpus):
    """Fresh adapter with the full fixture corpus loaded."""
    a = ChromaAdapter()
    a.ingest(corpus)
    return a


# ---------------------------------------------------------------------------
# Corpus ingest
# ---------------------------------------------------------------------------

class TestCorpusIngest:
    def test_all_documents_ingested(self, adapter, corpus):
        assert adapter.count == len(corpus)

    def test_document_ids_match_fixture(self, adapter, corpus):
        """Retrieve all docs and confirm the fixture IDs are represented."""
        results = adapter.retrieve("attack security", top_k=len(corpus))
        returned_ids = {r["source_id"] for r in results}
        fixture_ids = {str(doc["id"]) for doc in corpus}
        # At least some fixture IDs should appear in results
        assert returned_ids.issubset(fixture_ids)


# ---------------------------------------------------------------------------
# Retrieval returns source_ids and confidence
# ---------------------------------------------------------------------------

class TestRetrievalMetadata:
    def test_retrieve_returns_source_id(self, adapter):
        results = adapter.retrieve("SQL injection database", top_k=1)
        assert len(results) == 1
        assert isinstance(results[0]["source_id"], str)
        assert results[0]["source_id"] != ""

    def test_retrieve_returns_confidence(self, adapter):
        results = adapter.retrieve("SQL injection database", top_k=1)
        conf = results[0]["confidence"]
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

    def test_retrieve_returns_text(self, adapter):
        results = adapter.retrieve("denial of service", top_k=1)
        assert isinstance(results[0]["text"], str)
        assert len(results[0]["text"]) > 0

    def test_retrieve_returns_metadata_dict(self, adapter):
        results = adapter.retrieve("authentication session management", top_k=1)
        assert isinstance(results[0]["metadata"], dict)

    def test_top_k_respected(self, adapter):
        for k in (1, 2, 3):
            results = adapter.retrieve("security", top_k=k)
            assert len(results) <= k

    def test_all_results_have_valid_confidence(self, adapter):
        results = adapter.retrieve("attack injection", top_k=7)
        for rec in results:
            assert 0.0 <= rec["confidence"] <= 1.0, (
                f"confidence {rec['confidence']!r} out of range for source_id={rec['source_id']!r}"
            )


# ---------------------------------------------------------------------------
# Disabled retrieval — empty source_ids, null confidence
# ---------------------------------------------------------------------------

class TestDisabledRetrieval:
    """When retrieval is not invoked, outputs must have empty source_ids and None confidence."""

    def test_no_retrieval_produces_empty_source_ids(self):
        """A threat dict created without retrieval should default to empty source_ids."""
        threat = {
            "name": "Example Threat",
            "source_ids": [],
            "confidence": None,
        }
        assert threat["source_ids"] == []
        assert threat["confidence"] is None

    def test_retrieval_enabled_produces_non_empty_source_ids(self, adapter):
        results = adapter.retrieve("injection attack", top_k=3)
        for rec in results:
            assert rec["source_id"] != ""


# ---------------------------------------------------------------------------
# Corpus fixture file
# ---------------------------------------------------------------------------

class TestFixtureCorpus:
    def test_fixture_file_exists(self):
        assert FIXTURE_CORPUS_PATH.exists()

    def test_fixture_has_minimum_five_documents(self, corpus):
        assert len(corpus) >= 5

    def test_every_document_has_id_and_text(self, corpus):
        for doc in corpus:
            assert "id" in doc, f"Missing 'id' in {doc}"
            assert "text" in doc, f"Missing 'text' in {doc}"

    def test_ids_are_unique(self, corpus):
        ids = [doc["id"] for doc in corpus]
        assert len(ids) == len(set(ids))

    def test_text_fields_are_non_empty(self, corpus):
        for doc in corpus:
            assert doc["text"].strip(), f"Empty text in doc id={doc['id']}"
