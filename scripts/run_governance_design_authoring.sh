#!/usr/bin/env bash
set -euo pipefail

SPRINT="${1:-2026_12}"
POLICY_PROFILE="${2:-}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_BIN="$REPO_ROOT/.venv/Scripts/python.exe"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

ARGS=(
  "scripts/governance_autoflow.py"
  "--context" "design-authoring"
  "--sprint" "$SPRINT"
)

if [[ -n "$POLICY_PROFILE" ]]; then
  ARGS+=("--policy-profile" "$POLICY_PROFILE")
fi

"$PYTHON_BIN" "${ARGS[@]}"
