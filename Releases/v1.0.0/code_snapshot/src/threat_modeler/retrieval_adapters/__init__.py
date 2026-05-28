"""
Retrieval adapter implementations.

Exports the ChromaAdapter for use alongside the existing Retriever abstraction.
"""

from .chroma_adapter import ChromaAdapter

__all__ = ["ChromaAdapter"]
