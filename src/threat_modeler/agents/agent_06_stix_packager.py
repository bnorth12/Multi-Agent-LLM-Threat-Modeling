"""Agent 06 — STIX 2.1 Packager."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .base import BaseAgent
from ..exports import export_stix
from ..state import FrameworkState

_JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


@dataclass
class StixPackagerAgent(BaseAgent):
    display_name: str = "STIX Packager"
    stage_id: str = "agent_06"
    _prompt_filename: str = "agent_06_stix_packager.txt"
    _fixture_filename: str = "agent_06_output.json"

    def _extract_json_candidate(self, llm_response: str) -> str:
        text = llm_response.strip()
        match = _JSON_BLOCK_PATTERN.search(text)
        if match:
            return match.group(1)
        if text.startswith("```"):
            lines = text.splitlines()
            return "\n".join(lines[1:-1] if lines and lines[-1].strip() == "```" else lines[1:])
        return text

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        text = self._extract_json_candidate(llm_response)
        try:
            bundle = json.loads(text)
            if isinstance(bundle, dict):
                state.stix_bundle = bundle
                return state
        except json.JSONDecodeError:
            pass

        # Fallback: derive STIX from canonical graph when model output format drifts.
        if state.canonical_graph is not None:
            bundle_obj = export_stix(state.canonical_graph)
            state.stix_bundle = json.loads(bundle_obj.serialize())
            state.record_message(self.stage_id, "STIX Packager: used canonical graph fallback export.")
        else:
            state.record_message(self.stage_id, "STIX Packager: failed to parse STIX bundle from response.")
        return state
