"""
Unit tests for retrieval.py (Retrieval/Knowledge Layer MVP)
"""
from src.threat_modeler.retrieval import CorpusIngestor, Retriever

def test_corpus_ingestor_ingest_and_clear():
    ingestor = CorpusIngestor()
    docs = [{"text": "alpha"}, {"text": "beta"}]
    ingestor.ingest(docs)
    assert len(ingestor.corpus) == 2
    ingestor.clear()
    assert len(ingestor.corpus) == 0

def test_retriever_retrieve_and_citation():
    docs = [
        {"text": "threat modeling for alpha", "id": "doc1"},
        {"text": "beta risk analysis", "id": "doc2"},
        {"text": "gamma controls", "id": "doc3"},
    ]
    retriever = Retriever(docs)
    results = retriever.retrieve("alpha")
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    cited = retriever.add_citation_metadata(results[0], source_id="doc1", confidence=0.95)
    assert cited["source_id"] == "doc1"
    assert cited["confidence"] == 0.95
