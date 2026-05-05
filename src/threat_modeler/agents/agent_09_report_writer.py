"""Agent 09 — Human Report Writer."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseAgent
from ..state import FrameworkState

_REQUIRED_SECTIONS = [
    "Executive Summary",
    "System Scope",
    "Trust Boundaries",
    "Data Flow Diagrams",
    "STRIDE Findings",
    "Top Threats",
    "Mitigation Mapping",
]


@dataclass
class ReportWriterAgent(BaseAgent):
    display_name: str = "Report Writer"
    stage_id: str = "agent_09"
    _prompt_filename: str = "agent_09_human_report_writer.txt"
    _fixture_filename: str = "agent_09_output.md"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        missing = [s for s in _REQUIRED_SECTIONS if s.lower() not in llm_response.lower()]
        if missing:
            state.record_message(
                self.stage_id,
                f"Report Writer: missing required sections: {missing}",
            )
        state.final_report = llm_response
        return state
