# D-S09-012: Live Validation Test API Mismatch

## Issue Summary

The live validation test suite (`Tests/e2e/test_live_llm_validation.py`) was written against an outdated orchestrator and settings API. It references a nonexistent `RuntimeSettings.provider` property, instantiates `FrameworkOrchestrator` with obsolete `system_name` and `architecture_text` arguments, and attempts to mutate frozen dataclass fields directly.

## Related Requirements

- GUI-016
- GUI-015
- PRJ-021, PRJ-022

## Severity

Medium - Blocks automated live validation coverage and prevents a clean end-to-end automation sweep.

## Scope

1. Update live validation tests to use the current `FrameworkOrchestrator(settings=..., run_id=...)` API.
1. Build explicit live-mode `RuntimeSettings` objects instead of assuming `build_default_settings()` returns live settings.
1. Hook the live adapter from the current agent registry rather than a nonexistent top-level orchestrator adapter.
1. Replace direct mutation of frozen dataclass fields with explicit construction or dataclass replacement.

## Acceptance Criteria

- [x] Live validation tests instantiate the current orchestrator successfully.
- [x] Live settings are created explicitly with live provider configuration.
- [x] Live adapter interception works through the shared agent adapter.
- [x] Timeout/retry validation uses immutable-safe settings updates.
- [x] Live validation suite runs cleanly when the live provider is available.

## Status

Resolved

## Implementation Notes (2026-05-10)

The test suite was updated to match the current runtime API and live provider configuration model. This issue documents the compatibility mismatch and its fix.

### Verification Evidence

- `pytest Tests/e2e/test_live_llm_validation.py -m llm_live -v --tb=short`
- Result: 5 passed in 1735.26s (28:55)
