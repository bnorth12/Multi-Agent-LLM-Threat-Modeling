"""Agent 01 — Input Normalizer and Graph Builder."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseAgent
from .deserialise import parse_graph_json
from ..state import FrameworkState


@dataclass
class InputNormalizerAgent(BaseAgent):
    display_name: str = "Input Normalizer"
    stage_id: str = "agent_01"
    _prompt_filename: str = "agent_01_input_normalizer.txt"
    _fixture_filename: str = "agent_01_output.json"

    def _build_user_message(self, state: FrameworkState) -> str:
        import json
        payload = {
            "raw_text": state.raw_text,
            "tables": state.tables,
        }
        return json.dumps(payload, ensure_ascii=False)

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        graph = parse_graph_json(llm_response)
        if graph is not None:
            state.canonical_graph = graph
        return state
