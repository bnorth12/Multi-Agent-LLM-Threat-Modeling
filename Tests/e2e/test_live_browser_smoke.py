"""Live browser E2E smoke wrapper.

This test intentionally delegates execution to a standalone script so
application startup/execution is not coupled to pytest internals.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.llm_live_browser
@pytest.mark.llm_live
def test_live_browser_end_to_end_smoke_script() -> None:
    """Run standalone live-browser smoke and assert full functional threat flow."""
    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        pytest.skip("Set RUN_VISIBLE_BROWSER_TESTS=1 to run visible-browser automation.")

    if not os.environ.get("GROK_API", "").strip():
        pytest.skip("Set GROK_API to run live-browser end-to-end smoke.")

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "live_browser_e2e_smoke.py"
    assert script_path.exists(), f"Missing smoke script: {script_path}"

    cmd = [sys.executable, str(script_path)]
    timeout_seconds = None if os.environ.get("THREAT_MODELER_SMOKE_KEEP_OPEN_UNTIL_INPUT") == "1" else 1800
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        pytest.fail(
            "Standalone smoke script failed.\n"
            f"Exit code: {proc.returncode}\n"
            "Output tail:\n"
            f"{output[-6000:]}"
        )

    assert "LIVE_BROWSER_SMOKE_OK" in output, (
        "Smoke success marker missing from standalone script output.\n"
        f"Output tail:\n{output[-6000:]}"
    )
