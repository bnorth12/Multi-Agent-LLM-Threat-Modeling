#!/bin/bash
#
# Git Pre-Commit Hook Setup
#
# Installs a pre-commit hook that warns developers if commit message
# lacks an issue reference before committing locally.
#
# This is OPTIONAL but recommended for catching traceability issues early.
#
# Usage:
#   bash scripts/setup-git-hooks.sh
#
# After setup:
#   - Every `git commit` will check message format
#   - If issue ID missing, you'll get a warning
#   - You can bypass with: git commit --no-verify
#

set -e

HOOK_DIR=".git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

echo "🔧 Setting up Git pre-commit hook..."

# Create hooks directory if it doesn't exist
if [ ! -d "$HOOK_DIR" ]; then
    mkdir -p "$HOOK_DIR"
    echo "  📁 Created $HOOK_DIR directory"
fi

# Create pre-commit hook
cat > "$HOOK_FILE" << 'EOF'
#!/bin/bash
#
# Pre-commit hook for sprint traceability verification
#
# This hook checks that commit messages reference an issue ID before allowing commit.
# Issue ID formats supported:
#   - D-S08-020 (defect)
#   - HITL-012 (requirement)
#   - PRJ-008, INT-015, GUI-003A (other requirements)
#   - GH #123 (GitHub issue number)
#
# If issue ID is missing, the hook will:
#   - ❌ WARN (yellow): Show missing issue ID
#   - Allow you to continue if you use: git commit --no-verify
#
# Exit codes:
#   0 = OK, continue commit
#   1 = WARN, but allow (for backward compatibility)
#

# Get the commit message from the temporary file created by git
COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Patterns to match issue IDs:
# D-S08-020, D-S09-001, etc. (defects)
# HITL-012, HITL-013, etc. (requirements)
# PRJ-008, INT-015, GUI-003A, etc. (other requirements)
# GH #123, issue #456 (GitHub issues)

ISSUE_PATTERN='(D-S|HITL|PRJ|INT|GUI|SCR)-[0-9]+[A-Z]?|GH\s*#[0-9]+|issue\s*#[0-9]+'

if grep -qEi "$ISSUE_PATTERN" "$COMMIT_MSG_FILE"; then
    # Issue ID found - commit is OK
    exit 0
else
    # Issue ID not found - warn but allow (exit 1 means fail, but we want warning only)
    echo ""
    echo "⚠️  WARNING: Commit message does not reference an issue ID"
    echo ""
    echo "Suggested fix: Include issue ID in your commit message"
    echo ""
    echo "Examples of good commit messages:"
    echo "  - Fix D-S08-020: Add trigger_reason field to HitlGateRecord"
    echo "  - Implements HITL-012: Track conditional gate trigger state"
    echo "  - Refs: GH #456"
    echo ""
    echo "Current commit message:"
    echo "  $COMMIT_MSG"
    echo ""
    echo "You can:"
    echo "  1. Exit and fix: ^C (Ctrl+C)"
    echo "  2. Continue anyway: git commit --no-verify"
    echo ""

    # Return 0 to allow commit (warning only, not blocking)
    # If you want to block commits without issue IDs, change this to: exit 1
    exit 0
fi
EOF

# Make hook executable
chmod +x "$HOOK_FILE"
echo "  ✅ Hook installed at $HOOK_FILE"

echo ""
echo "✅ Pre-commit hook setup complete!"
echo ""
echo "What this hook does:"
echo "  - On each 'git commit', checks if message references an issue ID"
echo "  - Issue ID formats: D-S08-020, HITL-012, PRJ-008, GH #123, etc."
echo "  - If missing, shows a warning (non-blocking)"
echo ""
echo "Usage:"
echo "  - Normal commits: 'git commit -m \"Implements HITL-012: ...\"' ✅"
echo "  - Skip check: 'git commit --no-verify' (not recommended)"
echo ""
echo "To uninstall:"
echo "  rm $HOOK_FILE"
echo ""
