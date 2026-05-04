"""Shared state container for staged framework execution."""

from dataclasses import dataclass, field
from typing import Any

from .models import CanonicalThreatModelGraph


@dataclass
class FrameworkState:
    raw_text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)
    canonical_graph: CanonicalThreatModelGraph | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    stix_bundle: dict[str, Any] | None = None
    mermaid_diagrams: dict[str, str] = field(default_factory=dict)
    final_report: str | None = None
    human_feedback: str | None = None
    next_stage_id: str | None = None
    trust_boundary_review_needed: bool = False
    stride_complete: bool = False
    threats_generated: bool = False

    # HITL state — populated by gate engine interactions
    hitl_gate_checkpoint: dict[str, Any] | None = None  # serialised gate engine state
    hitl_paused_at_gate: str | None = None               # gate_id when pipeline is paused
    hitl_rejected_at_gate: str | None = None             # gate_id if analyst rejected

    def record_message(self, stage_id: str, text: str) -> None:
        self.messages.append({"stage_id": stage_id, "text": text})

    def canonical_graph_dict(self) -> dict[str, Any]:
        if self.canonical_graph is None:
            return {}
        return self.canonical_graph.to_dict()
