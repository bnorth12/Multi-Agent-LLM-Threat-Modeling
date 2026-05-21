"""Full workflow Playwright lane for React + MUI frontend."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


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


@pytest.mark.llm_live_browser
@pytest.mark.frontend_full
def test_react_mui_full_workflow_page_actions():
    """Validate the full React shell workflow actions end-to-end."""
    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        pytest.skip("Set RUN_VISIBLE_BROWSER_TESTS=1 to run frontend browser automation.")

    if shutil.which("npm") is None:
        pytest.skip("npm is required for frontend browser test.")

    if os.environ.get("FRONTEND_FULL_BROWSER_TESTS") != "1":
        pytest.skip(
            "Set FRONTEND_FULL_BROWSER_TESTS=1 to run full workflow assertions in browser lane."
        )

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

            run_id = "run-s12-full-workflow"

            page.get_by_role("button", name="Runs").click(timeout=10000)
            page.get_by_label("Run ID").first.fill(run_id)
            page.get_by_role("button", name="Submit Run").click(timeout=10000)
            page.get_by_text(run_id).first.wait_for(timeout=15000)

            page.get_by_role("button", name="Prompt Control").click(timeout=10000)
            page.get_by_label("Prompt Text").fill("S12 full workflow prompt update")
            page.get_by_role("button", name="Save Prompt").click(timeout=10000)
            page.get_by_text("S12 full workflow prompt update").first.wait_for(timeout=15000)

            page.get_by_role("button", name="Configuration").click(timeout=10000)
            page.get_by_label("Provider").fill("fixture")
            page.get_by_label("Model Name").fill("fixture-s12-full")
            page.get_by_role("button", name="Save Config").click(timeout=10000)
            page.get_by_text("fixture-s12-full").first.wait_for(timeout=15000)

            page.get_by_role("button", name="Artifacts").click(timeout=10000)
            page.get_by_label("Run ID").first.fill(run_id)
            page.get_by_role("button", name="Load").click(timeout=10000)
            page.get_by_role("heading", name="Artifacts").wait_for(timeout=10000)

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
