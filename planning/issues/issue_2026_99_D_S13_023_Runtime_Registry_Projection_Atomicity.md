# Issue D-S13-023: Runtime Registry Projection Atomicity

## Issue Summary

Code review identified a race-risk in backend state projection:

- `get_run_status` returns a shallow copy of `_RUN_REGISTRY` entries.
- The copied entry still holds references to mutable `FrameworkState` objects (`live_state`, `result_state`).
- API serialization then reads nested mutable fields while background execution threads may still mutate them.

This can produce non-atomic projections where status, pause metadata, and nested gate state are not read from a consistent snapshot.

## Related Requirements

- RIC-005
- PRJ-003
- HITL-012

## Severity

High - can yield inconsistent API projections and false operator conclusions under concurrent execution.

## Evidence

- `src/threat_modeler/backend/run_manager.py`: `get_run_status` shallow-copies registry entries.
- `src/threat_modeler/server/api.py`: `_serialize_run_entry` and `_resolve_run_state` consume nested state references derived from that copied entry.
- Live run evidence (2026-05-22, run_id `2ba76d34-6930-4e4f-8314-13ccf95b5a00`):
  - Gate 1 entered pause state before complete payload fields were visible in UI.
  - Gate 2 initially showed partial gate data, then metadata and system information appeared after delay.
  - Observed delay window was approximately 5-20 seconds before payload completeness.

## Implemented Scope

1. Introduce atomic projection snapshot helper for run status and required state fields.
1. Ensure API projection reads from immutable or lock-protected snapshots.
1. Add regression tests for consistency of status plus gate payload publication under concurrent updates.

## Acceptance Criteria

- [ ] API projection reads status and gate payload from a consistent snapshot boundary.
- [ ] Concurrent run execution cannot produce mixed transition bundles in `/runs` and `/state/full` responses.
- [ ] Regression tests cover concurrent updates and projection consistency.

## Verification

- `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit/test_run_manager.py Tests/test_hmi_backend_api.py -q`
- Concurrent stress probe that polls `/runs` and `/state/full` while a run transitions through queued -> running -> paused.
- Add timed capture that compares first paused snapshot timestamp vs first complete payload timestamp per gate.

## Status

Open
