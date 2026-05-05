"""Agent 02 — Hierarchical Context Builder."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class ContextBuilderAgent(BaseAgent):
    display_name: str = "Context Builder"
    stage_id: str = "agent_02"
    _prompt_filename: str = "agent_02_hierarchical_context_builder.txt"
    _fixture_filename: str = "agent_02_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            state.canonical_graph = graph
        return state
