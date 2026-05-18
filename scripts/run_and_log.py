#!/usr/bin/env python3
"""
Test runner wrapper for consistent log and output directory handling.

- Runs any test script (Python or shell) and captures stdout/stderr to a timestamped log file.
- Organizes logs under test_reports/YYYY-MM-DD/ and by test type if specified.
- Usage:
    python scripts/run_and_log.py <script> [args...]
    # Example:
    python scripts/run_and_log.py scripts/verify_sprint_traceability.py --sprint 2026_11
"""
from __future__ import annotations

import os
import sys
import subprocess
import time
from pathlib import Path


def _load_dotenv(repo_root: Path) -> None:
    """Load repo-root .env into process environment without overriding existing values."""
    dotenv_path = repo_root / ".env"
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _required_env_for_script(script_path: Path) -> tuple[list[str], dict[str, str]]:
    """Return required and default env vars for known script categories."""
    defaults: dict[str, str] = {"PYTHONIOENCODING": "utf-8"}
    required: list[str] = []

    name = script_path.name.lower()
    if name == "live_browser_e2e_smoke.py":
        defaults["RUN_VISIBLE_BROWSER_TESTS"] = "1"
        required = ["GROK_API|GROK_API_KEY"]

    return required, defaults

if len(sys.argv) < 2:
    print("Usage: python scripts/run_and_log.py <script> [args...]")
    sys.exit(1)

script = sys.argv[1]
args = sys.argv[2:]
script_path = Path(script)

repo_root = Path(__file__).resolve().parents[1]
_load_dotenv(repo_root)

required_env, default_env = _required_env_for_script(script_path)
for key, value in default_env.items():
    os.environ.setdefault(key, value)

for req in required_env:
    if "|" in req:
        options = req.split("|")
        if not any(os.environ.get(opt, "").strip() for opt in options):
            print(
                "Missing required environment variable. Set one of: "
                f"{', '.join(options)}\n"
                "Tip: place it in a local .env file or export in your shell before running tests."
            )
            sys.exit(2)
    elif not os.environ.get(req, "").strip():
        print(
            f"Missing required environment variable: {req}\n"
            "Tip: place it in a local .env file or export in your shell before running tests."
        )
        sys.exit(2)

# Directory structure: test_reports/YYYY-MM-DD/[test_type]/
date_str = time.strftime("%Y-%m-%d")
test_type = Path(script).stem.replace("test_", "").replace("verify_", "")
log_dir = Path("test_reports") / date_str / test_type
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"{Path(script).stem}_{date_str}.log"

with log_file.open("w", encoding="utf-8") as f:
    proc = subprocess.Popen(
        [sys.executable, script, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ.copy(),
    )
    for line in proc.stdout:
        print(line, end="")
        f.write(line)
    proc.wait()
    sys.exit(proc.returncode)
