"""Streamlit UI adapter for non-blocking pipeline execution.

Owns the session-state synchronisation and URL-param bookkeeping for the
active run.  All pipeline execution logic lives in
``threat_modeler.backend.run_manager`` (no Streamlit dependency) — this
module simply delegates to it and keeps the Streamlit session coherent.
"""

import time
from typing import Optional, Callable

import streamlit as st

from threat_modeler.state import FrameworkState
from threat_modeler.config import RuntimeSettings
from threat_modeler.backend import run_manager as _run_manager
from threat_modeler.backend.run_manager import ExecutionStatus
from threat_modeler.backend.runtime_state import (
    get_provider_display,
    get_last_settings,
    remember_settings,
)

_STATUS_POLL_INTERVAL = 3


def _normalize_query_value(value: object) -> Optional[str]:
    """Normalize Streamlit query param values to a single string."""
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    text = str(value).strip()
    return text or None


def _read_query_run_id() -> Optional[str]:
    """Read run_id from query params if present."""
    try:
        return _normalize_query_value(st.query_params.get("run_id"))
    except Exception:
        return None


def _write_query_run_id(run_id: str) -> None:
    """Write run_id into query params for browser-reload restoration."""
    try:
        st.query_params["run_id"] = run_id
    except Exception:
        # Query param APIs can be unavailable depending on runtime context.
        pass


def _get_execution_state():
    """Get or initialize execution state from session."""
    if "_execution_state" not in st.session_state:
        st.session_state["_execution_state"] = {
            "status": ExecutionStatus.IDLE.value,
            "run_id": None,
            "thread": None,
            "start_time": None,
            "end_time": None,
            "error": None,
            "result_state": None,
            "pause_gate": None,
            "last_heartbeat_time": None,
            "heartbeat_timeout_seconds": None,
        }
    return st.session_state["_execution_state"]


def sync_execution_state_to_session() -> None:
    """Sync execution state from the backend run manager into session state.

    This keeps screen content coherent across page navigation and browser
    reloads.  The authoritative state is ``backend.run_manager``; session
    state is a read cache for Streamlit screens.
    """
    session_state = _get_execution_state()

    # Attempt run restoration when session has no run_id yet.
    run_id = st.session_state.get("run_id")
    if not run_id:
        query_run_id = _read_query_run_id()
        if query_run_id and _run_manager.get_run_status(query_run_id) is not None:
            run_id = query_run_id
            st.session_state["run_id"] = query_run_id

    if not run_id:
        return

    run_state = _run_manager.get_run_status(run_id)
    if not run_state:
        return

    # Mirror runtime status into session-visible execution state.
    for key in (
        "status",
        "run_id",
        "start_time",
        "end_time",
        "error",
        "pause_gate",
        "last_heartbeat_time",
        "heartbeat_timeout_seconds",
    ):
        session_state[key] = run_state.get(key)

    # Restore settings used for this run so resumed actions do not fall back
    # to fixture defaults after reload/navigation.
    run_settings = run_state.get("settings")
    if isinstance(run_settings, RuntimeSettings):
        st.session_state["settings_override"] = run_settings
        remember_settings(run_settings)
        st.session_state["config_selected_provider"] = run_settings.model.provider
        st.session_state["model_connection_valid"] = True
    elif st.session_state.get("settings_override") is None:
        last_settings = get_last_settings()
        if isinstance(last_settings, RuntimeSettings):
            st.session_state["settings_override"] = last_settings

    # Keep the run addressable after browser reload.
    _write_query_run_id(run_id)

    status = run_state.get("status")
    result_state = run_state.get("result_state")
    live_state = run_state.get("live_state")

    # While active, prefer live_state so progress and gate state are not pinned
    # to a previous pause checkpoint retained in result_state.
    if status in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        effective_state = live_state if live_state is not None else result_state
    else:
        effective_state = result_state if result_state is not None else live_state
    if effective_state is not None:
        st.session_state["pipeline_state"] = effective_state
    # Sync gate checkpoint from whichever state object has it.
    state_candidates = (live_state, result_state) if status in (
        ExecutionStatus.RUNNING.value,
        ExecutionStatus.QUEUED.value,
    ) else (result_state, live_state)
    for _state_candidate in state_candidates:
        if _state_candidate is None:
            continue
        checkpoint = getattr(_state_candidate, "hitl_gate_checkpoint", None)
        if isinstance(checkpoint, dict) and checkpoint.get("gates"):
            st.session_state["gate_states"] = checkpoint.get("gates", {})
            break
    if status == ExecutionStatus.RUNNING.value:
        stage_id = getattr(live_state, "next_stage_id", None)
        if stage_id:
            st.session_state["pipeline_execution_summary"] = f"Running stage {stage_id} ..."
        else:
            st.session_state["pipeline_execution_summary"] = "Pipeline execution is running ..."
        st.session_state.pop("pipeline_execution_error", None)
    elif status == ExecutionStatus.FAILED.value and run_state.get("error"):
        st.session_state["pipeline_execution_error"] = str(run_state["error"])
    elif status == ExecutionStatus.PAUSED.value and run_state.get("pause_gate"):
        st.session_state["pipeline_execution_summary"] = (
            f"Pipeline paused at {run_state['pause_gate']} and is awaiting review."
        )
        st.session_state.pop("pipeline_execution_error", None)
    elif status == ExecutionStatus.COMPLETED.value:
        st.session_state["pipeline_execution_summary"] = "Pipeline completed successfully."
        st.session_state.pop("pipeline_execution_error", None)
    else:
        st.session_state.pop("pipeline_execution_summary", None)
        st.session_state.pop("pipeline_execution_error", None)


