"""Unit tests for SCR-015 last-prompt diagnostics support."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from threat_modeler.agents.base import BaseAgent
from threat_modeler.llm.base import LlmAdapter
from threat_modeler.state import FrameworkState
from threat_modeler.ui.runtime_io import framework_state_from_dict, framework_state_to_dict


class _TimeoutAdapter(LlmAdapter):
    def complete(self, system_prompt: str, user_message: str) -> str:  # pragma: no cover - trivial
        raise TimeoutError("timed out")


def test_base_agent_records_prompt_before_timeout() -> None:
    state = FrameworkState(raw_text="hello")
    agent = BaseAgent(
        display_name="Test Agent",
        stage_id="agent_01",
        adapter=_TimeoutAdapter(),
        _prompt_filename="agent_01_input_normalizer.txt",
    )

    with pytest.raises(TimeoutError):
        agent.run(state)

    latest = state.latest_llm_prompt()
    assert latest is not None
    assert latest["stage_id"] == "agent_01"
    assert latest["provider"] == "_TimeoutAdapter"
    assert latest["system_prompt"]
    assert latest["user_message"]
    assert latest["user_message_chars"] == len(latest["user_message"])


def test_framework_state_round_trip_includes_prompt_history() -> None:
    state = FrameworkState()
    state.record_llm_prompt(
        "agent_04",
        {
            "provider": "OpenAiCompatibleAdapter",
            "endpoint_mode": "chat_completions",
            "model": "grok-4",
            "system_prompt": "sys",
            "user_message": "user",
            "system_prompt_chars": 3,
            "user_message_chars": 4,
        },
    )

    payload = framework_state_to_dict(state)
    restored = framework_state_from_dict(payload)

    assert "agent_04" in restored.llm_prompts_by_stage
    assert len(restored.llm_prompt_history) == 1
    assert restored.llm_prompt_history[0]["stage_id"] == "agent_04"


def test_app_navigation_includes_last_prompt_page() -> None:
    tree = ast.parse(Path("src/threat_modeler/ui/app.py").read_text(encoding="utf-8"))
    strings = [
        node.s if isinstance(node, ast.Constant) and isinstance(node.s, str) else None
        for node in ast.walk(tree)
    ]
    assert "Last Prompt" in strings


def test_last_prompt_screen_module_exposes_render() -> None:
    from threat_modeler.ui.screens.last_prompt import render

    assert callable(render)


def test_last_prompt_screen_contains_dark_mode_contrast_style() -> None:
    text = Path("src/threat_modeler/ui/screens/last_prompt.py").read_text(encoding="utf-8")
    assert "_apply_dark_prompt_text_style" in text
    assert "textarea[disabled]" in text
