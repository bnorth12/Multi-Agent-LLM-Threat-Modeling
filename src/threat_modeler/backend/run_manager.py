"""Backend pipeline execution manager.

Pure Python — no Streamlit dependency.  Provides ``submit_run()``,
``resume_run()``, and supporting read accessors so the Streamlit UI adapter
(``ui/execution.py``) and any future web interface can drive the pipeline
without importing Streamlit.

Run metadata (status, timing, pause-gate, error, settings) is mirrored to a
JSON checkpoint file so that browser-reload recovery survives Streamlit
reruns.  The ``FrameworkState`` objects themselves are kept in-memory only;
use the snapshot helpers in ``ui/runtime_io`` when persistent state snapshots
are needed.
"""

from __future__ import annotations

import json
import os
import threading
import time
import logging
from threat_modeler.llm.llm_provider_error import LlmProviderError
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from threat_modeler.config import RuntimeSettings
from threat_modeler.hitl import GatePausedError, GateRejectedError
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState
from threat_modeler.backend.runtime_state import (
    clear_run_state,
    get_last_settings,
    mark_run_started,
    mark_run_status,
    remember_settings,
)

# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class ExecutionStatus(Enum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    PROVIDER_THROTTLED = "provider_throttled"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Process-level registry
# ---------------------------------------------------------------------------

_RUN_REGISTRY: dict[str, dict[str, Any]] = {}
_REGISTRY_LOCK = threading.Lock()

# JSON checkpoint — persists run metadata across process restarts.
_CHECKPOINT_FILE = Path.home() / ".multi_agent_threat_modeler_runs.json"

# Heartbeat/watchdog defaults (seconds). Override with environment variables.
_HEARTBEAT_INTERVAL_SECONDS_DEFAULT = 3.0
_HEARTBEAT_TIMEOUT_SECONDS_DEFAULT = 10.0  # Tuned from 35s based on observed max heartbeat age ~2s