def is_execution_active() -> bool:
    """Check if pipeline execution is currently active."""
    sync_execution_state_to_session()
    state = _get_execution_state()
    return state["status"] in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value)


def get_execution_status() -> str:
    """Get current execution status."""
    sync_execution_state_to_session()
    return _get_execution_state()["status"]


def get_active_run_id() -> Optional[str]:
    """Get the currently executing run ID."""
    sync_execution_state_to_session()
    state = _get_execution_state()
    return state.get("run_id")


def get_execution_error() -> Optional[str]:
    """Get last execution error if any."""
    sync_execution_state_to_session()
    return _get_execution_state().get("error")


def get_paused_at_gate() -> Optional[str]:
    """Get gate ID if execution is paused."""
    sync_execution_state_to_session()
    state = _get_execution_state()
    if state["status"] == ExecutionStatus.PAUSED.value:
        return state["pause_gate"]
    return None


def start_pipeline_execution(
    run_id: str,
    initial_state: FrameworkState,
    settings: RuntimeSettings,
    on_complete: Optional[Callable] = None,
) -> None:
    """Start pipeline execution in a background thread.

    Delegates all execution logic to ``backend.run_manager.submit_run()``.
    This function handles only Streamlit session-state bookkeeping.

    Args:
        run_id:        Unique identifier for this run.
        initial_state: Initial FrameworkState populated with parsed inputs.
        settings:      RuntimeSettings for the run.
        on_complete:   Optional zero-argument callback when execution completes.
    """
    if is_execution_active():
        exec_state = _get_execution_state()
        st.error(f"🔒 A run is already executing: {exec_state['run_id']}")
        return

    # Anchor run_id in session and URL before the background thread starts.
    st.session_state["run_id"] = run_id
    _write_query_run_id(run_id)

    # Delegate all thread / orchestrator logic to the Streamlit-free backend.
    _run_manager.submit_run(run_id, initial_state, settings, on_complete=on_complete)


def resume_pipeline_execution(
    run_id: str,
    pipeline_state: FrameworkState,
    settings: RuntimeSettings,
    gate_id: str,
) -> None:
    """Resume a paused pipeline from a gate checkpoint in a background thread.

    Delegates all execution logic to ``backend.run_manager.resume_run()``.

    Args:
        run_id:         Existing run identifier.
        pipeline_state: FrameworkState captured at the pause point.
        settings:       RuntimeSettings for the run.
        gate_id:        Gate ID that triggered the pause; positions resume point.
    """
    exec_state = _get_execution_state()

    # Prevent duplicate resume attempts while a background thread is already active.
    if exec_state.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        return

    paused_gate = exec_state.get("pause_gate")
    if paused_gate and paused_gate != gate_id:
        # Ignore stale resume clicks that do not match the active pause checkpoint.
        return

    # Delegate all thread / orchestrator logic to the Streamlit-free backend.
    _run_manager.resume_run(run_id, gate_id, pipeline_state, settings)


