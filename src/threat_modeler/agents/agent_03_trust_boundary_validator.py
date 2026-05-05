"""Agent 03 — Trust Boundary Validator and Enricher."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class TrustBoundaryValidatorAgent(BaseAgent):
    display_name: str = "Trust Boundary Validator"
    stage_id: str = "agent_03"
    _prompt_filename: str = "agent_03_trust_boundary_validator.txt"
    _fixture_filename: str = "agent_03_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            state.canonical_graph = graph
            # Flag for HITL if any interface needs review
            state.trust_boundary_review_needed = any(
                getattr(iface, "trust_boundary_review_needed", False)
                for iface in graph.interfaces
            )
        return state
