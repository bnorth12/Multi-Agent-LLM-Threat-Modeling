"""Regression tests for live-mode failover hard-stop behavior (D-S08-026)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.backend import run_manager
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState
from threat_modeler.ui import execution


@dataclass
class _StreamlitStub:
    """Minimal Streamlit stub for execution manager unit tests."""

    session_state: dict[str, Any] = field(default_factory=dict)
    query_params: dict[str, Any] = field(default_factory=dict)

    def error(self, _message: str) -> None:  # pragma: no cover - helper only
        return


class _FailingOrchestrator:
    """Orchestrator stub that simulates live-mode degradation failure."""

    def __init__(self, _settings: RuntimeSettings) -> None:
        self._settings = _settings

    def run_planned_stages(self, _state: FrameworkState) -> FrameworkState:
        raise RuntimeError(
            "Stage agent_01 (Input Normalizer) failed: RuntimeError: "
            "Live adapter required for agent_01 (Input Normalizer) but adapter is missing. "
            "Execution halted to prevent fallback to fixture mode."
        )


def _live_settings() -> RuntimeSettings:
    return RuntimeSettings(
        model=ModelSelection(
            provider="xai",
            model_name="grok-4",
            offline_only=False,
            endpoint_mode="chat_completions",
        ),
        pipeline=PipelineSettings(
            execution_mode="langgraph-compatible",
            enabled_stage_ids=("agent_01", "agent_02"),
            require_hitl_gates=False,
            stop_on_validation_error=False,
        ),
    )


def test_live_mode_missing_adapter_halts_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Live-intent runs must fail closed when no live adapter is available."""

    # Force the live adapter factory to degrade to None.
    monkeypatch.setattr("threat_modeler.agents._build_live_adapter", lambda _settings: None)

    settings = _live_settings()
    orchestrator = FrameworkOrchestrator(settings=settings, run_id="failover-halt-test")
    state = FrameworkState(raw_text="System: live failover halt test")

    with pytest.raises(RuntimeError) as exc_info:
        orchestrator.run_planned_stages(state)

    message = str(exc_info.value)
    assert "Stage agent_01" in message
    assert "Live adapter required for agent_01" in message
    assert "fallback to fixture mode" in message
    # Ensure execution halted before stage 2.
    assert not any(m.get("stage_id") == "agent_02" for m in state.messages)


def test_execution_manager_marks_failed_on_live_degradation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execution manager must publish FAILED status and fallback error details."""

    streamlit_stub = _StreamlitStub()
    monkeypatch.setattr(execution, "st", streamlit_stub)
    monkeypatch.setattr(run_manager, "FrameworkOrchestrator", _FailingOrchestrator)

    with run_manager._REGISTRY_LOCK:
        run_manager._RUN_REGISTRY.clear()
    streamlit_stub.session_state.clear()

    run_id = "run-live-failover-status"
    execution.start_pipeline_execution(
        run_id=run_id,
        initial_state=FrameworkState(raw_text="System: execution manager failover test"),
        settings=_live_settings(),
    )

    assert execution.wait_for_execution_complete(timeout=5)
    assert execution.get_execution_status() == execution.ExecutionStatus.FAILED.value

    error_text = execution.get_execution_error() or ""
    assert "Live adapter required" in error_text
    assert "fallback to fixture mode" in error_text

    execution.sync_execution_state_to_session()
    assert "pipeline_execution_error" in streamlit_stub.session_state
    assert "Stage agent_01" in streamlit_stub.session_state["pipeline_execution_error"]
