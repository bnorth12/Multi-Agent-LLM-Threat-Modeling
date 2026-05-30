# Issue D-S13-022: Runtime State and Gate Contract Corrections

Status: Reopened (Regression Confirmed)
Priority: P1
Sprint: 2026-99
Date Opened: 2026-05-22
Date Resolved: 2026-05-22
Date Reopened: 2026-05-22

## Summary

This issue consolidates four coupled defects that produced misleading execution behavior and governance risk:

1. Gate 0 could open before preflight integrity data was ready.
1. User cancellation from paused runs did not move to a terminal cancelled state.
1. UI status overlays could continue to display paused semantics after cancellation.
1. Governance artifacts lacked explicit requirement/issue documentation for input parsing parity and prompt expected-output/schema drift controls.

## Root Cause

- Gate trigger sequencing relied on state snapshots that were not guaranteed ready at trigger time.
- Cancellation semantics treated paused cancellation as non-terminal or failure-adjacent behavior instead of a dedicated terminal status.
- Frontend status derivation allowed stale pause metadata to override terminal status messaging.
- Requirements and issue artifacts were not yet updated to cover these defects as a single traceable package.

## Regression Update (2026-05-22)

- Live validation confirmed Gate 0 still pauses before preflight payload is consistently available to operators.
- The previous Gate 0 readiness changes reduced failures but did not eliminate a pause-versus-payload publication race.
- Timing probe evidence shows `status=paused` appears first and `artifact_snapshot.input_preflight.raw_text_preview` becomes visible later.
- This issue remains open until Gate 0 trigger/publish ordering enforces data-ready-before-pause behavior end-to-end.

## Affected Requirements

- RIC-001 through RIC-004 in Requirements/13_Runtime_State_And_Input_Contract_Requirements.md
- HITL-009 in Requirements/03_HITL_Requirements.md
- GUI-031 in Requirements/10_GUI_Requirements.md
- RHMI-005 and RHMI-017 in Requirements/11_React_HMI_Refactor_Requirements.md

## Resolution Implemented

### Backend and Orchestrator

- Added Gate 0 readiness guards before local trigger open to ensure preflight data exists and is complete enough for review.
- Added terminal CANCELLED execution status to run lifecycle semantics.
- Updated cancel behavior to allow paused-run cancellation and clear pause metadata.

### API Projection

- Adjusted run serialization so paused metadata is emitted only when run status is actually paused.

### Frontend

- Updated status derivation to prioritize terminal cancelled state over stale paused gate overlays.
- Restricted pause overlay logic to active execution states.
- Updated timeline status text to display cancelled-by-user semantics.

### Tests

- Added/updated backend unit tests for Gate 0 readiness and cancellation semantics.
- Added frontend regression test for cancelled status precedence when stale gate metadata exists.

## Files Touched

- src/threat_modeler/orchestrator.py
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- frontend/src/App.tsx
- Tests/unit/test_framework_orchestrator_langgraph.py
- Tests/unit/test_run_manager.py
- frontend/src/App.test.tsx

## Verification Evidence

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit/test_run_manager.py Tests/unit/test_framework_orchestrator_langgraph.py -q
- cd frontend; npm run test -- --run src/App.test.tsx --reporter=dot

### Additional Regression Evidence (2026-05-22)

- API timing probe against `/runs`, `/runs/{run_id}/state/gates`, and `/runs/{run_id}/state/full` confirmed race behavior:

1. `status=paused` and `pause_gate=gate_0_input_integrity` observed at approximately 200-300 ms after run submission.
1. Gate 0 `artifact_snapshot.input_preflight` and non-empty `raw_text_preview` observed later, around approximately 1000 ms.

- Operator report corroborated delayed Gate 0 data appearance in live UI.

## Current Disposition

- Cancel semantics and terminal cancelled UI precedence remain validated.
- Gate 0 race condition is not fully resolved; final closure is blocked pending a backend trigger/publish ordering fix and re-validation.
- Prompt/schema drift and input parsing parity remain tracked under RIC-003 and RIC-004.
