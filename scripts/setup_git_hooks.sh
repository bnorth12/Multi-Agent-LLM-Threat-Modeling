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
echo "Pre-commit and pre-merge-commit now run archive hygiene checks and governance autoflow."
echo "Pre-push now runs unit tests, sprint traceability, archive hygiene,"
echo "cross-domain exception policy validation, and governance autoflow."
echo "Governance routing is loaded from config/governance_autoflow_routing.json."
echo "Governance execution ledger is written under independent_reviews/latest and independent_reviews/history."
echo ""
echo "Env toggles:"
echo " - TRACEABILITY_ENFORCE=1 makes traceability check blocking"
echo " - ARCHIVE_HYGIENE_ENFORCE=0 makes archive hygiene check warning-only on pre-push"
echo " - EXCEPTION_POLICY_ENFORCE=0 makes exception policy check warning-only"
echo " - INDEPENDENT_REVIEW_SPRINT accepts YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN (default 2026_12)"
echo " - INDEPENDENT_REVIEW_PROFILE manually overrides profile selection (options: strict/default/advisory)"
echo "   If unset, hooks auto-select strict on main/release/* and default otherwise"
echo " - INDEPENDENT_REVIEW_HOOK_FAIL_MODE=warn downgrades profile blocking to warning-only"
echo ""
echo "Operator commands:"
echo " - ./scripts/run_governance_planning.sh 2026_12"
echo " - ./scripts/run_governance_closeout.sh 2026_12"
