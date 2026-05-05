"""Agent 07 — Mitigation Generator."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class MitigationGeneratorAgent(BaseAgent):
    display_name: str = "Mitigation Generator"
    stage_id: str = "agent_07"
    _prompt_filename: str = "agent_07_mitigation_generator.txt"
    _fixture_filename: str = "agent_07_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            state.canonical_graph = graph
        return state
