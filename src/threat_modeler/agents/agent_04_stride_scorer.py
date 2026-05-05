"""Agent 04 — STRIDE Per Element Scorer."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class StrideScorer(BaseAgent):
    display_name: str = "STRIDE Scorer"
    stage_id: str = "agent_04"
    _prompt_filename: str = "agent_04_stride_scorer.txt"
    _fixture_filename: str = "agent_04_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            state.canonical_graph = graph
            state.stride_complete = True
        return state
