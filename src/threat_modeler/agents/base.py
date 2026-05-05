"""Base class for all pipeline agents."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..llm.base import FixtureAdapter, LlmAdapter
from ..state import FrameworkState


_AGENTS_PROMPT_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "agents"
_FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "Tests" / "fixtures" / "agents"
_DEFAULT_MAX_LIST_ITEMS = 40
_DEFAULT_MAX_STRING_CHARS = 600


@dataclass
class BaseAgent:
    """Common behaviour for all pipeline stage agents.

    Subclasses set ``display_name``, ``stage_id``, and ``_prompt_filename``
    and implement ``_apply(state, llm_response)`` to merge the LLM JSON
    response back into the state.
    """

    display_name: str
    stage_id: str
    adapter: LlmAdapter | None = None

    # Subclasses must set these class-level attributes.
    _prompt_filename: str = ""
    _fixture_filename: str = ""

    def _load_system_prompt(self) -> str:
        prompt_path = _AGENTS_PROMPT_DIR / self._prompt_filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return f"You are the {self.display_name} agent. Output JSON only."

    def _get_adapter(self) -> LlmAdapter:
        if self.adapter is not None:
            return self.adapter
        # Default: fixture mode
        fixture_path = _FIXTURES_DIR / self._fixture_filename
        return FixtureAdapter(fixture_path)

    def _max_user_message_chars(self) -> int | None:
        value = os.getenv("THREAT_MODELER_MAX_USER_MESSAGE_CHARS")
        if value is None:
            return None
        try:
            parsed = int(value)
            if parsed <= 0:
                return None
            return max(1000, parsed)
        except ValueError:
            return None

    def _reduce_prompt_payload(self, value: Any) -> Any:
        if isinstance(value, dict):
            out: dict[str, Any] = {}
            for key, sub_value in value.items():
                out[key] = self._reduce_prompt_payload(sub_value)
            return out

        if isinstance(value, list):
            trimmed = [self._reduce_prompt_payload(v) for v in value[:_DEFAULT_MAX_LIST_ITEMS]]
            if len(value) > _DEFAULT_MAX_LIST_ITEMS:
                trimmed.append({"_truncated_items": len(value) - _DEFAULT_MAX_LIST_ITEMS})
            return trimmed

        if isinstance(value, str) and len(value) > _DEFAULT_MAX_STRING_CHARS:
            return value[:_DEFAULT_MAX_STRING_CHARS] + "...[truncated]"

        return value

    def _summarize_prompt_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "system" in payload:
            interfaces = payload.get("interfaces", [])
            first_interfaces = [
                {
                    "id": i.get("id", ""),
                    "name": i.get("name", ""),
                    "protocol": i.get("protocol", ""),
                    "trust_boundary_crossing": i.get("trust_boundary_crossing", False),
                }
                for i in interfaces[:10]
                if isinstance(i, dict)
            ]
            return {
                "metadata": payload.get("metadata", {}),
                "system": payload.get("system", {}),
                "counts": {
                    "subsystems": len(payload.get("subsystems", [])),
                    "components": len(payload.get("components", [])),
                    "functions": len(payload.get("functions", [])),
                    "interfaces": len(interfaces),
                },
                "interfaces_preview": first_interfaces,
            }

        return {
            "raw_text_preview": str(payload.get("raw_text", ""))[:2000],
            "tables_count": len(payload.get("tables", [])),
        }

    def _serialize_payload(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    def _build_user_message(self, state: FrameworkState) -> str:
        payload = state.canonical_graph_dict() or {"raw_text": state.raw_text, "tables": state.tables}
        max_chars = self._max_user_message_chars()
        serialised = self._serialize_payload(payload)
        if max_chars is None:
            return serialised
        if len(serialised) <= max_chars:
            return serialised

        reduced_payload = self._reduce_prompt_payload(payload)
        reduced_serialised = self._serialize_payload(reduced_payload)
        reduced_envelope = {
            "truncated": True,
            "prompt_notice": "Input payload reduced to satisfy prompt size limit.",
            "payload": reduced_payload,
        }
        reduced_envelope_serialised = self._serialize_payload(reduced_envelope)
        if len(reduced_envelope_serialised) <= max_chars:
            return reduced_envelope_serialised

        summary_payload = self._summarize_prompt_payload(payload)
        summary_envelope = {
            "truncated": True,
            "prompt_notice": "Input payload summarized to satisfy prompt size limit.",
            "payload": summary_payload,
        }
        summary_envelope_serialised = self._serialize_payload(summary_envelope)
        if len(summary_envelope_serialised) <= max_chars:
            return summary_envelope_serialised

        # Final safety guard: ensure output is valid JSON and always within configured limit.
        minimal = {
            "truncated": True,
            "prompt_notice": "Input omitted due size constraints.",
            "payload": {
                "system_name": payload.get("system", {}).get("name", "") if isinstance(payload, dict) else "",
                "raw_text_preview": str(payload.get("raw_text", ""))[:400] if isinstance(payload, dict) else "",
            },
        }
        return self._serialize_payload(minimal)

    def _apply(self, state: FrameworkState, llm_response: str) -> FrameworkState:
        """Merge LLM JSON response into state. Override in subclasses."""
        return state

    def run(self, state: FrameworkState) -> FrameworkState:
        adapter = self._get_adapter()
        system_prompt = self._load_system_prompt()
        user_message = self._build_user_message(state)
        response = adapter.complete(system_prompt, user_message)
        state = self._apply(state, response)
        state.record_message(self.stage_id, f"{self.display_name} completed.")
        return state
