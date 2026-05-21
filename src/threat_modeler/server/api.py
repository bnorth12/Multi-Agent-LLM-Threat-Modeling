"""Operational HTTP server for backend runtime control.

This module is intentionally Streamlit-free so production/runtime execution can
be hosted without GUI dependencies.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from threat_modeler.backend import prompt_store
from threat_modeler.backend.run_manager import (
    cancel_run,
    get_all_run_ids,
    get_run_status,
    purge_run,
    resume_run,
    submit_run,
)
from threat_modeler.server.hmi_data import (
    extract_threats_from_state,
    extract_stages_from_messages,
    extract_llm_metrics,
    serialize_gate,
)
from threat_modeler.config import (
    PROVIDER_MATRIX,
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
    build_default_settings,
    normalize_execution_mode,
)
from threat_modeler.llm import OpenAiCompatibleAdapter
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState

_LOGGER = logging.getLogger(__name__)
_CONFIG_LOCK = threading.Lock()
_CURRENT_SETTINGS: RuntimeSettings = build_default_settings()
_RUN_CATALOG_LOCK = threading.Lock()
_RUN_CATALOG_FILE = os.path.join(os.path.expanduser("~"), ".multi_agent_threat_modeler_run_catalog.json")


def _load_run_catalog() -> dict[str, dict[str, Any]]:
    try:
        if not os.path.exists(_RUN_CATALOG_FILE):
            return {}
        with open(_RUN_CATALOG_FILE, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _save_run_catalog(catalog: dict[str, dict[str, Any]]) -> None:
    try:
        with open(_RUN_CATALOG_FILE, "w", encoding="utf-8") as handle:
            json.dump(catalog, handle, indent=2)
    except Exception:
        pass


def _get_run_metadata(run_id: str) -> dict[str, Any]:
    with _RUN_CATALOG_LOCK:
        catalog = _load_run_catalog()
        entry = catalog.get(run_id)
    return entry if isinstance(entry, dict) else {}


def _set_run_metadata(run_id: str, *, name: str | None = None, archived: bool | None = None) -> dict[str, Any]:
    with _RUN_CATALOG_LOCK:
        catalog = _load_run_catalog()
        existing = catalog.get(run_id)
        metadata = existing if isinstance(existing, dict) else {}
        if name is not None:
            metadata["name"] = name
        if archived is not None:
            metadata["archived"] = archived
        catalog[run_id] = metadata
        _save_run_catalog(catalog)
    return metadata


def _remove_run_metadata(run_id: str) -> None:
    with _RUN_CATALOG_LOCK:
        catalog = _load_run_catalog()
        if run_id in catalog:
            del catalog[run_id]
            _save_run_catalog(catalog)


def _purge_archived_runs() -> list[str]:
    with _RUN_CATALOG_LOCK:
        catalog = _load_run_catalog()
    archived_ids = [rid for rid, meta in catalog.items() if isinstance(meta, dict) and meta.get("archived") is True]
    purged: list[str] = []
    for run_id in archived_ids:
        if purge_run(run_id):
            purged.append(run_id)
            _remove_run_metadata(run_id)
    return purged


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
        api_key=str(model_payload.get("api_key", getattr(defaults.model, "api_key", ""))),
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


def _settings_with_api_key(settings: RuntimeSettings, api_key: str) -> RuntimeSettings:
    if not api_key.strip():
        return settings
    model = settings.model
    updated_model = ModelSelection(
        provider=model.provider,
        model_name=model.model_name,
        api_key=api_key.strip(),
        offline_only=model.offline_only,
        connection_url=model.connection_url,
        endpoint_mode=model.endpoint_mode,
        request_timeout_seconds=model.request_timeout_seconds,
        request_max_attempts=model.request_max_attempts,
    )
    return RuntimeSettings(model=updated_model, pipeline=settings.pipeline)


def _verify_config_connection(settings: RuntimeSettings) -> tuple[bool, str]:
    provider = settings.model.provider
    provider_info = PROVIDER_MATRIX.get(provider)
    if provider_info is None:
        return False, f"Unknown provider '{provider}'."

    if provider == "fixture":
        return True, "Fixture mode active."

    if settings.model.offline_only:
        return False, "Live verification requires offline_only=false for real providers."

    requires_api_key = bool(provider_info.get("requires_api_key", False))
    if requires_api_key and not settings.model.api_key.strip():
        return False, "API key required for selected provider."

    requires_url = bool(provider_info.get("requires_url", False))
    if requires_url and not settings.model.connection_url.strip():
        return False, "Connection URL required for selected provider."

    base_url_map = {
        "openai": "https://api.openai.com/v1",
        "xai": "https://api.x.ai/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }
    base_url = settings.model.connection_url.strip() or base_url_map.get(provider, "")
    if not base_url:
        return False, "No connection URL available for provider verification."

    timeout_seconds = max(5, min(int(settings.model.request_timeout_seconds), 20))
    adapter = OpenAiCompatibleAdapter(
        model=settings.model.model_name,
        api_key=settings.model.api_key,
        endpoint_mode=settings.model.endpoint_mode,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        max_attempts=1,
    )

    try:
        reply = adapter.complete(
            system_prompt="You are a connection verification probe.",
            user_message="Reply with exactly OK.",
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Live prompt ping failed: {exc}"

    if not str(reply).strip():
        return False, "Live prompt ping failed: provider returned an empty response."

    return True, "Live prompt ping succeeded."


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



def _settings_to_response_payload(settings: RuntimeSettings | None) -> dict[str, Any] | None:
    if not isinstance(settings, RuntimeSettings):
        return None
    payload = asdict(settings)
    model_payload = payload.get("model") if isinstance(payload, dict) else None
    if isinstance(model_payload, dict) and "api_key" in model_payload:
        model_payload["api_key"] = ""
    return payload

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
    run_id = entry.get("run_id")
    metadata = _get_run_metadata(str(run_id)) if run_id else {}
    last_heartbeat = entry.get("last_heartbeat_time")
    heartbeat_timeout = entry.get("heartbeat_timeout_seconds")
    pause_gate = entry.get("pause_gate")
    live_state = entry.get("live_state") if isinstance(entry.get("live_state"), FrameworkState) else None
    result_state = entry.get("result_state") if isinstance(entry.get("result_state"), FrameworkState) else None
    paused_at_gate = pause_gate or getattr(live_state, "hitl_paused_at_gate", None) or getattr(result_state, "hitl_paused_at_gate", None)
    try:
        heartbeat_age_seconds = None if paused_at_gate else (max(0.0, time.time() - float(last_heartbeat)) if last_heartbeat else None)
    except Exception:
        heartbeat_age_seconds = None

    return {
        "run_id": entry.get("run_id"),
        "run_name": metadata.get("name") or str(entry.get("run_id") or ""),
        "archived": bool(metadata.get("archived", False)),
        "status": entry.get("status"),
        "start_time": entry.get("start_time"),
        "end_time": entry.get("end_time"),
        "pause_gate": pause_gate,
        "error": entry.get("error"),
        "last_heartbeat_time": last_heartbeat,
        "heartbeat_timeout_seconds": heartbeat_timeout,
        "heartbeat_age_seconds": heartbeat_age_seconds,
        "settings": _settings_to_response_payload(settings),
        "result_state": _serialize_framework_state(result_state),
        "live_state": _serialize_framework_state(live_state),
    }


def _execution_plan_payload(settings: RuntimeSettings) -> dict[str, Any]:
    orchestrator = FrameworkOrchestrator(settings)
    return asdict(orchestrator.build_langgraph_execution_plan())


def _get_current_settings() -> RuntimeSettings:
    with _CONFIG_LOCK:
        return _CURRENT_SETTINGS


def _set_current_settings(settings: RuntimeSettings) -> None:
    global _CURRENT_SETTINGS
    with _CONFIG_LOCK:
        _CURRENT_SETTINGS = settings


def _resolve_run_state(run_id: str) -> FrameworkState | None:
    entry = get_run_status(run_id)
    if not isinstance(entry, dict):
        return None
    result_state = entry.get("result_state")
    if isinstance(result_state, FrameworkState):
        return result_state
    live_state = entry.get("live_state")
    if isinstance(live_state, FrameworkState):
        return live_state
    return None


def _serialize_checkpoint_gates(checkpoint: dict[str, Any] | None) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    if not isinstance(checkpoint, dict):
        return gates

    gates_raw = checkpoint.get("gates", {})
    if isinstance(gates_raw, dict):
        raw_items = list(gates_raw.values())
    elif isinstance(gates_raw, list):
        raw_items = gates_raw
    else:
        raw_items = []

    for gate_data in raw_items:
        try:
            from threat_modeler.hitl.models import HitlGateRecord

            if isinstance(gate_data, dict):
                gate = HitlGateRecord.from_dict(gate_data)
                gates.append(serialize_gate(gate))
        except Exception:
            pass

    return gates


def _auth_required() -> bool:
    return _coerce_bool(os.environ.get("THREAT_MODELER_AUTH_REQUIRED"), False)


def _expected_auth_token() -> str:
    return str(os.environ.get("THREAT_MODELER_AUTH_TOKEN", "")).strip()


def build_handler() -> type[BaseHTTPRequestHandler]:
    class ThreatModelerApiHandler(BaseHTTPRequestHandler):
        def _send_cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")

        def _authorize_request(self, path: str) -> bool:
            if path == "/health":
                return True
            if not _auth_required():
                return True

            auth_header = str(self.headers.get("Authorization") or "").strip()
            if not auth_header.startswith("Bearer "):
                self._json_response(
                    401,
                    {
                        "error": "Unauthorized",
                        "details": "Missing or invalid Authorization header.",
                    },
                )
                return False

            token = auth_header.removeprefix("Bearer ").strip()
            if not token:
                self._json_response(401, {"error": "Unauthorized", "details": "Bearer token is empty."})
                return False

            expected = _expected_auth_token()
            if expected and token != expected:
                self._json_response(401, {"error": "Unauthorized", "details": "Bearer token mismatch."})
                return False

            return True

        def _json_response(self, code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._send_cors_headers()
            self.send_header("Content-Length", "0")
            self.end_headers()

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

        def _normalize_path(self, raw_path: str) -> str:
            path = raw_path.rstrip("/") or "/"
            if path == "/api":
                return "/"
            if path.startswith("/api/"):
                return path[4:]
            return path

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = self._normalize_path(parsed.path)

            if not self._authorize_request(path):
                return

            if path == "/health":
                self._json_response(200, {"status": "ok"})
                return

            if path == "/execution/plan":
                settings = _get_current_settings()
                self._json_response(200, {"plan": _execution_plan_payload(settings)})
                return

            if path == "/config":
                self._json_response(200, {"config": _settings_to_response_payload(_get_current_settings())})
                return

            if path == "/prompts":
                prompts_payload: dict[str, dict[str, Any]] = {}
                for agent_id in prompt_store.AGENT_IDS:
                    prompts_payload[agent_id] = {
                        "prompt": prompt_store.get_prompt(agent_id),
                        "expected_output": prompt_store.get_expected_output(agent_id),
                        "temperature": prompt_store.get_temperature(agent_id),
                        "is_modified": prompt_store.is_modified(agent_id),
                    }
                self._json_response(
                    200,
                    {
                        "prompts": prompts_payload,
                        "prompt_store_path": prompt_store.get_store_path(),
                    },
                )
                return

            if path.startswith("/prompts/"):
                parts = path.split("/")
                if len(parts) == 3 and parts[1] == "prompts" and parts[2]:
                    agent_id = parts[2]
                    try:
                        history = [entry._asdict() for entry in prompt_store.get_history(agent_id)]
                        self._json_response(
                            200,
                            {
                                "agent_id": agent_id,
                                "prompt": prompt_store.get_prompt(agent_id),
                                "default_prompt": prompt_store.get_default_prompt(agent_id),
                                "expected_output": prompt_store.get_expected_output(agent_id),
                                "temperature": prompt_store.get_temperature(agent_id),
                                "is_modified": prompt_store.is_modified(agent_id),
                                "history": history,
                                "prompt_store_path": prompt_store.get_store_path(),
                            },
                        )
                    except KeyError:
                        self._json_response(404, {"error": f"Unknown agent_id: {agent_id}"})
                    return

            if path == "/runs":
                runs = []
                for run_id in get_all_run_ids():
                    serialized = _serialize_run_entry(get_run_status(run_id))
                    if serialized is not None:
                        runs.append(serialized)
                self._json_response(200, {"runs": runs})
                return

            if path.startswith("/runs/") and "/artifacts/" in path:
                parts = path.split("/")
                if len(parts) == 5 and parts[1] == "runs" and parts[3] == "artifacts" and parts[2] and parts[4]:
                    run_id = parts[2]
                    artifact_name = parts[4]
                    state = _resolve_run_state(run_id)
                    if state is None:
                        self._json_response(404, {"error": f"Unknown or incomplete run_id: {run_id}"})
                        return

                    if artifact_name == "canonical":
                        self._json_response(200, {"artifact": "canonical", "content": state.canonical_graph_dict()})
                        return
                    if artifact_name == "stix":
                        self._json_response(200, {"artifact": "stix", "content": state.stix_bundle or {}})
                        return
                    if artifact_name == "mermaid":
                        self._json_response(200, {"artifact": "mermaid", "content": state.mermaid_diagrams})
                        return
                    if artifact_name == "report":
                        self._json_response(200, {"artifact": "report", "content": state.final_report or ""})
                        return

                    self._json_response(404, {"error": f"Unknown artifact: {artifact_name}"})
                    return

            if path.startswith("/runs/") and "/state/" in path:
                parts = path.split("/")
                if len(parts) >= 4 and parts[1] == "runs" and parts[3] == "state" and parts[2]:
                    run_id = parts[2]
                    state_type = parts[4] if len(parts) > 4 else ""

                    run_entry = get_run_status(run_id)
                    if run_entry is None:
                        self._json_response(404, {"error": f"Unknown run_id: {run_id}"})
                        return

                    state = _resolve_run_state(run_id)
                    if state is None:
                        self._json_response(404, {"error": f"No state available for run_id: {run_id}"})
                        return

                    # GET /runs/{run_id}/state/threats
                    if state_type == "threats":
                        threats = extract_threats_from_state(state)
                        self._json_response(200, {"threats": threats})
                        return

                    # GET /runs/{run_id}/state/gates
                    if state_type == "gates":
                        checkpoint = state.hitl_gate_checkpoint or {}
                        gates = _serialize_checkpoint_gates(checkpoint)
                        self._json_response(200, {"gates": gates})
                        return

                    # GET /runs/{run_id}/state/messages
                    if state_type == "messages":
                        messages = state.messages or []
                        self._json_response(200, {"messages": messages})
                        return

                    # GET /runs/{run_id}/state/stages
                    if state_type == "stages":
                        stages = extract_stages_from_messages(
                            state.messages or [],
                            run_status=str(run_entry.get("status", "")),
                            next_stage_id=state.next_stage_id,
                        )
                        self._json_response(200, {"stages": stages})
                        return

                    # GET /runs/{run_id}/state/metrics
                    if state_type == "metrics":
                        metrics = extract_llm_metrics(state)
                        self._json_response(200, {"metrics": metrics})
                        return

                    # GET /runs/{run_id}/state/prompts
                    if state_type == "prompts":
                        self._json_response(
                            200,
                            {
                                "last_prompt": state.llm_prompt_history[-1] if state.llm_prompt_history else None,
                                "prompt_history": state.llm_prompt_history or [],
                                "prompts_by_stage": state.llm_prompts_by_stage or {},
                            },
                        )
                        return

                    # GET /runs/{run_id}/state/full
                    if state_type == "full" or not state_type:
                        threats = extract_threats_from_state(state)
                        stages = extract_stages_from_messages(
                            state.messages or [],
                            run_status=str(run_entry.get("status", "")),
                            next_stage_id=state.next_stage_id,
                        )
                        metrics = extract_llm_metrics(state)
                        checkpoint = state.hitl_gate_checkpoint or {}
                        gates = _serialize_checkpoint_gates(checkpoint)

                        self._json_response(200, {
                            "state": _serialize_framework_state(state),
                            "threats": threats,
                            "gates": gates,
                            "stages": stages,
                            "metrics": metrics,
                            "messages": state.messages or [],
                        })
                        return

                    self._json_response(404, {"error": f"Unknown state endpoint: {state_type}"})
                    return

            self._json_response(404, {"error": f"Unknown route: {path}"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = self._normalize_path(parsed.path)

            if not self._authorize_request(path):
                return

            payload = self._read_json()

            if path == "/execution/plan":
                settings = _runtime_settings_from_payload(payload.get("settings"))
                self._json_response(200, {"plan": _execution_plan_payload(settings)})
                return

            if path == "/config":
                candidate = payload.get("config") if isinstance(payload.get("config"), dict) else payload
                settings = _runtime_settings_from_payload(candidate)
                _set_current_settings(settings)
                self._json_response(200, {"config": _settings_to_response_payload(settings)})
                return

            if path == "/config/verify":
                candidate = payload.get("config") if isinstance(payload.get("config"), dict) else payload
                settings = _runtime_settings_from_payload(candidate)
                api_key = str(payload.get("api_key") or "").strip()
                verification_settings = _settings_with_api_key(settings, api_key)
                ok, message = _verify_config_connection(verification_settings)
                self._json_response(200, {"ok": ok, "message": message})
                return

            if path.startswith("/prompts/"):
                parts = path.split("/")
                if len(parts) == 3 and parts[1] == "prompts" and parts[2]:
                    agent_id = parts[2]
                    try:
                        if payload.get("prompt") is not None:
                            prompt_store.set_prompt(agent_id, str(payload.get("prompt")), actor="api")
                        if payload.get("expected_output") is not None:
                            prompt_store.set_expected_output(agent_id, str(payload.get("expected_output")))
                        if payload.get("temperature") is not None:
                            prompt_store.set_temperature(agent_id, float(payload.get("temperature")))
                        self._json_response(
                            200,
                            {
                                "agent_id": agent_id,
                                "prompt": prompt_store.get_prompt(agent_id),
                                "expected_output": prompt_store.get_expected_output(agent_id),
                                "temperature": prompt_store.get_temperature(agent_id),
                            },
                        )
                    except KeyError:
                        self._json_response(404, {"error": f"Unknown agent_id: {agent_id}"})
                    except ValueError as exc:
                        self._json_response(400, {"error": str(exc)})
                    return

            if path == "/runs":
                provided_run_id = payload.get("run_id")
                run_name = str(payload.get("run_name") or "").strip()
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
                _set_run_metadata(run_id, name=run_name or run_id, archived=False)
                self._json_response(202, {"run_id": run_id, "status_url": f"/runs/{run_id}"})
                return

            if path.startswith("/runs/"):
                parts = path.split("/")
                if len(parts) == 3 and parts[1] == "runs" and parts[2]:
                    run_id = parts[2]
                    settings = _runtime_settings_from_payload(payload.get("settings"))
                    initial_state = _framework_state_from_payload(payload.get("initial_state"))
                    submit_run(run_id, initial_state, settings)
                    _set_run_metadata(run_id, name=run_id, archived=False)
                    self._json_response(201, {"run_id": run_id, "status_url": f"/runs/{run_id}"})
                    return

            if path == "/runs/purge":
                archived_only = _coerce_bool(payload.get("archived_only"), True)
                if archived_only:
                    purged_run_ids = _purge_archived_runs()
                    self._json_response(200, {"purged_run_ids": purged_run_ids, "count": len(purged_run_ids)})
                    return
                self._json_response(400, {"error": "Only archived_only purge mode is supported."})
                return

            if path.startswith("/runs/") and path.endswith("/metadata"):
                parts = path.split("/")
                if len(parts) == 4 and parts[1] == "runs" and parts[2] and parts[3] == "metadata":
                    run_id = parts[2]
                    if get_run_status(run_id) is None:
                        self._json_response(404, {"error": f"Unknown run_id: {run_id}"})
                        return
                    name = payload.get("run_name")
                    archived = payload.get("archived")
                    metadata = _set_run_metadata(
                        run_id,
                        name=str(name).strip() if name is not None else None,
                        archived=_coerce_bool(archived, False) if archived is not None else None,
                    )
                    self._json_response(200, {"run_id": run_id, "metadata": metadata})
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
                    run_entry = get_run_status(run_id)
                    settings_payload = payload.get("settings")
                    if isinstance(run_entry, dict) and settings_payload is None and isinstance(run_entry.get("settings"), RuntimeSettings):
                        settings = run_entry["settings"]
                    else:
                        settings = _runtime_settings_from_payload(settings_payload)

                    pipeline_payload = payload.get("pipeline_state")
                    pipeline_state = _framework_state_from_payload(pipeline_payload) if pipeline_payload is not None else _resolve_run_state(run_id)
                    if pipeline_state is None:
                        self._json_response(404, {"error": f"No resumable state available for run_id: {run_id}"})
                        return
                    resume_run(run_id, gate_id, pipeline_state, settings)
                    self._json_response(202, {"run_id": run_id, "resumed_from_gate": gate_id})
                    return

            if path.startswith("/runs/") and "/gates/" in path and "/decide" in path:
                parts = path.split("/")
                if len(parts) >= 5 and parts[1] == "runs" and parts[3] == "gates" and parts[5] == "decide" and parts[2] and parts[4]:
                    run_id = parts[2]
                    gate_id = parts[4]

                    run_entry = get_run_status(run_id)
                    if run_entry is None:
                        self._json_response(404, {"error": f"Unknown run_id: {run_id}"})
                        return

                    state = _resolve_run_state(run_id)
                    if state is None:
                        self._json_response(404, {"error": f"No state available for run_id: {run_id}"})
                        return

                    # Apply decision through the HITL engine and persist updated checkpoint state.
                    from threat_modeler.hitl import GateRejectedError
                    from threat_modeler.hitl.models import GateAction
                    from threat_modeler.orchestrator import FrameworkOrchestrator
                    try:
                        action = GateAction(str(payload.get("action", "accept_as_is")))
                        settings = run_entry.get("settings") if isinstance(run_entry.get("settings"), RuntimeSettings) else _get_current_settings()
                        orchestrator = FrameworkOrchestrator(settings, run_id=run_id)
                        checkpoint = state.hitl_gate_checkpoint or {}
                        if checkpoint:
                            orchestrator.hitl_service.restore_checkpoint_state(checkpoint)

                        gate_record = orchestrator.hitl_service.submit_decision(
                            gate_id=gate_id,
                            actor=str(payload.get("actor", "web_ui")),
                            role=str(payload.get("role", "analyst")),
                            action=action,
                            rationale=str(payload.get("rationale", "")),
                        )
                        state.hitl_gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
                        state.hitl_paused_at_gate = gate_id if gate_record.status.value in {"open", "draft"} else None
                        state.hitl_rejected_at_gate = gate_id if gate_record.status.value == "rejected" else None

                        self._json_response(200, {
                            "run_id": run_id,
                            "gate_id": gate_id,
                            "gate_status": gate_record.status.value,
                            "decision_recorded": True,
                        })
                    except GateRejectedError as exc:
                        state.hitl_gate_checkpoint = orchestrator.hitl_service.checkpoint_state()
                        state.hitl_paused_at_gate = None
                        state.hitl_rejected_at_gate = exc.gate_record.gate_id
                        self._json_response(200, {
                            "run_id": run_id,
                            "gate_id": gate_id,
                            "gate_status": exc.gate_record.status.value,
                            "decision_recorded": True,
                        })
                    except (ValueError, KeyError) as exc:
                        self._json_response(400, {"error": str(exc)})
                    return

            if path.startswith("/runs/") and "/threats/" in path and "/decide" in path:
                parts = path.split("/")
                if len(parts) >= 5 and parts[1] == "runs" and parts[3] == "threats" and parts[5] == "decide" and parts[2] and parts[4]:
                    run_id = parts[2]
                    threat_id = parts[4]

                    run_entry = get_run_status(run_id)
                    if run_entry is None:
                        self._json_response(404, {"error": f"Unknown run_id: {run_id}"})
                        return

                    state = _resolve_run_state(run_id)
                    if state is None:
                        self._json_response(404, {"error": f"No state available for run_id: {run_id}"})
                        return

                    # Persist threat decision to run state so notes rehydrate in UI.
                    decision = {
                        "threat_id": threat_id,
                        "decision": str(payload.get("decision", "approve")),  # approve, reject, needs_work
                        "notes": str(payload.get("notes", "")),
                        "reviewer": str(payload.get("reviewer", "web_ui")),
                    }
                    state.threat_review_decisions[threat_id] = decision

                    self._json_response(200, {
                        "run_id": run_id,
                        "threat_id": threat_id,
                        "decision_recorded": True,
                    })
                    return

            self._json_response(404, {"error": f"Unknown route: {path}"})

        def do_DELETE(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = self._normalize_path(parsed.path)

            if not self._authorize_request(path):
                return

            if path.startswith("/runs/"):
                parts = path.split("/")
                if len(parts) == 3 and parts[1] == "runs" and parts[2]:
                    run_id = parts[2]
                    cancelled = cancel_run(run_id)
                    code = 200 if cancelled else 409
                    self._json_response(code, {"run_id": run_id, "cancelled": cancelled})
                    return

                if len(parts) == 4 and parts[1] == "runs" and parts[3] == "purge" and parts[2]:
                    run_id = parts[2]
                    removed = purge_run(run_id)
                    _remove_run_metadata(run_id)
                    self._json_response(200 if removed else 404, {"run_id": run_id, "purged": removed})
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
