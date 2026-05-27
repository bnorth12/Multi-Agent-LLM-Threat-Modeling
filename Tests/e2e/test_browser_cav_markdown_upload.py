"""Browser automation for CAV fixture upload workflow on Input Entry."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


def _wait_for_port(host: str, port: int, timeout_seconds: float = 45.0) -> None:
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


@pytest.mark.llm_live_browser
def test_visible_browser_uploads_cav_and_markdown_files():
    """Validate CAV fixture and markdown files can be loaded from UI uploader."""
    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        pytest.skip("Set RUN_VISIBLE_BROWSER_TESTS=1 to run visible-browser automation.")

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        pytest.skip("Playwright is not installed; install with: pip install playwright")

    repo_root = Path(__file__).resolve().parents[2]
    app_path = repo_root / "src" / "threat_modeler" / "ui" / "app.py"
    icd_path = repo_root / "Tests" / "fixtures" / "inputs" / "systems" / "charlie" / "icd_charlie_v1.xlsx"
    cav_md_path = repo_root / "Tests" / "fixtures" / "inputs" / "systems" / "cav" / "description_cav.md"
    avionics_md_path = repo_root / "Tests" / "fixtures" / "inputs" / "systems" / "avionics" / "description_avionics.md"

    assert icd_path.exists()
    assert cav_md_path.exists()
    assert avionics_md_path.exists()

    port = int(os.environ.get("THREAT_MODELER_BROWSER_TEST_PORT", "8511"))
    app_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_port("127.0.0.1", port, timeout_seconds=60.0)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}", wait_until="domcontentloaded")

            # Ensure we are on the Input Entry screen before interacting with form fields.
            sidebar = page.locator("[data-testid='stSidebar']")
            sidebar.wait_for(state="visible", timeout=30000)
            try:
                input_entry_label = sidebar.locator(
                    "[data-testid='stRadio'] label:not([data-testid='stWidgetLabel']):has-text('Input Entry')"
                ).first
                input_entry_label.wait_for(state="visible", timeout=30000)
                input_entry_label.click(timeout=30000)
            except Exception:
                sidebar.get_by_text("Input Entry", exact=True).first.click(timeout=30000)
            page.get_by_role("heading", name="Input Entry Form").wait_for(timeout=30000)

            page.get_by_role("textbox", name="System name").fill(
                "CAV Browser Live Validation",
                timeout=30000,
            )
            page.locator("input[type='file']").set_input_files(
                [
                    str(icd_path),
                    str(cav_md_path),
                    str(avionics_md_path),
                ]
            )

            page.get_by_text("icd_charlie_v1.xlsx").wait_for(timeout=15000)
            page.get_by_text("description_cav.md").wait_for(timeout=15000)
            page.get_by_text("description_avionics.md").wait_for(timeout=15000)
            browser.close()
    finally:
        app_proc.terminate()
        try:
            app_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            app_proc.kill()
