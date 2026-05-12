"""Unit tests for token usage state/runtime export helpers."""

from __future__ import annotations

import json
from pathlib import Path

from threat_modeler.state import FrameworkState
from threat_modeler.ui.runtime_io import export_token_usage_json, framework_state_from_dict, framework_state_to_dict


def test_framework_state_records_and_sums_token_usage() -> None:
    state = FrameworkState()
    state.record_llm_usage(
        "agent_02",
        {
            "prompt_tokens": 10,
            "completion_tokens": 7,
            "reasoning_tokens": 2,
            "cached_tokens": 1,
            "total_tokens": 17,
        },
    )
    state.record_llm_usage(
        "agent_03",
        {
            "prompt_tokens": 5,
            "completion_tokens": 8,
            "reasoning_tokens": 0,
            "cached_tokens": 0,
            "total_tokens": 13,
        },
    )

    totals = state.llm_usage_totals()
    assert totals["prompt_tokens"] == 15
    assert totals["completion_tokens"] == 15
    assert totals["reasoning_tokens"] == 2
    assert totals["cached_tokens"] == 1
    assert totals["total_tokens"] == 30
    assert totals["request_count"] == 2


def test_runtime_io_serializes_token_usage_fields() -> None:
    state = FrameworkState()
    state.record_llm_usage("agent_01", {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5})
    state.record_llm_attempt("agent_01", {"status": "submitted"})
    state.record_llm_attempt("agent_01", {"status": "completed"})
    state.record_llm_prompt("agent_01", {"system_prompt": "sys", "user_message": "user"})

    payload = framework_state_to_dict(state)
    restored = framework_state_from_dict(payload)

    assert "agent_01" in restored.llm_usage_by_stage
    assert restored.llm_usage_by_stage["agent_01"][0]["total_tokens"] == 5
    assert "agent_01" in restored.llm_attempts_by_stage
    assert restored.llm_attempts_by_stage["agent_01"][0]["status"] == "submitted"
    assert "agent_01" in restored.llm_prompts_by_stage
    assert restored.llm_prompt_history[0]["stage_id"] == "agent_01"


def test_export_token_usage_json_contains_totals_and_by_stage() -> None:
    state = FrameworkState()
    state.record_llm_usage("agent_04", {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16})
    state.record_llm_attempt("agent_04", {"status": "submitted"})
    state.record_llm_attempt("agent_04", {"status": "completed"})
    state.record_llm_prompt("agent_04", {"system_prompt": "sys", "user_message": "user"})

    exported = export_token_usage_json(state)
    payload = json.loads(exported)

    assert "llm_usage_by_stage" in payload
    assert "llm_attempts_by_stage" in payload
    assert "llm_prompts_by_stage" in payload
    assert "llm_prompt_history" in payload
    assert "attempt_totals" in payload
    assert "totals" in payload
    assert payload["totals"]["total_tokens"] == 16
    assert payload["attempt_totals"]["completed"] == 1
    assert payload["llm_usage_by_stage"]["agent_04"][0]["prompt_tokens"] == 12
    assert payload["llm_prompt_history"][0]["stage_id"] == "agent_04"


def test_framework_state_attempt_totals() -> None:
    state = FrameworkState()
    state.record_llm_attempt("agent_01", {"status": "submitted"})
    state.record_llm_attempt("agent_01", {"status": "failed"})
    state.record_llm_attempt("agent_02", {"status": "submitted"})
    state.record_llm_attempt("agent_02", {"status": "completed"})

    totals = state.llm_attempt_totals()
    assert totals["submitted"] == 2
    assert totals["completed"] == 1
    assert totals["failed"] == 1
    assert totals["total"] == 4


def test_token_usage_screen_uses_fixed_width_stage_table_for_horizontal_scroll() -> None:
    text = Path("src/threat_modeler/ui/screens/token_usage.py").read_text(encoding="utf-8")
    assert "use_container_width=False" in text
    assert "width=1400" in text


def test_execution_registry_persists_and_restores_settings_override() -> None:
    # execution.py still reads settings from the run registry entry during sync.
    exec_text = Path("src/threat_modeler/ui/execution.py").read_text(encoding="utf-8")
    assert 'run_state.get("settings")' in exec_text
    assert 'st.session_state["settings_override"] = run_settings' in exec_text
    # The settings key is now written by backend/run_manager.py (not execution.py).
    manager_text = Path("src/threat_modeler/backend/run_manager.py").read_text(encoding="utf-8")
    assert '"settings": settings' in manager_text
