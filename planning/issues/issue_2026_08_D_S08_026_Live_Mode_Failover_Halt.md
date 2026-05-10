# D-S08-026: Live Mode Failover to Fixture Must Halt Execution

## Issue Summary

When a run is configured for live LLM mode, any fallback to offline fixture/static adapter behavior SHALL be treated as a runtime integrity failure. Execution must halt immediately with explicit error state and operator-visible failure reason.

## Related Requirements

- PRJ-020: Live-Mode Integrity Halt on Provider Degradation
- GUI-017: Live Mode Failover Hard-Stop Indicator and Halt
- PRJ-015: Fail-safe halting behavior

## Severity

High - Silent degradation from live LLM to fixture mode invalidates verification and can mask production errors.

## Acceptance Criteria

- [x] Runtime detects fixture adapter usage when run settings indicate live provider mode.
- [x] Detection triggers FAILED run status and terminates further stage execution.
- [x] Error message includes stage id, expected provider mode, and detected fallback mode.
- [x] HMI displays hard-stop failure status on Home and relevant review screens.
- [x] Tests assert hard failure when live run degrades to fixture adapter path.
- [x] No silent fallback path remains in live mode execution code.

## Implementation Scope

### Code Changes

- Add guardrails in startup and stage execution path to prevent build_default_settings fixture substitution in live-intent runs.
- Add runtime adapter-mode assertions before each stage LLM call.
- Add explicit run failure handling and operator message when fallback is detected.

### Verification

- Configure live provider, forcibly remove/clear runtime settings before stage execution, confirm run halts as FAILED.
- Validate that explicit fixture mode still runs normally when selected intentionally.

### Verification Evidence

Command:

```powershell
& .venv\Scripts\python.exe -m pytest Tests/unit/test_live_mode_failover_halt.py -q --tb=short
```

Result:

- 2 passed in 11.23s
- `test_live_mode_missing_adapter_halts_pipeline`: verifies stage-level halt with explicit fallback-prevention error text and no progression to `agent_02`.
- `test_execution_manager_marks_failed_on_live_degradation`: verifies execution manager transitions to `FAILED` and surfaces hard-stop error details to session state for UI rendering.

## Notes

- This issue governs the quality gate for live-evidence test suites.

---

Status: Resolved
Assigned: Engineering
Sprint: 2026-08

Resolution Date: 2026-05-08
Resolution Notes: 2026-05-08 BN - Added D-S08-026 regression tests and verified fail-closed behavior for live-intent adapter degradation.
