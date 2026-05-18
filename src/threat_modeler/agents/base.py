"""Base class for all pipeline agents."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..llm.base import FixtureAdapter, LlmAdapter
from ..state import FrameworkState


logger = logging.getLogger(__name__)


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
    require_live_adapter: bool = False

    # Subclasses must set these class-level attributes.
    _prompt_filename: str = ""
    _fixture_filename: str = ""

    def _load_system_prompt_from_file(self) -> str:
        prompt_path = _AGENTS_PROMPT_DIR / self._prompt_filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return f"You are the {self.display_name} agent. Output JSON only."

    def _load_system_prompt(self) -> str:
        try:
            from ..backend.prompt_store import get_prompt
            return get_prompt(self.stage_id)
        except ImportError as e:
            logger.warning(
                f"Backend prompt store not available for {self.stage_id}; falling back to file-based prompt. "
                f"ImportError: {e}"
            )
            return self._load_system_prompt_from_file()
        except KeyError as e:
            logger.warning(
                f"Prompt not found in backend store for {self.stage_id}; falling back to file-based prompt. "
                f"KeyError: {e}"
            )
            return self._load_system_prompt_from_file()
        except Exception as e:
            logger.error(
                f"Unexpected error loading system prompt for {self.stage_id}: {type(e).__name__}: {e}. "
                f"Falling back to file-based prompt."
            )
            return self._load_system_prompt_from_file()

    def _load_expected_output(self) -> str:
        try:
            from ..backend.prompt_store import get_expected_output
            return get_expected_output(self.stage_id)
        except ImportError as e:
            logger.debug(
                f"Backend prompt store not available for expected output of {self.stage_id}. "
                f"ImportError: {e}"
            )
            return ""
        except KeyError as e:
            logger.debug(
                f"Expected output not found in backend store for {self.stage_id}. "
                f"KeyError: {e}"
            )
            return ""
        except Exception as e:
            logger.error(
                f"Unexpected error loading expected output for {self.stage_id}: {type(e).__name__}: {e}"
            )
            return ""

    def _compose_system_prompt(self, system_prompt: str, expected_output: str) -> str:
        if not expected_output.strip():
            return system_prompt
        return (
            f"{system_prompt.rstrip()}\n\n"
            "Expected output example (match structure and ordering style; do not copy literal values unless input supports them):\n"
            "--- EXPECTED_OUTPUT_EXAMPLE_START ---\n"
            f"{expected_output.rstrip()}\n"
            "--- EXPECTED_OUTPUT_EXAMPLE_END ---"
        )

    def _get_adapter(self) -> LlmAdapter:
        if self.adapter is not None:
            return self.adapter
        if self.require_live_adapter:
            raise RuntimeError(
                f"Live adapter required for {self.stage_id} ({self.display_name}) but adapter is missing. "
                "Execution halted to prevent fallback to fixture mode."
            )
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
        expected_output = self._load_expected_output()
        llm_system_prompt = self._compose_system_prompt(system_prompt, expected_output)
        user_message = self._build_user_message(state)
        endpoint_mode = str(getattr(adapter, "_endpoint_mode", ""))
        model_name = str(getattr(adapter, "_model", ""))
        prompt_record_id = f"{self.stage_id}:{time.time_ns()}"
        state.record_llm_prompt(
            self.stage_id,
            {
                "prompt_record_id": prompt_record_id,
                "provider": str(getattr(adapter, "__class__", type(adapter)).__name__),
                "endpoint_mode": endpoint_mode,
                "model": model_name,
                "system_prompt": system_prompt,
                "expected_output": expected_output,
                "llm_system_prompt": llm_system_prompt,
                "user_message": user_message,
                "system_prompt_chars": len(system_prompt),
                "expected_output_chars": len(expected_output),
                "llm_system_prompt_chars": len(llm_system_prompt),
                "user_message_chars": len(user_message),
            },
        )
        state.record_llm_attempt(
            self.stage_id,
            {
                "prompt_record_id": prompt_record_id,
                "status": "submitted",
                "provider": str(getattr(adapter, "__class__", type(adapter)).__name__),
                "endpoint_mode": endpoint_mode,
                "model": model_name,
            },
        )
        try:
            response = adapter.complete(llm_system_prompt, user_message)
        except Exception as exc:
            state.record_llm_attempt(
                self.stage_id,
                {
                    "prompt_record_id": prompt_record_id,
                    "status": "failed",
                    "provider": str(getattr(adapter, "__class__", type(adapter)).__name__),
                    "endpoint_mode": endpoint_mode,
                    "model": model_name,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
            raise

        state.record_llm_attempt(
            self.stage_id,
            {
                "prompt_record_id": prompt_record_id,
                "status": "completed",
                "provider": str(getattr(adapter, "__class__", type(adapter)).__name__),
                "endpoint_mode": endpoint_mode,
                "model": model_name,
                # Keep a bounded response body for operator diagnostics.
                "response_chars": len(response),
                "response_preview": response[:2000],
                "response_text": response[:20000],
            },
        )

        usage = adapter.usage_snapshot() if hasattr(adapter, "usage_snapshot") else {}
        if usage:
            state.record_llm_usage(self.stage_id, usage)
        state = self._apply(state, response)
        state.record_message(self.stage_id, f"{self.display_name} completed.")
        return state
