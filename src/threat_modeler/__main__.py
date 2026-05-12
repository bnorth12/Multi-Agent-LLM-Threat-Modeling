"""Operational entry point for the Threat Modeler runtime.

Usage:
    python -m threat_modeler
    python -m threat_modeler --host 0.0.0.0 --port 9000

This command launches the non-Streamlit operational API server.
"""

from __future__ import annotations

import argparse
from threat_modeler.server.api import start_server


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m threat_modeler",
        description="Multi-Agent LLM Threat Modeler — starts the operational API server.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Bind host for the operational API server (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8600,
        help="Port for the operational API server (default: 8600).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
