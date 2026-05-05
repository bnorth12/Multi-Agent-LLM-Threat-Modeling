"""Agent 06 — STIX 2.1 Packager."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .base import BaseAgent
from ..state import FrameworkState


@dataclass
class StixPackagerAgent(BaseAgent):
    display_name: str = "STIX Packager"
    stage_id: str = "agent_06"
    _prompt_filename: str = "agent_06_stix_packager.txt"
    _fixture_filename: str = "agent_06_output.json"

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        text = llm_response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            bundle = json.loads(text)
            if isinstance(bundle, dict):
                state.stix_bundle = bundle
        except json.JSONDecodeError:
            state.record_message(self.stage_id, "STIX Packager: failed to parse STIX bundle from response.")
        return state
