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
            # Preserve prior graph fields when a partial response omits collections.
            if state.canonical_graph is not None:
                if not graph.system.name and state.canonical_graph.system.name:
                    graph.system.name = state.canonical_graph.system.name
                if not graph.system.description and state.canonical_graph.system.description:
                    graph.system.description = state.canonical_graph.system.description
                if not graph.subsystems and state.canonical_graph.subsystems:
                    graph.subsystems = list(state.canonical_graph.subsystems)
                if not graph.components and state.canonical_graph.components:
                    graph.components = list(state.canonical_graph.components)
                if not graph.functions and state.canonical_graph.functions:
                    graph.functions = list(state.canonical_graph.functions)
                if not graph.interfaces and state.canonical_graph.interfaces:
                    graph.interfaces = list(state.canonical_graph.interfaces)

                previous_by_id = {iface.id: iface for iface in state.canonical_graph.interfaces if iface.id}
                for iface in graph.interfaces:
                    if iface.trust_boundary_name and not iface.trust_boundary_crossing:
                        iface.trust_boundary_crossing = True
                    previous = previous_by_id.get(iface.id)
                    if previous is not None and previous.trust_boundary_crossing and not iface.trust_boundary_crossing:
                        iface.trust_boundary_crossing = True
                        if not iface.trust_boundary_name:
                            iface.trust_boundary_name = previous.trust_boundary_name
            state.canonical_graph = graph
            # Flag for HITL when any interface crosses a trust boundary.
            state.trust_boundary_review_needed = any(
                bool(getattr(iface, "trust_boundary_crossing", False))
                for iface in graph.interfaces
            )
        return state
