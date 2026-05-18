"""Operational HTTP server for backend runtime control.

This module is intentionally Streamlit-free so production/runtime execution can
be hosted without GUI dependencies.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from threat_modeler.backend.run_manager import (
    cancel_run,
    get_run_status,
    resume_run,
    submit_run,
)
from threat_modeler.config import (
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
    build_default_settings,
    normalize_execution_mode,
)
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState

_LOGGER = logging.getLogger(__name__)


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _runtime_settings_from_payload(payload: dict[str, Any] | None) -> RuntimeSettings:
    defaults = build_default_settings()
    if not isinstance(payload, dict):
        return defaults

    model_candidate = payload.get("model")
    pipeline_candidate = payload.get("pipeline")
    model_payload = model_candidate if isinstance(model_candidate, dict) else {}
    pipeline_payload = pipeline_candidate if isinstance(pipeline_candidate, dict) else {}

    enabled_stage_ids = pipeline_payload.get("enabled_stage_ids", defaults.pipeline.enabled_stage_ids)
    if isinstance(enabled_stage_ids, (list, tuple)):
        enabled_stage_ids = tuple(str(item) for item in enabled_stage_ids)
    else:
        enabled_stage_ids = defaults.pipeline.enabled_stage_ids

    model = ModelSelection(
        provider=str(model_payload.get("provider", defaults.model.provider)),
        model_name=str(model_payload.get("model_name", defaults.model.model_name)),
        offline_only=_coerce_bool(model_payload.get("offline_only"), defaults.model.offline_only),
        connection_url=str(model_payload.get("connection_url", defaults.model.connection_url)),
        endpoint_mode=str(model_payload.get("endpoint_mode", defaults.model.endpoint_mode)),
        request_timeout_seconds=int(
            model_payload.get("request_timeout_seconds", defaults.model.request_timeout_seconds)
        ),
        request_max_attempts=int(
            model_payload.get("request_max_attempts", defaults.model.request_max_attempts)
        ),
    )

    pipeline = PipelineSettings(
        execution_mode=normalize_execution_mode(
            pipeline_payload.get("execution_mode", defaults.pipeline.execution_mode),
            default=defaults.pipeline.execution_mode,
        ),
        enabled_stage_ids=enabled_stage_ids,
        stop_on_validation_error=_coerce_bool(
            pipeline_payload.get("stop_on_validation_error"),
            defaults.pipeline.stop_on_validation_error,
        ),
        require_hitl_gates=_coerce_bool(
            pipeline_payload.get("require_hitl_gates"),
            defaults.pipeline.require_hitl_gates,
        ),
    )

    return RuntimeSettings(model=model, pipeline=pipeline)


def _framework_state_from_payload(payload: dict[str, Any] | None) -> FrameworkState:
    state = FrameworkState()
    if not isinstance(payload, dict):
        return state

    if "raw_text" in payload:
        state.raw_text = str(payload.get("raw_text") or "")
    tables = payload.get("tables")
    if isinstance(tables, list):
        state.tables = tables
    if isinstance(payload.get("messages"), list):
        state.messages = payload["messages"]
    if isinstance(payload.get("llm_usage_by_stage"), dict):
        state.llm_usage_by_stage = payload["llm_usage_by_stage"]
    if isinstance(payload.get("llm_attempts_by_stage"), dict):
        state.llm_attempts_by_stage = payload["llm_attempts_by_stage"]
    if isinstance(payload.get("llm_prompts_by_stage"), dict):
        state.llm_prompts_by_stage = payload["llm_prompts_by_stage"]
    if isinstance(payload.get("llm_prompt_history"), list):
        state.llm_prompt_history = payload["llm_prompt_history"]
    if isinstance(payload.get("hitl_gate_checkpoint"), dict):
        state.hitl_gate_checkpoint = payload["hitl_gate_checkpoint"]
    if payload.get("hitl_paused_at_gate") is not None:
        state.hitl_paused_at_gate = str(payload["hitl_paused_at_gate"])
    if payload.get("hitl_rejected_at_gate") is not None:
        state.hitl_rejected_at_gate = str(payload["hitl_rejected_at_gate"])
    if payload.get("next_stage_id") is not None:
        state.next_stage_id = str(payload["next_stage_id"])
    return state


def _serialize_framework_state(state: FrameworkState | None) -> dict[str, Any] | None:
    if state is None:
        return None
    return {
        "next_stage_id": state.next_stage_id,
        "messages": state.messages,
        "hitl_paused_at_gate": state.hitl_paused_at_gate,
        "hitl_rejected_at_gate": state.hitl_rejected_at_gate,
        "llm_usage_totals": state.llm_usage_totals(),
        "llm_attempt_totals": state.llm_attempt_totals(),
        "has_canonical_graph": state.canonical_graph is not None,
        "has_stix_bundle": state.stix_bundle is not None,
        "has_mermaid_diagrams": bool(state.mermaid_diagrams),
        "has_final_report": bool(state.final_report),
    }


def _serialize_run_entry(entry: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    settings = entry.get("settings")
    return {
        "run_id": entry.get("run_id"),
        "status": entry.get("status"),
        "start_time": entry.get("start_time"),
        "end_time": entry.get("end_time"),
        "pause_gate": entry.get("pause_gate"),
        "error": entry.get("error"),
        "settings": asdict(settings) if isinstance(settings, RuntimeSettings) else None,
        "result_state": _serialize_framework_state(entry.get("result_state")),
        "live_state": _serialize_framework_state(entry.get("live_state")),
    }


def _execution_plan_payload(settings: RuntimeSettings) -> dict[str, Any]:
    orchestrator = FrameworkOrchestrator(settings)
    return asdict(orchestrator.build_langgraph_execution_plan())


def build_handler() -> type[BaseHTTPRequestHandler]:
    class ThreatModelerApiHandler(BaseHTTPRequestHandler):
        def _json_response(self, code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except (TypeError, ValueError):
                _LOGGER.warning("Invalid Content-Length header: %r", self.headers.get("Content-Length"))
                return {}
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            if not raw:
                return {}
            try:
                payload = json.loads(raw.decode("utf-8"))
                return payload if isinstance(payload, dict) else {}
            except json.JSONDecodeError as exc:
                _LOGGER.warning("Invalid JSON body: %s", exc)
                return {}

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"

            if path == "/health":
                self._json_response(200, {"status": "ok"})
                return

            if path == "/execution/plan":
                settings = build_default_settings()
                self._json_response(200, {"plan": _execution_plan_payload(settings)})
                return

            if path.startswith("/runs/"):
                parts = path.split("/")
                if len(parts) != 3 or parts[1] != "runs" or not parts[2]:
                    self._json_response(404, {"error": f"Unknown route: {path}"})
                    return
                run_id = parts[2]
                entry = _serialize_run_entry(get_run_status(run_id))
                if entry is None:
                    self._json_response(404, {"error": f"Unknown run_id: {run_id}"})
                    return
                self._json_response(200, {"run": entry})
                return

            self._json_response(404, {"error": f"Unknown route: {path}"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"
            payload = self._read_json()

            if path == "/execution/plan":
                settings = _runtime_settings_from_payload(payload.get("settings"))
                self._json_response(200, {"plan": _execution_plan_payload(settings)})
                return

            if path == "/runs":
                provided_run_id = payload.get("run_id")
                if provided_run_id is None:
                    run_id = str(uuid.uuid4())
                else:
                    run_id = str(provided_run_id).strip()
                    if not run_id:
                        self._json_response(400, {"error": "run_id must be non-empty when provided"})
                        return
                settings = _runtime_settings_from_payload(payload.get("settings"))
                initial_state = _framework_state_from_payload(payload.get("initial_state"))
                submit_run(run_id, initial_state, settings)
                self._json_response(202, {"run_id": run_id, "status_url": f"/runs/{run_id}"})
                return

            if path.endswith("/cancel") and "/runs/" in path:
                parts = path.split("/")
                if len(parts) == 4 and parts[1] == "runs" and parts[3] == "cancel" and parts[2]:
                    run_id = parts[2]
                    cancelled = cancel_run(run_id)
                    code = 200 if cancelled else 409
                    self._json_response(code, {"run_id": run_id, "cancelled": cancelled})
                    return

            if path.endswith("/resume") and "/runs/" in path:
                parts = path.split("/")
                if len(parts) == 4 and parts[1] == "runs" and parts[3] == "resume" and parts[2]:
                    run_id = parts[2]
                    gate_id = str(payload.get("gate_id") or "")
                    if not gate_id:
                        self._json_response(400, {"error": "gate_id is required"})
                        return
                    settings = _runtime_settings_from_payload(payload.get("settings"))
                    pipeline_state = _framework_state_from_payload(payload.get("pipeline_state"))
                    resume_run(run_id, gate_id, pipeline_state, settings)
                    self._json_response(202, {"run_id": run_id, "resumed_from_gate": gate_id})
                    return

            self._json_response(404, {"error": f"Unknown route: {path}"})

        def log_message(self, msg_format: str, *args: Any) -> None:
            _LOGGER.info("api_request %s", msg_format % args)

    return ThreatModelerApiHandler


def start_server(*, host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), build_handler())
    _LOGGER.info("Operational API server listening on http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