def _coerce_positive_float(value: object, default: float) -> float:
    """Return a positive float parsed from *value* or *default* on failure."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _heartbeat_interval_seconds() -> float:
    return _coerce_positive_float(
        os.environ.get("THREAT_MODELER_HEARTBEAT_INTERVAL_SECONDS"),
        _HEARTBEAT_INTERVAL_SECONDS_DEFAULT,
    )


def _heartbeat_timeout_seconds() -> float:
    return _coerce_positive_float(
        os.environ.get("THREAT_MODELER_HEARTBEAT_TIMEOUT_SECONDS"),
        _HEARTBEAT_TIMEOUT_SECONDS_DEFAULT,
    )


# ---------------------------------------------------------------------------
# JSON persistence helpers
# ---------------------------------------------------------------------------

def _serialize_settings(settings: RuntimeSettings | None) -> dict | None:
    if settings is None:
        return None
    try:
        return asdict(settings)
    except Exception:
        return None


def _persist_run_metadata(run_id: str) -> None:
    """Write the metadata-only fields of *run_id* to the checkpoint file."""
    with _REGISTRY_LOCK:
        entry = _RUN_REGISTRY.get(run_id)
    if not entry:
        return
    record = {
        "run_id": run_id,
        "status": entry.get("status", ExecutionStatus.IDLE.value),
        "start_time": entry.get("start_time"),
        "end_time": entry.get("end_time"),
        "pause_gate": entry.get("pause_gate"),
        "error": entry.get("error"),
        "last_heartbeat_time": entry.get("last_heartbeat_time"),
        "heartbeat_timeout_seconds": entry.get("heartbeat_timeout_seconds"),
        "settings": _serialize_settings(entry.get("settings")),
    }
    try:
        existing: dict = {}
        if _CHECKPOINT_FILE.exists():
            try:
                existing = json.loads(_CHECKPOINT_FILE.read_text(encoding="utf-8"))
            except Exception:
                existing = {}
        if not isinstance(existing, dict):
            existing = {}
        existing[run_id] = record
        _CHECKPOINT_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except Exception:
        pass


def _restore_metadata_from_checkpoint() -> None:
    """Populate _RUN_REGISTRY with metadata from the on-disk checkpoint."""
    if not _CHECKPOINT_FILE.exists():
        return
    try:
        payload = json.loads(_CHECKPOINT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    with _REGISTRY_LOCK:
        for run_id, record in payload.items():
            if run_id not in _RUN_REGISTRY and isinstance(record, dict):
                # Restore metadata only; FrameworkState objects are not stored in JSON.
                _RUN_REGISTRY[run_id] = {
                    "status": record.get("status", ExecutionStatus.IDLE.value),
                    "run_id": run_id,
                    "start_time": record.get("start_time"),
                    "end_time": record.get("end_time"),
                    "pause_gate": record.get("pause_gate"),
                    "error": record.get("error"),
                    "last_heartbeat_time": record.get("last_heartbeat_time"),
                    "heartbeat_timeout_seconds": record.get(
                        "heartbeat_timeout_seconds",
                        _heartbeat_timeout_seconds(),
                    ),
                    "result_state": None,
                    "live_state": None,
                    "settings": None,  # settings are re-hydrated from runtime_state on next run
                }


_restore_metadata_from_checkpoint()


# ---------------------------------------------------------------------------
# Public read accessors
# ---------------------------------------------------------------------------

def get_run_status(run_id: str) -> Optional[dict[str, Any]]:
    """Return the full registry entry for *run_id*, or ``None`` if unknown."""
    with _REGISTRY_LOCK:
        return dict(_RUN_REGISTRY[run_id]) if run_id in _RUN_REGISTRY else None


def get_all_run_ids() -> list[str]:
    """Return all run IDs currently known to the registry."""
    with _REGISTRY_LOCK:
        return list(_RUN_REGISTRY.keys())


def is_run_active(run_id: str) -> bool:
    """Return True if *run_id* is currently queued or running."""
    with _REGISTRY_LOCK:
        entry = _RUN_REGISTRY.get(run_id)
    if not entry:
        return False
    return entry.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value)


def any_run_active() -> bool:
    """Return True if any run is currently queued or running."""
    with _REGISTRY_LOCK:
        for entry in _RUN_REGISTRY.values():
            if entry.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
                return True
    return False


def _set_heartbeat(run_id: str, ts: float | None = None) -> None:
    """Record a heartbeat timestamp for *run_id*."""
    heartbeat_time = ts if ts is not None else time.time()
    with _REGISTRY_LOCK:
        if run_id in _RUN_REGISTRY:
            _RUN_REGISTRY[run_id]["last_heartbeat_time"] = heartbeat_time


def _run_heartbeat_ticker(run_id: str, stop_event: threading.Event) -> None:
    """Emit periodic heartbeats while a run is queued/running."""
    interval = _heartbeat_interval_seconds()
    while not stop_event.wait(interval):
        with _REGISTRY_LOCK:
            entry = _RUN_REGISTRY.get(run_id)
            status = entry.get("status") if entry else None
        if status not in (ExecutionStatus.QUEUED.value, ExecutionStatus.RUNNING.value):
            break
        _set_heartbeat(run_id)


def _run_heartbeat_watchdog(run_id: str, stop_event: threading.Event) -> None:
    """Fail the run if heartbeats stop for longer than timeout."""
    while not stop_event.wait(1.0):
        with _REGISTRY_LOCK:
            entry = _RUN_REGISTRY.get(run_id)
            if not entry:
                break
            status = entry.get("status")
            last_heartbeat_time = float(entry.get("last_heartbeat_time") or 0.0)
            heartbeat_timeout_seconds = _coerce_positive_float(
                entry.get("heartbeat_timeout_seconds"),
                _heartbeat_timeout_seconds(),
            )

        if status not in (ExecutionStatus.QUEUED.value, ExecutionStatus.RUNNING.value):
            break
        if last_heartbeat_time <= 0:
            continue

        stale_for = time.time() - last_heartbeat_time
        if stale_for <= heartbeat_timeout_seconds:
            continue

        error_msg = (
            "Heartbeat timeout: no run heartbeat for "
            f"{stale_for:.1f}s (threshold={heartbeat_timeout_seconds:.1f}s)."
        )
        with _REGISTRY_LOCK:
            current = _RUN_REGISTRY.get(run_id)
            if current and current.get("status") in (
                ExecutionStatus.QUEUED.value,
                ExecutionStatus.RUNNING.value,
            ):
                current["status"] = ExecutionStatus.FAILED.value
                current["error"] = error_msg
                current["end_time"] = time.time()
        mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)
        _persist_run_metadata(run_id)
        break


# ---------------------------------------------------------------------------
# Submit (start a new run)
# ---------------------------------------------------------------------------

def submit_run(
    run_id: str,
    initial_state: FrameworkState,
    settings: RuntimeSettings,
    on_complete: Optional[Callable] = None,
) -> None:
    """Start pipeline execution in a background thread.

    This function has no Streamlit dependency and can be called from any
    context — including from ``ui/execution.py``, a REST endpoint, or a CLI
    entry point.

    Args:
        run_id:        Unique identifier for this run.
        initial_state: Initial ``FrameworkState`` populated with parsed inputs.
        settings:      ``RuntimeSettings`` selecting the LLM provider and pipeline.
        on_complete:   Optional zero-argument callback invoked when the thread exits.
    """
    start_time = time.time()
    heartbeat_timeout_seconds = _heartbeat_timeout_seconds()

    with _REGISTRY_LOCK:
        _RUN_REGISTRY[run_id] = {
            "status": ExecutionStatus.QUEUED.value,
            "run_id": run_id,
            "start_time": start_time,
            "end_time": None,
            "error": None,
            "last_heartbeat_time": start_time,
            "heartbeat_timeout_seconds": heartbeat_timeout_seconds,
            "result_state": None,
            "live_state": initial_state,
            "pause_gate": None,
            "settings": settings,
        }

    _persist_run_metadata(run_id)

    if isinstance(settings, RuntimeSettings):
        mark_run_started(run_id, settings)

    def _execute() -> None:
        logger = logging.getLogger("threat_modeler.backend.run_manager")
        stop_event = threading.Event()
        heartbeat_thread = threading.Thread(
            target=_run_heartbeat_ticker,
            args=(run_id, stop_event),
            daemon=True,
            name=f"heartbeat-{run_id[:8]}",
        )
        watchdog_thread = threading.Thread(
            target=_run_heartbeat_watchdog,
            args=(run_id, stop_event),
            daemon=True,
            name=f"watchdog-{run_id[:8]}",
        )
        heartbeat_thread.start()
        watchdog_thread.start()
        retry_count = 0
        max_retries = 3
        while True:
            try:
                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY:
                        _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.RUNNING.value
                mark_run_status(ExecutionStatus.RUNNING.value)
                _set_heartbeat(run_id)

                # Keep live_state reference visible for dashboard progress reads.
                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY:
                        _RUN_REGISTRY[run_id]["live_state"] = initial_state

                orchestrator = FrameworkOrchestrator(settings)
                final_state = orchestrator.run_planned_stages(initial_state)
                setattr(final_state, "next_stage_id", None)

                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                        ExecutionStatus.QUEUED.value,
                        ExecutionStatus.RUNNING.value,
                    ):
                        _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.COMPLETED.value
                        _RUN_REGISTRY[run_id]["result_state"] = final_state
                with _REGISTRY_LOCK:
                    run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
                if run_status == ExecutionStatus.COMPLETED.value:
                    mark_run_status(ExecutionStatus.COMPLETED.value)
                break

            except LlmProviderError as exc:
                if exc.retryable and retry_count < max_retries:
                    wait_seconds = exc.wait_seconds or 120
                    logger.warning(f"LLM provider throttled (rate limit). Pausing for {wait_seconds}s before retry ({retry_count+1}/{max_retries})")
                    with _REGISTRY_LOCK:
                        if run_id in _RUN_REGISTRY:
                            _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.PROVIDER_THROTTLED.value
                            _RUN_REGISTRY[run_id]["error"] = str(exc)
                    mark_run_status(ExecutionStatus.PROVIDER_THROTTLED.value, error=str(exc))
                    _persist_run_metadata(run_id)
                    time.sleep(wait_seconds)
                    retry_count += 1
                    continue
                else:
                    # Include all LlmProviderError details for telemetry
                    error_details = {
                        "type": "LlmProviderError",
                        "message": str(exc),
                        "code": getattr(exc, "code", None),
                        "retryable": getattr(exc, "retryable", False),
                        "wait_seconds": getattr(exc, "wait_seconds", None),
                        "retries": retry_count,
                    }
                    error_msg = f"LlmProviderError: {error_details}"
                    with _REGISTRY_LOCK:
                        if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                            ExecutionStatus.QUEUED.value,
                            ExecutionStatus.RUNNING.value,
                            ExecutionStatus.PROVIDER_THROTTLED.value,
                        ):
                            _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                            _RUN_REGISTRY[run_id]["error"] = error_msg
                            _RUN_REGISTRY[run_id]["result_state"] = initial_state
                    with _REGISTRY_LOCK:
                        run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
                    if run_status == ExecutionStatus.FAILED.value:
                        mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)
                    break

            except GatePausedError as exc:
                gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
                initial_state.hitl_gate_checkpoint = gate_checkpoint
                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                        ExecutionStatus.QUEUED.value,
                        ExecutionStatus.RUNNING.value,
                    ):
                        _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.PAUSED.value
                        _RUN_REGISTRY[run_id]["pause_gate"] = exc.gate_record.gate_id
                        _RUN_REGISTRY[run_id]["result_state"] = initial_state
                with _REGISTRY_LOCK:
                    run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
                if run_status == ExecutionStatus.PAUSED.value:
                    mark_run_status(ExecutionStatus.PAUSED.value, pause_gate=exc.gate_record.gate_id)
                break

            except GateRejectedError as exc:
                error_msg = f"Gate rejected at {exc.gate_record.gate_id}"
                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                        ExecutionStatus.QUEUED.value,
                        ExecutionStatus.RUNNING.value,
                    ):
                        _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                        _RUN_REGISTRY[run_id]["error"] = error_msg
                        _RUN_REGISTRY[run_id]["result_state"] = initial_state
                with _REGISTRY_LOCK:
                    run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
                if run_status == ExecutionStatus.FAILED.value:
                    mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)
                break

            except Exception as exc:
                error_msg = f"{type(exc).__name__}: {exc}"
                with _REGISTRY_LOCK:
                    if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                        ExecutionStatus.QUEUED.value,
                        ExecutionStatus.RUNNING.value,
                    ):
                        _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                        _RUN_REGISTRY[run_id]["error"] = error_msg
                        _RUN_REGISTRY[run_id]["result_state"] = initial_state
                with _REGISTRY_LOCK:
                    run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
                if run_status == ExecutionStatus.FAILED.value:
                    mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)
                break

        # Always finalize the run record once the execution loop exits.
        stop_event.set()
        end_time = time.time()
        with _REGISTRY_LOCK:
            if run_id in _RUN_REGISTRY:
                _RUN_REGISTRY[run_id]["end_time"] = end_time
        _persist_run_metadata(run_id)
        if on_complete:
            on_complete()

    thread = threading.Thread(target=_execute, daemon=True, name=f"run-{run_id[:8]}")
    with _REGISTRY_LOCK:
        _RUN_REGISTRY[run_id]["thread"] = thread
    thread.start()


# ---------------------------------------------------------------------------
# Resume (continue from a HITL gate pause)
# ---------------------------------------------------------------------------

def resume_run(
    run_id: str,
    gate_id: str,
    pipeline_state: FrameworkState,
    settings: RuntimeSettings,
) -> None:
    """Resume a paused run from a gate checkpoint in a background thread.

    Args:
        run_id:         Existing run identifier (must be in registry).
        gate_id:        Gate ID that triggered the pause; used to position resume.
        pipeline_state: ``FrameworkState`` captured at the pause point.
        settings:       ``RuntimeSettings`` for the resumed execution.
    """
    # Guard: do not double-resume while a thread is already active.
    with _REGISTRY_LOCK:
        entry = _RUN_REGISTRY.get(run_id)
    if entry and entry.get("status") in (ExecutionStatus.RUNNING.value, ExecutionStatus.QUEUED.value):
        return

    remember_settings(settings)
    now = time.time()
    heartbeat_timeout_seconds = _heartbeat_timeout_seconds()

    with _REGISTRY_LOCK:
        if run_id in _RUN_REGISTRY:
            _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.RUNNING.value
            _RUN_REGISTRY[run_id]["end_time"] = None
            _RUN_REGISTRY[run_id]["pause_gate"] = None
            _RUN_REGISTRY[run_id]["error"] = None
            _RUN_REGISTRY[run_id]["last_heartbeat_time"] = now
            _RUN_REGISTRY[run_id]["heartbeat_timeout_seconds"] = heartbeat_timeout_seconds
            _RUN_REGISTRY[run_id]["result_state"] = None
            _RUN_REGISTRY[run_id]["live_state"] = pipeline_state
            _RUN_REGISTRY[run_id]["settings"] = settings
        else:
            # Run was not in registry (e.g. restored from JSON without live state).
            _RUN_REGISTRY[run_id] = {
                "status": ExecutionStatus.RUNNING.value,
                "run_id": run_id,
                "start_time": now,
                "end_time": None,
                "error": None,
                "last_heartbeat_time": now,
                "heartbeat_timeout_seconds": heartbeat_timeout_seconds,
                "result_state": None,
                "live_state": pipeline_state,
                "pause_gate": None,
                "settings": settings,
            }

    def _resume_execute() -> None:
        stop_event = threading.Event()
        heartbeat_thread = threading.Thread(
            target=_run_heartbeat_ticker,
            args=(run_id, stop_event),
            daemon=True,
            name=f"heartbeat-resume-{run_id[:8]}",
        )
        watchdog_thread = threading.Thread(
            target=_run_heartbeat_watchdog,
            args=(run_id, stop_event),
            daemon=True,
            name=f"watchdog-resume-{run_id[:8]}",
        )
        heartbeat_thread.start()
        watchdog_thread.start()
        try:
            orchestrator = FrameworkOrchestrator(settings, run_id=run_id)
            _set_heartbeat(run_id)
            checkpoint = getattr(pipeline_state, "hitl_gate_checkpoint", None)
            if isinstance(checkpoint, dict) and checkpoint:
                orchestrator.hitl_service.restore_checkpoint_state(checkpoint)

            final_state = orchestrator.resume_from_checkpoint(pipeline_state, gate_id)
            setattr(final_state, "next_stage_id", None)

            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                    ExecutionStatus.QUEUED.value,
                    ExecutionStatus.RUNNING.value,
                ):
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.COMPLETED.value
                    _RUN_REGISTRY[run_id]["error"] = None
                    _RUN_REGISTRY[run_id]["result_state"] = final_state
            with _REGISTRY_LOCK:
                run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
            if run_status == ExecutionStatus.COMPLETED.value:
                mark_run_status(ExecutionStatus.COMPLETED.value)

        except GatePausedError as exc:
            gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
            pipeline_state.hitl_gate_checkpoint = gate_checkpoint
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                    ExecutionStatus.QUEUED.value,
                    ExecutionStatus.RUNNING.value,
                ):
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.PAUSED.value
                    _RUN_REGISTRY[run_id]["pause_gate"] = exc.gate_record.gate_id
                    _RUN_REGISTRY[run_id]["error"] = None
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            with _REGISTRY_LOCK:
                run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
            if run_status == ExecutionStatus.PAUSED.value:
                mark_run_status(ExecutionStatus.PAUSED.value, pause_gate=exc.gate_record.gate_id)

        except GateRejectedError as exc:
            error_msg = f"Gate rejected at {exc.gate_record.gate_id}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                    ExecutionStatus.QUEUED.value,
                    ExecutionStatus.RUNNING.value,
                ):
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = error_msg
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            with _REGISTRY_LOCK:
                run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
            if run_status == ExecutionStatus.FAILED.value:
                mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)

        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {exc}"
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY and _RUN_REGISTRY[run_id].get("status") in (
                    ExecutionStatus.QUEUED.value,
                    ExecutionStatus.RUNNING.value,
                ):
                    _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
                    _RUN_REGISTRY[run_id]["error"] = error_msg
                    _RUN_REGISTRY[run_id]["result_state"] = pipeline_state
            with _REGISTRY_LOCK:
                run_status = _RUN_REGISTRY.get(run_id, {}).get("status")
            if run_status == ExecutionStatus.FAILED.value:
                mark_run_status(ExecutionStatus.FAILED.value, error=error_msg)

        finally:
            stop_event.set()
            end_time = time.time()
            with _REGISTRY_LOCK:
                if run_id in _RUN_REGISTRY:
                    _RUN_REGISTRY[run_id]["end_time"] = end_time
            _persist_run_metadata(run_id)

    thread = threading.Thread(target=_resume_execute, daemon=True, name=f"resume-{run_id[:8]}")
    with _REGISTRY_LOCK:
        _RUN_REGISTRY[run_id]["thread"] = thread
    thread.start()


# ---------------------------------------------------------------------------
# Cancel / wait
# ---------------------------------------------------------------------------

def cancel_run(run_id: str) -> bool:
    """Mark *run_id* as failed / cancelled.

    Note: graceful thread cancellation is not supported; this only marks the
    status so the UI shows the run as failed.

    Returns:
        ``True`` if the run was active and has been marked failed.
    """
    with _REGISTRY_LOCK:
        entry = _RUN_REGISTRY.get(run_id)
    if not entry or entry.get("status") not in (
        ExecutionStatus.RUNNING.value,
        ExecutionStatus.QUEUED.value,
    ):
        return False
    with _REGISTRY_LOCK:
        if run_id in _RUN_REGISTRY:
            _RUN_REGISTRY[run_id]["status"] = ExecutionStatus.FAILED.value
            _RUN_REGISTRY[run_id]["error"] = "Cancelled by user"
            _RUN_REGISTRY[run_id]["end_time"] = time.time()
    _persist_run_metadata(run_id)
    return True


def wait_for_run(run_id: str, timeout: float = 300) -> bool:
    """Block until *run_id* leaves the active state or *timeout* expires.

    Returns:
        ``True`` if the run completed (in any terminal state) before the
        timeout; ``False`` if the timeout was reached.
    """
    start = time.time()
    while is_run_active(run_id):
        if time.time() - start > timeout:
            return False
        time.sleep(0.1)
    return True


def purge_run(run_id: str) -> bool:
    """Permanently remove *run_id* from in-memory and checkpoint metadata."""
    removed = False
    with _REGISTRY_LOCK:
        if run_id in _RUN_REGISTRY:
            del _RUN_REGISTRY[run_id]
            removed = True

    try:
        if _CHECKPOINT_FILE.exists():
            payload = json.loads(_CHECKPOINT_FILE.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and run_id in payload:
                del payload[run_id]
                _CHECKPOINT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                removed = True
    except Exception:
        pass

    return removed
