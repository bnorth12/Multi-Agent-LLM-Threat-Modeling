#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SPRINT_DEFAULTS_FILE="$ROOT_DIR/config/sprint_defaults.env"
if [ -f "$SPRINT_DEFAULTS_FILE" ]; then
  # shellcheck disable=SC1090
  . "$SPRINT_DEFAULTS_FILE"
fi
DEFAULT_SPRINT="${DEFAULT_SPRINT:-2026_013}"

SPRINT="${1:-${INDEPENDENT_REVIEW_SPRINT:-$DEFAULT_SPRINT}}"
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
