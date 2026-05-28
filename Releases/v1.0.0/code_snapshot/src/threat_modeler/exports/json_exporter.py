"""
JSON exporter — serialises a CanonicalThreatModelGraph to a JSON string.

Includes source_ids and confidence retrieval evidence fields when present.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..models import CanonicalThreatModelGraph


def export_json(graph: CanonicalThreatModelGraph, *, indent: int = 2) -> str:
    """Return the canonical graph serialised as a JSON string.

    Parameters
    ----------
    graph:
        The canonical threat model graph to export.
    indent:
        JSON indentation level (default 2).

    Returns
    -------
    str
        JSON-encoded representation of the full graph.
    """
    data: dict[str, Any] = asdict(graph)
    return json.dumps(data, indent=indent, ensure_ascii=False)
