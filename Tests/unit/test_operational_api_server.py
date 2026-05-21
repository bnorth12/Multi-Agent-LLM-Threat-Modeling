"""Unit tests for non-Streamlit operational API server."""

from __future__ import annotations

import json
import os
import threading
import urllib.request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from threat_modeler.server.api import build_handler


def _start_test_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), build_handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json_with_status(url: str, headers: dict[str, str] | None = None) -> tuple[int, dict]:
    request = urllib.request.Request(url=url, method="GET", headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.getcode(), json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _delete_json(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url=url, method="DELETE")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.getcode(), json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_health_endpoint_returns_ok():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        payload = _get_json(f"{base_url}/health")
        assert payload == {"status": "ok"}
    finally:
        server.shutdown()
        server.server_close()


def test_execution_plan_endpoint_returns_langgraph_plan():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        payload = _get_json(f"{base_url}/execution/plan")
        assert "plan" in payload
        assert "nodes" in payload["plan"]
        assert len(payload["plan"]["nodes"]) >= 1
    finally:
        server.shutdown()
        server.server_close()


def test_post_runs_delegates_to_run_manager_submit():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with patch("threat_modeler.server.api.submit_run") as submit_mock:
            payload = _post_json(
                f"{base_url}/runs",
                {
                    "run_id": "run-123",
                    "initial_state": {"raw_text": "subsystem: Nav, component: GPS"},
                },
            )
            assert payload["run_id"] == "run-123"
            submit_mock.assert_called_once()
    finally:
        server.shutdown()
        server.server_close()


def test_config_round_trip_endpoint():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        updated = _post_json(
            f"{base_url}/config",
            {
                "config": {
                    "model": {"provider": "fixture", "model_name": "fixture-placeholder"},
                    "pipeline": {"execution_mode": "langgraph-compatible"},
                }
            },
        )
        assert updated["config"]["model"]["provider"] == "fixture"

        fetched = _get_json(f"{base_url}/config")
        assert fetched["config"]["pipeline"]["execution_mode"] == "langgraph-compatible"
    finally:
        server.shutdown()
        server.server_close()


def test_prompts_endpoints_return_catalog_and_single_prompt():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        all_prompts = _get_json(f"{base_url}/prompts")
        assert "prompts" in all_prompts
        assert "agent_01" in all_prompts["prompts"]

        single_prompt = _get_json(f"{base_url}/prompts/agent_01")
        assert single_prompt["agent_id"] == "agent_01"
        assert "prompt" in single_prompt
    finally:
        server.shutdown()
        server.server_close()


def test_runs_list_and_delete_cancel_endpoint():
    server, _ = _start_test_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with patch("threat_modeler.server.api.submit_run") as submit_mock:
            _post_json(f"{base_url}/runs", {"run_id": "run-list-1"})
            submit_mock.assert_called_once()

        with patch("threat_modeler.server.api.get_all_run_ids", return_value=["run-list-1"]), patch(
            "threat_modeler.server.api.get_run_status",
            return_value={
                "run_id": "run-list-1",
                "status": "running",
                "start_time": None,
                "end_time": None,
                "pause_gate": None,
                "error": None,
                "settings": None,
                "result_state": None,
                "live_state": None,
            },
        ):
            runs_payload = _get_json(f"{base_url}/runs")
            assert runs_payload["runs"][0]["run_id"] == "run-list-1"

        with patch("threat_modeler.server.api.cancel_run", return_value=True):
            code, deleted = _delete_json(f"{base_url}/runs/run-list-1")
            assert code == 200
            assert deleted["cancelled"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_auth_required_rejects_non_health_without_token():
    with patch.dict(
        os.environ,
        {
            "THREAT_MODELER_AUTH_REQUIRED": "1",
            "THREAT_MODELER_AUTH_TOKEN": "s12-token",
        },
        clear=False,
    ):
        server, _ = _start_test_server()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            health_payload = _get_json(f"{base_url}/health")
            assert health_payload == {"status": "ok"}

            code, payload = _get_json_with_status(f"{base_url}/runs")
            assert code == 401
            assert payload["error"] == "Unauthorized"
        finally:
            server.shutdown()
            server.server_close()


def test_auth_required_accepts_matching_bearer_token():
    with patch.dict(
        os.environ,
        {
            "THREAT_MODELER_AUTH_REQUIRED": "1",
            "THREAT_MODELER_AUTH_TOKEN": "s12-token",
        },
        clear=False,
    ):
        server, _ = _start_test_server()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with patch("threat_modeler.server.api.get_all_run_ids", return_value=[]):
                code, payload = _get_json_with_status(
                    f"{base_url}/runs",
                    headers={"Authorization": "Bearer s12-token"},
                )
            assert code == 200
            assert payload == {"runs": []}
        finally:
            server.shutdown()
            server.server_close()


def test_auth_required_rejects_malformed_authorization_header():
    with patch.dict(
        os.environ,
        {
            "THREAT_MODELER_AUTH_REQUIRED": "1",
            "THREAT_MODELER_AUTH_TOKEN": "s12-token",
        },
        clear=False,
    ):
        server, _ = _start_test_server()
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            code, payload = _get_json_with_status(
                f"{base_url}/runs",
                headers={"Authorization": "Token s12-token"},
            )
            assert code == 401
            assert payload["error"] == "Unauthorized"
            assert "Authorization header" in payload.get("details", "")
        finally:
            server.shutdown()
            server.server_close()

