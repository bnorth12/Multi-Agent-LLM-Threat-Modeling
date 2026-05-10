"""Background execution manager for non-blocking pipeline runs.

Enables pipeline execution in background thread while allowing UI navigation.
Stores execution state in Streamlit session_state for cross-screen visibility.
"""

import threading
import time
from enum import Enum
from typing import Optional, Callable

import streamlit as st

from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState
from threat_modeler.config import RuntimeSettings
from threat_modeler.hitl import GatePausedError, GateRejectedError
from threat_modeler.backend.runtime_state import (
    clear_run_state,
    get_provider_display,
    get_last_settings,
    mark_run_started,
    mark_run_status,
    remember_settings,
)


class ExecutionStatus(Enum):
    """Pipeline execution status."""
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# Process-local run registry used to recover active runs across Streamlit reruns
# and browser reloads that reuse the same server process.
_RUN_REGISTRY: dict[str, dict] = {}
_REGISTRY_LOCK = threading.Lock()
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
        }
    return st.session_state["_execution_state"]


def sync_execution_state_to_session() -> None:
    """Sync execution state from process registry into session state.

    This keeps screen content coherent across page navigation and browser reloads.
    """
    session_state = _get_execution_state()

    # Attempt run restoration when session has no run_id yet.
    run_id = st.session_state.get("run_id")
    if not run_id:
        query_run_id = _read_query_run_id()
        if query_run_id:
            with _REGISTRY_LOCK:
                if query_run_id in _RUN_REGISTRY:
                    run_id = query_run_id
                    st.session_state["run_id"] = query_run_id

    if not run_id:
        return

    with _REGISTRY_LOCK:
        run_state = _RUN_REGISTRY.get(run_id)

    if not run_state:
        return

    # Mirror runtime status into session-visible execution state.
    for key in ("status", "run_id", "start_time", "end_time", "error", "pause_gate"):
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
        live_state = run_state.get("live_state")
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
    """Start pipeline execution in background thread.

    Args:
        run_id: Unique identifier for this run
        initial_state: Initial FrameworkState
        settings: RuntimeSettings for the run
        on_complete: Optional callback when execution completes
    """
    exec_state = _get_execution_state()

    # Check if already running
    if is_execution_active():
        st.error(f"🔒 A run is already executing: {exec_state['run_id']}")
        return

    # Mark as queued
    start_time = time.time()
    exec_state["status"] = ExecutionStatus.QUEUED.value
    exec_state["run_id"] = run_id
    exec_state["start_time"] = start_time
    exec_state["end_time"] = None
    exec_state["error"] = None
    exec_state["pause_gate"] = None
    exec_state["result_state"] = None

    with _REGISTRY_LOCK:
        _RUN_REGISTRY[run_id] = {
            "status": ExecutionStatus.QUEUED.value,
            "run_id": run_id,
            "start_time": start_time,
            "end_time": None,
            "error": None,
            "result_state": None,
            "live_state": initial_state,
            "pause_gate": None,
            "settings": settings,
        }

    if isinstance(settings, RuntimeSettings):
        mark_run_started(run_id, settings)

    # Keep run_id in URL for recovery on browser reload.
    st.session_state["run_id"] = run_id
    _write_query_run_id(run_id)

    def _execute():
        """Execution function to run in background thread."""
        try:
            exec_state["status"] = ExecutionStatus.RUNNING.value
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.RUNNING.value
            mark_run_status(ExecutionStatus.RUNNING.value)

            # Expose the mutable state object so the dashboard can read live progress.
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["live_state"] = initial_state

            # Execute pipeline
            orchestrator = FrameworkOrchestrator(settings)
            final_state = orchestrator.run_langgraph_compatible(initial_state)
            setattr(final_state, "next_stage_id", None)

            # Success
            exec_state["status"] = ExecutionStatus.COMPLETED.value
            exec_state["result_state"] = final_state
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.COMPLETED.value
                    _RUN_REGISTRY[run_id]["result_state"] = final_state
            mark_run_status(ExecutionStatus.COMPLETED.value)

        except GatePausedError as e:
            # Expected: pipeline paused for human review.
            # Persist the gate checkpoint so the UI can display gate state without
            # requiring the orchestrator instance (which won't survive the thread boundary).
            gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
            initial_state.hitl_gate_checkpoint = gate_checkpoint

            exec_state["status"] = ExecutionStatus.PAUSED.value
            exec_state["pause_gate"] = e.gate_record.gate_id
            exec_state["result_state"] = initial_state
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.PAUSED.value
                    _RUN_REGISTRY[run_id]["pause_gate"] = e.gate_record.gate_id
                    _RUN_REGISTRY[run_id]["result_state"] = initial_state
            mark_run_status(ExecutionStatus.PAUSED.value, pause_gate=e.gate_record.gate_id)

        except GateRejectedError as e:
            # Gate rejected the output
            exec_state["status"] = ExecutionStatus.FAILED.value
            exec_state["error"] = f"Gate rejected at {e.gate_record.gate_id}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = f"Gate rejected at {e.gate_record.gate_id}"
                    _RUN_REGISTRY[run_id]["result_state"] = initial_state
            mark_run_status(ExecutionStatus.FAILED.value, error=f"Gate rejected at {e.gate_record.gate_id}")

        except Exception as e:
            # Unexpected error
            exec_state["status"] = ExecutionStatus.FAILED.value
            exec_state["error"] = f"{type(e).__name__}: {str(e)}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = f"{type(e).__name__}: {str(e)}"
                    _RUN_REGISTRY[run_id]["result_state"] = initial_state
            mark_run_status(ExecutionStatus.FAILED.value, error=f"{type(e).__name__}: {str(e)}")

        finally:
            end_time = time.time()
            exec_state["end_time"] = end_time
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["end_time"] = end_time
            if on_complete:
                on_complete()
            if exec_state["status"] == ExecutionStatus.IDLE.value:
                clear_run_state()

    # Start background thread
    thread = threading.Thread(target=_execute, daemon=True)
    exec_state["thread"] = thread
    thread.start()


