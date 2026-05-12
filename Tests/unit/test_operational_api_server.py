"""Unit tests for non-Streamlit operational API server."""

from __future__ import annotations

import json
import threading
import urllib.request
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

