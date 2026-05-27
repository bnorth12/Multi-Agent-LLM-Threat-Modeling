"""Playwright adaptation for Sprint 12 React + MUI shell workflows."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import json
from pathlib import Path

import pytest
from urllib.request import Request, urlopen


def _wait_for_port(host: str, port: int, timeout_seconds: float = 60.0) -> None:
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _post_json(url: str, payload: dict) -> dict:
    req = Request(
        url,
        data=str.encode(json.dumps(payload)),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=10) as resp:  # nosec B310 - controlled local test URL
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


@pytest.mark.llm_live_browser
@pytest.mark.frontend_shell
def test_react_mui_shell_navigation_and_hitl_controls():
    """Validate frame navigation and HITL/top-control visibility on the React shell."""
    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        pytest.skip("Set RUN_VISIBLE_BROWSER_TESTS=1 to run frontend browser automation.")

    if shutil.which("npm") is None:
        pytest.skip("npm is required for frontend browser test.")

    npm_exec = "npm.cmd" if sys.platform.startswith("win") else "npm"

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        pytest.skip("Playwright is not installed; install with: pip install playwright")

    repo_root = Path(__file__).resolve().parents[2]
    frontend_dir = repo_root / "frontend"

    backend_port = int(os.environ.get("THREAT_MODELER_API_PORT") or _find_free_port())
    frontend_port = int(os.environ.get("THREAT_MODELER_FRONTEND_PORT") or _find_free_port())

    backend_env = dict(os.environ)
    existing_pythonpath = backend_env.get("PYTHONPATH", "")
    backend_env["PYTHONPATH"] = f"src{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "src"

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "threat_modeler", "--host", "127.0.0.1", "--port", str(backend_port)],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=backend_env,
    )

    frontend_env = dict(os.environ)
    frontend_env["VITE_API_BASE_URL"] = f"http://127.0.0.1:{backend_port}"

    frontend_proc = subprocess.Popen(
        [
            npm_exec,
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(frontend_port),
            "--strictPort",
        ],
        cwd=str(frontend_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=frontend_env,
    )

    try:
        _wait_for_port("127.0.0.1", backend_port, timeout_seconds=80.0)
        _wait_for_port("127.0.0.1", frontend_port, timeout_seconds=120.0)

        with sync_playwright() as p:
            headless = os.environ.get("THREAT_MODELER_BROWSER_HEADLESS", "1") != "0"
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{frontend_port}", wait_until="domcontentloaded")

            page.get_by_text("Threat Modeler Control Console", exact=True).wait_for(timeout=30000)
            page.get_by_role("button", name="New Run Wizard").wait_for(timeout=30000)
            assert page.get_by_role("button", name="Menu").count() == 0

            run_id = "run-s12-browser"
            _post_json(
                f"http://127.0.0.1:{backend_port}/runs",
                {
                    "run_id": run_id,
                    "run_name": "run-s12-browser",
                    "initial_state": {"raw_text": "browser shell smoke"},
                },
            )

            page.reload(wait_until="domcontentloaded")
            page.get_by_role("button", name="run-s12-browser queued").click(timeout=15000)

            page.get_by_role("tab", name="HITL GATES").wait_for(timeout=15000)
            page.get_by_role("tab", name="TOKENS").wait_for(timeout=15000)
            page.get_by_role("tab", name="Canonical Graph").wait_for(timeout=15000)
            page.get_by_text("Status:", exact=False).first.wait_for(timeout=15000)

            browser.close()
    finally:
        frontend_proc.terminate()
        backend_proc.terminate()
        try:
            frontend_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            frontend_proc.kill()
        try:
            backend_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            backend_proc.kill()


@pytest.mark.llm_live_browser
@pytest.mark.frontend_shell
def test_react_mui_shell_shows_clear_unauthorized_message_when_auth_required():
    """Validate unauthorized API responses are surfaced with a clear UI message."""
    if os.environ.get("FRONTEND_AUTH_UI_TESTS") != "1":
        pytest.skip("Set FRONTEND_AUTH_UI_TESTS=1 to run unauthorized-message browser assertion.")

    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        pytest.skip("Set RUN_VISIBLE_BROWSER_TESTS=1 to run frontend browser automation.")

    if shutil.which("npm") is None:
        pytest.skip("npm is required for frontend browser test.")

    npm_exec = "npm.cmd" if sys.platform.startswith("win") else "npm"

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        pytest.skip("Playwright is not installed; install with: pip install playwright")

    repo_root = Path(__file__).resolve().parents[2]
    frontend_dir = repo_root / "frontend"

    backend_port = int(os.environ.get("THREAT_MODELER_API_PORT") or _find_free_port())
    frontend_port = int(os.environ.get("THREAT_MODELER_FRONTEND_PORT") or _find_free_port())

    backend_env = dict(os.environ)
    existing_pythonpath = backend_env.get("PYTHONPATH", "")
    backend_env["PYTHONPATH"] = f"src{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "src"
    backend_env["THREAT_MODELER_AUTH_REQUIRED"] = "1"
    backend_env["THREAT_MODELER_AUTH_TOKEN"] = "s12-secret"

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "threat_modeler", "--host", "127.0.0.1", "--port", str(backend_port)],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=backend_env,
    )

    frontend_env = dict(os.environ)
    frontend_env["VITE_API_BASE_URL"] = f"http://127.0.0.1:{backend_port}"
    frontend_env["VITE_AUTH_TOKEN"] = "wrong-token"

    frontend_proc = subprocess.Popen(
        [
            npm_exec,
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(frontend_port),
            "--strictPort",
        ],
        cwd=str(frontend_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=frontend_env,
    )

    try:
        _wait_for_port("127.0.0.1", backend_port, timeout_seconds=80.0)
        _wait_for_port("127.0.0.1", frontend_port, timeout_seconds=120.0)

        with sync_playwright() as p:
            headless = os.environ.get("THREAT_MODELER_BROWSER_HEADLESS", "1") != "0"
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{frontend_port}", wait_until="domcontentloaded")

            page.get_by_text("Threat Modeler Control Console", exact=True).wait_for(timeout=30000)
            alert = page.get_by_role("alert").first
            alert.wait_for(timeout=30000)
            assert "Unauthorized" in alert.inner_text()

            browser.close()
    finally:
        frontend_proc.terminate()
        backend_proc.terminate()
        try:
            frontend_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            frontend_proc.kill()
        try:
            backend_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
