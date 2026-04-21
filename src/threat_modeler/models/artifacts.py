"""Artifact grouping models used by the runtime skeleton."""

from dataclasses import dataclass, field
from typing import Any

from .canonical import CanonicalThreatModelGraph


@dataclass
class ExportArtifacts:
    stix_bundle: dict[str, Any] | None = None
    mermaid_diagrams: dict[str, str] = field(default_factory=dict)
    final_report: str | None = None


@dataclass
class ThreatModelArtifactSet:
    canonical_graph: CanonicalThreatModelGraph = field(default_factory=CanonicalThreatModelGraph)
    exports: ExportArtifacts = field(default_factory=ExportArtifacts)
