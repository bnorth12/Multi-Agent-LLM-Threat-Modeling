"""Application entry point.

Start the full Threat Modeler application with::

    python -m threat_modeler

This launches the Streamlit web server so the UI is immediately accessible in
a browser.  The Streamlit server runs the ``ui/app.py`` shell, which in turn
renders all screens and polls the Streamlit-free backend
(``backend/run_manager.py``) for pipeline execution state.

The ``--server.headless true`` flag suppresses the automatic browser launch
that Streamlit performs in interactive mode; remove it if you prefer the
browser to open automatically.

Usage
-----
::

    # Default: headless, port 8501
    python -m threat_modeler

    # Custom port
    python -m threat_modeler --port 9000

    # With auto-browser
    python -m threat_modeler --open-browser
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m threat_modeler",
        description="Multi-Agent LLM Threat Modeler — starts the Streamlit web server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for the Streamlit server (default: 8501).",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=False,
        help="Open a browser tab automatically when the server starts.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    app_path = Path(__file__).parent / "ui" / "app.py"
    if not app_path.exists():
        print(f"[threat_modeler] ERROR: UI entry point not found: {app_path}", file=sys.stderr)
        sys.exit(1)

    headless = "false" if args.open_browser else "true"

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(args.port),
        "--server.headless",
        headless,
    ]

    print(f"[threat_modeler] Starting web server on http://localhost:{args.port}")
    print(f"[threat_modeler] Command: {' '.join(cmd)}")

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("\n[threat_modeler] Shutdown requested.")
        sys.exit(0)


if __name__ == "__main__":
    main()