def resume_pipeline_execution(
    run_id: str,
    pipeline_state: FrameworkState,
    settings: RuntimeSettings,
    gate_id: str,
) -> None:
    """Resume a paused pipeline from a gate checkpoint in a background thread.

    Mirrors start_pipeline_execution but resumes via orchestrator.resume_from_checkpoint().
    Updates _RUN_REGISTRY status so the dashboard reflects RUNNING while stages execute.

    Args:
        run_id: Existing run identifier (must already exist in _RUN_REGISTRY)
        pipeline_state: FrameworkState captured at the pause point
        settings: RuntimeSettings for the run
        gate_id: Gate ID to resume from
    """
    exec_state = _get_execution_state()

    # Prevent duplicate resume attempts while a background thread is already active.
    if exec_state.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        return

    paused_gate = exec_state.get("pause_gate")
    if paused_gate and paused_gate != gate_id:
        # Ignore stale resume clicks that do not match the active pause checkpoint.
        return

    # Re-mark as running in both the session state and the registry.
    exec_state["status"] = ExecutionStatus.RUNNING.value
    exec_state["end_time"] = None
    exec_state["pause_gate"] = None
    exec_state["error"] = None
    exec_state["result_state"] = None

    with _REGISTRY_LOCK:
        if run_id in _RUN_REGISTRY:
            _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.RUNNING.value
            _RUN_REGISTRY[run_id]["end_time"] = None
            _RUN_REGISTRY[run_id]["pause_gate"] = None
            _RUN_REGISTRY[run_id]["error"] = None
            _RUN_REGISTRY[run_id]["result_state"] = None
            _RUN_REGISTRY[run_id]["live_state"] = pipeline_state
            _RUN_REGISTRY[run_id]["settings"] = settings

    remember_settings(settings)

    def _execute():
        try:
            orchestrator = FrameworkOrchestrator(settings, run_id=run_id)
            # Restore HITL checkpoint so the orchestrator knows which gates already passed.
            checkpoint = getattr(pipeline_state, "hitl_gate_checkpoint", None)
            if isinstance(checkpoint, dict) and checkpoint:
                orchestrator.hitl_service.restore_checkpoint_state(checkpoint)

            final_state = orchestrator.resume_from_checkpoint(pipeline_state, gate_id)
            setattr(final_state, "next_stage_id", None)

            exec_state["status"] = ExecutionStatus.COMPLETED.value
            exec_state["result_state"] = final_state
            exec_state["error"] = None
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.COMPLETED.value
                    _RUN_REGISTRY[run_id]["error"] = None
                    _RUN_REGISTRY[run_id]["result_state"] = final_state
            mark_run_status(ExecutionStatus.COMPLETED.value)

        except GatePausedError as e:
            # Persist gate checkpoint so the UI can display gate state without the orchestrator instance.
            gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
            pipeline_state.hitl_gate_checkpoint = gate_checkpoint

            exec_state["status"] = ExecutionStatus.PAUSED.value
            exec_state["pause_gate"] = e.gate_record.gate_id
            exec_state["result_state"] = pipeline_state
            exec_state["error"] = None
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.PAUSED.value
                    _RUN_REGISTRY[run_id]["pause_gate"] = e.gate_record.gate_id
                    _RUN_REGISTRY[run_id]["error"] = None
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            mark_run_status(ExecutionStatus.PAUSED.value, pause_gate=e.gate_record.gate_id)

        except GateRejectedError as e:
            exec_state["status"] = ExecutionStatus.FAILED.value
            exec_state["error"] = f"Gate rejected at {e.gate_record.gate_id}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = f"Gate rejected at {e.gate_record.gate_id}"
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            mark_run_status(ExecutionStatus.FAILED.value, error=f"Gate rejected at {e.gate_record.gate_id}")

        except Exception as e:
            exec_state["status"] = ExecutionStatus.FAILED.value
            exec_state["error"] = f"{type(e).__name__}: {str(e)}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = f"{type(e).__name__}: {str(e)}"
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            mark_run_status(ExecutionStatus.FAILED.value, error=f"{type(e).__name__}: {str(e)}")

        finally:
            end_time = time.time()
            exec_state["end_time"] = end_time
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["end_time"] = end_time

    thread = threading.Thread(target=_execute, daemon=True)
    exec_state["thread"] = thread
    thread.start()


def cancel_execution() -> bool:
    """Request cancellation of active execution.

    Note: Graceful cancellation is not currently supported.
    This marks the run as failed.

    Returns:
        True if cancellation was successful
    """
    state = _get_execution_state()
    if not is_execution_active():
        return False

    state["status"] = ExecutionStatus.FAILED.value
    state["error"] = "Execution cancelled by user"
    state["end_time"] = time.time()
    return True


def wait_for_execution_complete(timeout: float = 300) -> bool:
    """Wait for active execution to complete (blocking).

    Args:
        timeout: Maximum seconds to wait

    Returns:
        True if execution completed, False if timeout
    """
    start = time.time()
    state = _get_execution_state()

    while is_execution_active():
        if time.time() - start > timeout:
            return False
        time.sleep(0.1)

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

    st.metric(
        "Execution Status",
        f"{badge} {status.upper()}",
        f"⏱️ {elapsed:.0f}s"
    )

    if run_id:
        st.caption(f"Run: {run_id[:8]}…")


def block_interaction_during_execution(widget_name: str = "form") -> bool:
    """Check if UI interaction should be blocked during active execution.

    Returns:
        True if execution is active (widget should be disabled), False otherwise
    """
    return is_execution_active()
