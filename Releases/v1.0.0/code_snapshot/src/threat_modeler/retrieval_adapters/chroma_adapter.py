"""
ChromaDB vector store adapter implementing the Retriever interface.

Uses an ephemeral (in-memory) ChromaDB client by default so no external server
is required.  Pass a persistent Client when you need on-disk storage.

Usage
-----
    from threat_modeler.retrieval_adapters import ChromaAdapter

    adapter = ChromaAdapter()                     # ephemeral
    adapter.ingest(documents)                      # list of {id, text, metadata}
    results = adapter.retrieve("injection", top_k=3)
    # [{"source_id": "...", "confidence": 0.87, "text": "...", "metadata": {...}}, ...]
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb import EphemeralClient


class ChromaAdapter:
    """Retriever adapter backed by a ChromaDB collection.

    Parameters
    ----------
    collection_name:
        Name of the ChromaDB collection to create/use.
    client:
        An existing ``chromadb.Client`` instance.  When *None* an ephemeral
        (in-memory) client is created automatically — suitable for tests and
        offline usage.
    """

    def __init__(
        self,
        collection_name: str | None = None,
        client: Optional[chromadb.ClientAPI] = None,
    ) -> None:
        self._client: chromadb.ClientAPI = client if client is not None else EphemeralClient()
        # Use a unique name by default so each adapter instance has an isolated collection.
        _name = collection_name if collection_name is not None else f"tm_{uuid.uuid4().hex}"
        self._collection = self._client.get_or_create_collection(
            name=_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the collection.

        Each document must contain:
          * ``id``   (str) — unique identifier
          * ``text`` (str) — content that will be embedded / matched

        Any additional keys are stored as metadata.
        """
        if not documents:
            return

        ids: List[str] = []
        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for doc in documents:
            doc_id = str(doc["id"])
            text = str(doc.get("text", ""))
            raw_meta = {k: v for k, v in doc.items() if k not in ("id", "text")}
            # ChromaDB requires flat metadata values (str, int, float, bool, or None).
            # Flatten nested dicts/lists to JSON strings.
            meta: Dict[str, Any] = {}
            for k, v in raw_meta.items():
                if isinstance(v, (str, int, float, bool)) or v is None:
                    meta[k] = v
                else:
                    meta[k] = json.dumps(v)
            # ChromaDB 1.x rejects empty metadata dicts; use a sentinel instead.
            if not meta:
                meta = {"_placeholder": "true"}
            ids.append(doc_id)
            texts.append(text)
            metadatas.append(meta)

        self._collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def clear(self) -> None:
        """Remove all documents from the collection."""
        existing = self._collection.get()
        if existing["ids"]:
            self._collection.delete(ids=existing["ids"])

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query the collection and return results with retrieval metadata.

        Returns a list of dicts, each containing:
          * ``source_id``  (str)
          * ``confidence`` (float) — cosine similarity score in ``[0.0, 1.0]``
          * ``text``       (str)
          * ``metadata``   (dict)
        """
        count = self._collection.count()
        if count == 0:
            return []

        k = min(top_k, count)
        response = self._collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        results: List[Dict[str, Any]] = []
        ids = response.get("ids", [[]])[0]
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        for doc_id, text, meta, distance in zip(ids, documents, metadatas, distances):
            # ChromaDB cosine distance is in [0, 2]; convert to similarity in [0, 1]
            confidence = float(max(0.0, min(1.0, 1.0 - distance / 2.0)))
            results.append(
                {
                    "source_id": str(doc_id),
                    "confidence": round(confidence, 6),
                    "text": text,
                    "metadata": meta or {},
                }
            )

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Number of documents currently in the collection."""
        return self._collection.count()
