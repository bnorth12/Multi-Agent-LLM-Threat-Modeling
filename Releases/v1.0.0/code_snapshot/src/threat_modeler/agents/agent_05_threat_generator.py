"""Agent 05 — Concrete Threat Generator."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class ThreatGeneratorAgent(BaseAgent):
    display_name: str = "Threat Generator"
    stage_id: str = "agent_05"
    _prompt_filename: str = "agent_05_concrete_threat_generator.txt"
    _fixture_filename: str = "agent_05_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            # Preserve system name and description from previous graph if not set in new graph
            if state.canonical_graph is not None:
                if not graph.system.name and state.canonical_graph.system.name:
                    graph.system.name = state.canonical_graph.system.name
                if not graph.system.description and state.canonical_graph.system.description:
                    graph.system.description = state.canonical_graph.system.description
            state.canonical_graph = graph
            state.threats_generated = True
        return state
