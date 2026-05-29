#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

HOOKS_PATH=".githooks"

if [ ! -d "$HOOKS_PATH" ]; then
    echo "Missing $HOOKS_PATH directory"
    exit 1
fi

git config --local core.hooksPath "$HOOKS_PATH"

echo "Git hooks path configured: $HOOKS_PATH"
echo "Installed hooks:"
find "$HOOKS_PATH" -maxdepth 1 -type f -printf ' - %f\n'
echo ""
echo "Hook install complete."
echo "Pre-commit and pre-merge-commit now run archive hygiene checks."
echo "Pre-push now runs unit tests, sprint traceability, archive hygiene,"
echo "cross-domain exception policy validation, and independent local review."
echo ""
echo "Env toggles:"
echo " - TRACEABILITY_ENFORCE=1 makes traceability check blocking"
echo " - ARCHIVE_HYGIENE_ENFORCE=0 makes archive hygiene check warning-only on pre-push"
echo " - EXCEPTION_POLICY_ENFORCE=0 makes exception policy check warning-only"
echo " - INDEPENDENT_REVIEW_SPRINT=YYYY_MM selects review sprint (default 2026_12)"
echo " - INDEPENDENT_REVIEW_PROFILE manually overrides profile selection (options: strict/default/advisory)"
echo "   If unset, hooks auto-select strict on main/release/* and default otherwise"
echo " - INDEPENDENT_REVIEW_HOOK_FAIL_MODE=warn downgrades profile blocking to warning-only"
