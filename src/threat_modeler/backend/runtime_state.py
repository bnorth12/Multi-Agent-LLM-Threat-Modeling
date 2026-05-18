"""Thread-safe backend runtime state shared across HMI screens and background work."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from threat_modeler.config import (
    EXECUTION_MODE_GOVERNED,
    LIVE_LLM_DEFAULT_MAX_ATTEMPTS,
    LIVE_LLM_DEFAULT_TIMEOUT_SECONDS,
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
    normalize_execution_mode,
)


@dataclass
class BackendRuntimeState:
    """Process-local backend state for the current live run and cached settings."""

    last_settings: Optional[RuntimeSettings] = None
    active_run_id: Optional[str] = None
    active_status: str = "idle"
    active_error: Optional[str] = None
    active_pause_gate: Optional[str] = None
    provider_label: str = "Unconfigured"
    provider_status: str = "⚪ UNCONFIGURED"
    provider_is_live: bool = False
    model_connection_valid: bool = False
    offline_override_active: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


_BACKEND_STATE = BackendRuntimeState()
_STATE_FILE = Path.home() / ".multi_agent_threat_modeler_runtime_state.json"


def _serialize_settings(settings: RuntimeSettings | None) -> dict | None:
    if settings is None:
        return None
    return asdict(settings)


def _deserialize_settings(payload: dict | None) -> RuntimeSettings | None:
    if not isinstance(payload, dict):
        return None

    model_data = payload.get("model")
    pipeline_data = payload.get("pipeline")
    if not isinstance(model_data, dict):
        return None
    if not isinstance(pipeline_data, dict):
        pipeline_data = {}

    try:
        model = ModelSelection(
            provider=str(model_data.get("provider", "fixture")),
            model_name=str(model_data.get("model_name", "fixture-placeholder")),
            offline_only=bool(model_data.get("offline_only", True)),
            connection_url=str(model_data.get("connection_url", "")),
            endpoint_mode=str(model_data.get("endpoint_mode", "chat_completions")),
            request_timeout_seconds=int(model_data.get("request_timeout_seconds", LIVE_LLM_DEFAULT_TIMEOUT_SECONDS)),
            request_max_attempts=int(model_data.get("request_max_attempts", LIVE_LLM_DEFAULT_MAX_ATTEMPTS)),
        )
        pipeline = PipelineSettings(
            execution_mode=normalize_execution_mode(
                pipeline_data.get("execution_mode", EXECUTION_MODE_GOVERNED),
                default=EXECUTION_MODE_GOVERNED,
            ),
            enabled_stage_ids=tuple(pipeline_data.get("enabled_stage_ids", ())),
            stop_on_validation_error=bool(pipeline_data.get("stop_on_validation_error", True)),
            require_hitl_gates=bool(pipeline_data.get("require_hitl_gates", True)),
        )
        return RuntimeSettings(model=model, pipeline=pipeline)
    except Exception:
        return None


def _persist_state_locked() -> None:
    payload = {
        "last_settings": _serialize_settings(_BACKEND_STATE.last_settings),
        "provider_label": _BACKEND_STATE.provider_label,
        "provider_status": _BACKEND_STATE.provider_status,
        "provider_is_live": _BACKEND_STATE.provider_is_live,
        "model_connection_valid": _BACKEND_STATE.model_connection_valid,
        "offline_override_active": _BACKEND_STATE.offline_override_active,
    }
    try:
        _STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        pass


def _restore_state_from_disk() -> None:
    if not _STATE_FILE.exists():
        return
    try:
        payload = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return

    if not isinstance(payload, dict):
        return

    restored_settings = _deserialize_settings(payload.get("last_settings"))

    with _BACKEND_STATE.lock:
        _BACKEND_STATE.last_settings = restored_settings
        _BACKEND_STATE.provider_label = str(payload.get("provider_label", _BACKEND_STATE.provider_label))
        _BACKEND_STATE.provider_status = str(payload.get("provider_status", _BACKEND_STATE.provider_status))
        _BACKEND_STATE.provider_is_live = bool(payload.get("provider_is_live", _BACKEND_STATE.provider_is_live))
        _BACKEND_STATE.model_connection_valid = bool(
            payload.get("model_connection_valid", _BACKEND_STATE.model_connection_valid)
        )
        _BACKEND_STATE.offline_override_active = bool(
            payload.get("offline_override_active", _BACKEND_STATE.offline_override_active)
        )


_restore_state_from_disk()


def snapshot() -> BackendRuntimeState:
    """Return the shared backend state object."""
    return _BACKEND_STATE


def remember_settings(settings: RuntimeSettings | None) -> None:
    """Persist the most recent runtime settings for reload recovery."""
    with _BACKEND_STATE.lock:
        _BACKEND_STATE.last_settings = settings
        if settings is None:
            _BACKEND_STATE.provider_label = "Unconfigured"
            _BACKEND_STATE.provider_status = "⚪ UNCONFIGURED"
            _BACKEND_STATE.provider_is_live = False
            _BACKEND_STATE.model_connection_valid = False
            _BACKEND_STATE.offline_override_active = False
            return

        provider = settings.model.provider
        offline = settings.model.offline_only
        if provider == "fixture" or offline:
            _BACKEND_STATE.provider_label = "Local/Fixture"
            _BACKEND_STATE.provider_status = "⚫ LOCAL (FIXTURE)"
            _BACKEND_STATE.provider_is_live = False
            _BACKEND_STATE.model_connection_valid = True
            _BACKEND_STATE.offline_override_active = False
        else:
            _BACKEND_STATE.provider_label = settings.model.provider
            _BACKEND_STATE.provider_status = "✅ LIVE LLM"
            _BACKEND_STATE.provider_is_live = True
        _persist_state_locked()


def remember_validation_state(is_valid: bool, *, offline_override: bool = False) -> None:
    """Persist connection validation status for cross-session continuity."""
    with _BACKEND_STATE.lock:
        _BACKEND_STATE.model_connection_valid = bool(is_valid)
        _BACKEND_STATE.offline_override_active = bool(offline_override)
        _persist_state_locked()


def get_validation_state() -> tuple[bool, bool]:
    """Return (model_connection_valid, offline_override_active)."""
    with _BACKEND_STATE.lock:
        return (
            _BACKEND_STATE.model_connection_valid,
            _BACKEND_STATE.offline_override_active,
        )


def get_last_settings() -> RuntimeSettings | None:
    """Return the last known runtime settings snapshot."""
    with _BACKEND_STATE.lock:
        return _BACKEND_STATE.last_settings


def mark_run_started(run_id: str, settings: RuntimeSettings) -> None:
    """Mark the backend as running with the supplied settings."""
    with _BACKEND_STATE.lock:
        _BACKEND_STATE.active_run_id = run_id
        _BACKEND_STATE.active_status = "queued"
        _BACKEND_STATE.active_error = None
        _BACKEND_STATE.active_pause_gate = None
    remember_settings(settings)


def mark_run_status(status: str, *, error: str | None = None, pause_gate: str | None = None) -> None:
    """Update the backend execution status."""
    with _BACKEND_STATE.lock:
        _BACKEND_STATE.active_status = status
        _BACKEND_STATE.active_error = error
        _BACKEND_STATE.active_pause_gate = pause_gate


def clear_run_state() -> None:
    """Reset active run metadata while keeping the last known settings cached."""
    with _BACKEND_STATE.lock:
        _BACKEND_STATE.active_run_id = None
        _BACKEND_STATE.active_status = "idle"
        _BACKEND_STATE.active_error = None
        _BACKEND_STATE.active_pause_gate = None


def get_provider_display() -> tuple[str, str, bool]:
    """Return the current provider display label, status badge, and live flag."""
    with _BACKEND_STATE.lock:
        return (
            _BACKEND_STATE.provider_label,
            _BACKEND_STATE.provider_status,
            _BACKEND_STATE.provider_is_live,
        )
