#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SPRINT="${1:-2026_12}"
POLICY_PROFILE="${2:-}"

if [ -x "$ROOT_DIR/.venv/Scripts/python.exe" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/Scripts/python.exe"
elif [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python"
fi

if [ -n "$POLICY_PROFILE" ]; then
  "$PYTHON_BIN" scripts/governance_autoflow.py --context closeout --sprint "$SPRINT" --policy-profile "$POLICY_PROFILE"
else
  "$PYTHON_BIN" scripts/governance_autoflow.py --context closeout --sprint "$SPRINT"
fi
