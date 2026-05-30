#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SPRINT_DEFAULTS_FILE="$REPO_ROOT/config/sprint_defaults.env"
if [ -f "$SPRINT_DEFAULTS_FILE" ]; then
  # shellcheck disable=SC1090
  . "$SPRINT_DEFAULTS_FILE"
fi
DEFAULT_SPRINT="${DEFAULT_SPRINT:-2026_013}"

SPRINT="${1:-${INDEPENDENT_REVIEW_SPRINT:-$DEFAULT_SPRINT}}"
POLICY_PROFILE="${2:-}"

PYTHON_BIN="$REPO_ROOT/.venv/Scripts/python.exe"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

ARGS=(
  "scripts/governance_autoflow.py"
  "--context" "blocker-planning"
  "--sprint" "$SPRINT"
)

if [[ -n "$POLICY_PROFILE" ]]; then
  ARGS+=("--policy-profile" "$POLICY_PROFILE")
fi

"$PYTHON_BIN" "${ARGS[@]}"