def cancel_execution() -> bool:
    """Request cancellation of the active execution.

    Delegates to ``backend.run_manager.cancel_run()``.

    Returns:
        True if a run was active and has been marked as failed.
    """
    run_id = st.session_state.get("run_id")
    if run_id:
        return _run_manager.cancel_run(run_id)
    return False


def wait_for_execution_complete(timeout: float = 300) -> bool:
    """Block until the active execution leaves its active state or *timeout* expires.

    Returns:
        True if execution completed, False if timeout was reached.
    """
    run_id = st.session_state.get("run_id")
    if run_id:
        return _run_manager.wait_for_run(run_id, timeout=timeout)
    return True


def get_execution_elapsed_seconds() -> float:
    """Get elapsed time for active execution in seconds."""
    sync_execution_state_to_session()
    state = _get_execution_state()
    start = state.get("start_time")
    if not start:
        return 0.0

    if state.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        end = time.time()
    else:
        end = state.get("end_time") or time.time()
    return end - start


def get_heartbeat_age_seconds() -> float | None:
    """Return seconds since last run heartbeat, or None if unavailable."""
    sync_execution_state_to_session()
    state = _get_execution_state()
    heartbeat_ts = state.get("last_heartbeat_time")
    if not heartbeat_ts:
        return None
    try:
        return max(0.0, time.time() - float(heartbeat_ts))
    except (TypeError, ValueError):
        return None


def get_current_provider_status() -> tuple[str, str]:
    """Get current provider and detect if using live LLM or local fixture.

    Returns:
        Tuple of (provider_label, status_indicator)
        Examples: ("xAI/Grok", "✅ LIVE"), ("Local/Fixture", "⚫ LOCAL")
    """
    provider_label, provider_status, _ = get_provider_display()
    return provider_label, provider_status


def verify_provider_not_fallen_back() -> bool:
    """Verify that provider is still configured as live (not fallen back to fixture).

    Returns:
        True if using live LLM, False if using fixture/offline mode
    """
    screen_name = st.session_state.get("nav_selection", "Unknown")

    provider_label, provider_status, is_live = get_provider_display()
    if is_live:
        print(f"[PROVIDER OK] Screen: {screen_name}, Using live provider: {provider_label}")
    else:
        print(
            f"[PROVIDER FALLBACK] Screen: {screen_name}, "
            f"Provider state: {provider_label}, Status: {provider_status}"
        )
    return is_live


@st.fragment(run_every=_STATUS_POLL_INTERVAL)
def render_execution_status_badge() -> None:
    """Render execution status badge and provider status for sidebar."""
    sync_execution_state_to_session()
    status = get_execution_status()
    run_id = get_active_run_id()

    # Always show provider status
    provider_label, provider_status = get_current_provider_status()
    st.metric(
        "LLM Provider",
        provider_label,
        provider_status,
    )

    if status == ExecutionStatus.IDLE.value:
        return  # Don't show execution status when idle

    # Color map for status
    color_map = {
        ExecutionStatus.QUEUED.value: "🟡",
        ExecutionStatus.RUNNING.value: "🔵",
        ExecutionStatus.PAUSED.value: "🟠",
        ExecutionStatus.COMPLETED.value: "🟢",
        ExecutionStatus.FAILED.value: "🔴",
    }

    badge = color_map.get(status, "⚪")
    elapsed = get_execution_elapsed_seconds()
    heartbeat_age = get_heartbeat_age_seconds()
    heartbeat_timeout = _get_execution_state().get("heartbeat_timeout_seconds")

    st.metric(
        "Execution Status",
        f"{badge} {status.upper()}",
        f"⏱️ {elapsed:.0f}s"
    )

    if run_id:
        st.caption(f"Run: {run_id[:8]}…")
    if heartbeat_age is not None and status in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        timeout_txt = ""
        if heartbeat_timeout:
            try:
                timeout_txt = f" / timeout {float(heartbeat_timeout):.0f}s"
            except (TypeError, ValueError):
                timeout_txt = ""
        st.caption(f"Heartbeat age: {heartbeat_age:.1f}s{timeout_txt}")


def block_interaction_during_execution(widget_name: str = "form") -> bool:
    """Check if UI interaction should be blocked during active execution.

    Returns:
        True if execution is active (widget should be disabled), False otherwise
    """
    return is_execution_active()
