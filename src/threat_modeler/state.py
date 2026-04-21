"""Shared state container for staged framework execution."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FrameworkState:
    raw_text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)
    canonical_graph: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    stix_bundle: dict[str, Any] | None = None
    mermaid_diagrams: dict[str, str] = field(default_factory=dict)
    final_report: str | None = None
    human_feedback: str | None = None
    next_stage_id: str | None = None
    trust_boundary_review_needed: bool = False
    stride_complete: bool = False
    threats_generated: bool = False

    def record_message(self, stage_id: str, text: str) -> None:
        self.messages.append({"stage_id": stage_id, "text": text})
