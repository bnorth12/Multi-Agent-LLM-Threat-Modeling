"""Artifact grouping models used by the runtime skeleton."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExportArtifacts:
    stix_bundle: dict[str, Any] | None = None
    mermaid_diagrams: dict[str, str] = field(default_factory=dict)
    final_report: str | None = None


@dataclass
class ThreatModelArtifactSet:
    canonical_graph: dict[str, Any] = field(default_factory=dict)
    exports: ExportArtifacts = field(default_factory=ExportArtifacts)
