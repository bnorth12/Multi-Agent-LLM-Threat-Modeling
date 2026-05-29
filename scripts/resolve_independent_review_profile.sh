#!/usr/bin/env bash
set -euo pipefail

# Resolves the effective independent review profile with this precedence:
# 1) explicit INDEPENDENT_REVIEW_PROFILE env override
# 2) strict on main and release/*
# 3) default on all other branches

CURRENT_BRANCH="$(git branch --show-current 2>/dev/null || true)"

if [ -n "${INDEPENDENT_REVIEW_PROFILE:-}" ]; then
  EFFECTIVE_INDEPENDENT_REVIEW_PROFILE="$INDEPENDENT_REVIEW_PROFILE"
  PROFILE_SOURCE="env override"
elif [ "$CURRENT_BRANCH" = "main" ] || [[ "$CURRENT_BRANCH" == release/* ]]; then
  EFFECTIVE_INDEPENDENT_REVIEW_PROFILE="strict"
  PROFILE_SOURCE="branch auto"
else
  EFFECTIVE_INDEPENDENT_REVIEW_PROFILE="default"
  PROFILE_SOURCE="branch auto"
fi

printf '%s\t%s\t%s\n' "$EFFECTIVE_INDEPENDENT_REVIEW_PROFILE" "$PROFILE_SOURCE" "$CURRENT_BRANCH"
