"""Agent 08 — Diagram Generator."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .base import BaseAgent
from ..state import FrameworkState

_SECTION_PATTERN = re.compile(
    r"MERMAID_LEVEL(\d)\s*```mermaid(.*?)```", re.DOTALL
)


@dataclass
class DiagramGeneratorAgent(BaseAgent):
    display_name: str = "Diagram Generator"
    stage_id: str = "agent_08"
    _prompt_filename: str = "agent_08_diagram_generator.txt"
    _fixture_filename: str = "agent_08_output.txt"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        diagrams: dict[str, str] = {}
        for match in _SECTION_PATTERN.finditer(llm_response):
            level = f"level_{match.group(1)}"
            diagrams[level] = match.group(2).strip()
        if diagrams:
            state.mermaid_diagrams = diagrams
        else:
            state.record_message(self.stage_id, "Diagram Generator: no MERMAID_LEVEL sections found in response.")
        return state
