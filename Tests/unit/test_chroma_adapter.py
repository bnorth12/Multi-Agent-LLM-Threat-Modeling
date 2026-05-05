"""
Unit tests for ChromaAdapter.

All tests use ChromaDB's in-memory EphemeralClient — no server required.
"""

import json
import pathlib
import pytest

from threat_modeler.retrieval_adapters import ChromaAdapter


FIXTURE_CORPUS = pathlib.Path(__file__).parent.parent / "fixtures" / "retrieval" / "fixture_corpus.json"


def _load_corpus():
    with open(FIXTURE_CORPUS, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestChromaAdapterConstruction:
    def test_creates_ephemeral_by_default(self):
        adapter = ChromaAdapter()
        assert adapter.count == 0

    def test_custom_collection_name(self):
        adapter = ChromaAdapter(collection_name="test_collection_unique_abc123")
        assert adapter.count == 0

    def test_two_adapters_independent_collections(self):
        # Each adapter uses an auto-generated unique collection name, so they are isolated.
        a = ChromaAdapter()
        b = ChromaAdapter()
        a.ingest([{"id": "x", "text": "hello world"}])
        assert a.count == 1
        assert b.count == 0


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class TestIngest:
    def test_ingest_empty_list_is_noop(self):
        adapter = ChromaAdapter()
        adapter.ingest([])
        assert adapter.count == 0

    def test_ingest_adds_documents(self):
        adapter = ChromaAdapter()
        adapter.ingest(_load_corpus())
        assert adapter.count == 7

    def test_ingest_preserves_ids(self):
        adapter = ChromaAdapter()
        adapter.ingest([{"id": "abc", "text": "some content"}])
        result = adapter.retrieve("content", top_k=1)
        assert result[0]["source_id"] == "abc"

    def test_clear_removes_all_documents(self):
        adapter = ChromaAdapter()
        adapter.ingest(_load_corpus())
        adapter.clear()
        assert adapter.count == 0

    def test_ingest_after_clear(self):
        adapter = ChromaAdapter()
        adapter.ingest(_load_corpus())
        adapter.clear()
        adapter.ingest(_load_corpus()[:2])
        assert adapter.count == 2


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

class TestRetrieve:
    @pytest.fixture()
    def loaded_adapter(self):
        adapter = ChromaAdapter()
        adapter.ingest(_load_corpus())
        return adapter

    def test_retrieve_empty_corpus_returns_empty_list(self):
        adapter = ChromaAdapter()
        assert adapter.retrieve("injection") == []

    def test_retrieve_returns_list(self, loaded_adapter):
        results = loaded_adapter.retrieve("injection attack", top_k=3)
        assert isinstance(results, list)

    def test_retrieve_respects_top_k(self, loaded_adapter):
        results = loaded_adapter.retrieve("attack", top_k=2)
        assert len(results) <= 2

    def test_retrieve_result_has_required_keys(self, loaded_adapter):
        results = loaded_adapter.retrieve("SQL injection", top_k=1)
        assert len(results) == 1
        rec = results[0]
        assert "source_id" in rec
        assert "confidence" in rec
        assert "text" in rec
        assert "metadata" in rec

    def test_confidence_in_valid_range(self, loaded_adapter):
        results = loaded_adapter.retrieve("denial of service flood traffic", top_k=5)
        for rec in results:
            assert 0.0 <= rec["confidence"] <= 1.0

    def test_source_id_is_string(self, loaded_adapter):
        results = loaded_adapter.retrieve("authentication session", top_k=3)
        for rec in results:
            assert isinstance(rec["source_id"], str)

    def test_top_k_larger_than_corpus_returns_all(self):
        adapter = ChromaAdapter()
        adapter.ingest(_load_corpus()[:3])
        # When top_k > corpus size, all documents are returned.
        results = adapter.retrieve("security", top_k=100)
        assert len(results) == 3

    def test_metadata_is_dict(self, loaded_adapter):
        results = loaded_adapter.retrieve("injection", top_k=1)
        assert isinstance(results[0]["metadata"], dict)


# ---------------------------------------------------------------------------
# Schema fields contract
# ---------------------------------------------------------------------------

class TestSchemaFieldsContract:
    """Verify the canonical graph schema includes source_ids and confidence."""

    SCHEMA_PATH = pathlib.Path(__file__).parent.parent.parent / "docs" / "schemas" / "canonical_graph.schema.json"

    def test_schema_file_exists(self):
        assert self.SCHEMA_PATH.exists(), f"Schema not found at {self.SCHEMA_PATH}"

    def test_schema_has_source_ids_field(self):
        with open(self.SCHEMA_PATH, encoding="utf-8") as fh:
            content = fh.read()
        assert "source_ids" in content

    def test_schema_has_confidence_field(self):
        with open(self.SCHEMA_PATH, encoding="utf-8") as fh:
            content = fh.read()
        assert "confidence" in content

    def test_source_ids_is_array_type(self):
        import json
        with open(self.SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        # Find source_ids in interfaces.threats
        threat_props = (
            schema["properties"]["interfaces"]["items"]["properties"]["threats"]["items"]["properties"]
        )
        assert "source_ids" in threat_props
        assert threat_props["source_ids"]["type"] == "array"

    def test_confidence_allows_null(self):
        import json
        with open(self.SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        threat_props = (
            schema["properties"]["interfaces"]["items"]["properties"]["threats"]["items"]["properties"]
        )
        assert "confidence" in threat_props
        conf_type = threat_props["confidence"]["type"]
        assert "null" in conf_type

    def test_data_flows_threats_also_have_source_ids(self):
        import json
        with open(self.SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        threat_props = (
            schema["properties"]["data_flows"]["items"]["properties"]["threats"]["items"]["properties"]
        )
        assert "source_ids" in threat_props
        assert "confidence" in threat_props
