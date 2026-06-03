# Issue S12-023: Watchdog Timer Goes Stale While Execution Timeline Still Shows Stage Active

Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-023-GUI_026-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_023_Watchdog_Stale_While_Stage_Still_Active_In_Timeline.md
Verification Method: Sprint traceability verification
Status: In Review

Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

During the active run the execution timeline continued to show the report writer stage as
running (blue/active indicator) after the run had already transitioned to Completed.
Watchdog telemetry then remained stale against a stage that never received a terminal
completion transition.

This represents two overlapping defects:

1. The run transitioned to Completed before final workflow sequencing was satisfied
  (specifically before HITL Gate 9 decision flow in S12-024), creating a premature
  terminal run state.
1. The report writer stage did not receive or emit a terminal completion trigger when the
  run terminalized, so stage state remained in-progress and the timeline stayed blue.
1. Watchdog tracking remained bound to that non-terminal stage state, producing stale
  telemetry symptoms that are secondary to the missing completion transition.

## Motivation

A stale watchdog during an in-progress stage produces false-stall signals that will
mislead operators into thinking the backend has hung when it has not. Combined with a
timeline that stays blue on a completed run, the operator cannot determine whether the
stage actually completed successfully or was abandoned mid-execution.

## Affected Requirements

- GUI-026 in Requirements/10_GUI_Requirements.md
  (Run Liveness Telemetry — heartbeat age and timeout threshold must reflect actual
  stage liveness, not a fixed global timer unaware of long-running stages)
- GUI-031 in Requirements/10_GUI_Requirements.md
  (Persistent Timeline Status — timeline must transition stages to terminal state
  when the run is marked completed)
- GUI-027 in Requirements/10_GUI_Requirements.md
  (Run Diagnostics Panel — stale watchdog should surface as a diagnosable condition,
  not silently coexist with a completed run status)
- RHMI-005 in Requirements/11_React_HMI_Refactor_Requirements.md
  (Execution status and watchdog telemetry in the React HMI)

## Scope

### Run Terminalization and Stage Completion Trigger

- Ensure run completion cannot occur while report-writer stage is still non-terminal.
- Ensure stage completion is triggered by the actual report-writer completion event
  (LLM response finalized and artifact write complete).
- Ensure any forced run terminalization path also applies a deterministic terminal
  transition to all in-progress stages.
- Coordinate with S12-024 so HITL Gate 9 sequencing blocks run completion until
  an approve/reject decision is recorded.

### Timeline Stage Terminal State

- When a run transitions to Completed (or Failed), all stages must synchronously
  transition to their terminal state in the execution timeline.
- A stage that was blue (running) when the run completed must flip to green (success)
  or red (failure) — never remain blue.
- Investigate whether the timeline polling loop or the run-state projection mechanism
  is responsible for the stale indicator.

## Acceptance Criteria

- [ ] Watchdog timer does not go stale while a stage is actively making LLM calls
  and does not remain stale against stages that should have been terminalized.
- [ ] When a run is marked Completed, all timeline stages that were In Progress
      transition to their terminal state (Success or Failure) within one polling cycle.
- [ ] No stage remains blue in the timeline on a run that is in Completed or Failed state.
- [ ] Run cannot transition to Completed before Gate 9 decision flow is satisfied
  (cross-validated with S12-024).
- [ ] Report writer stage transitions to terminal state only after actual completion
  signal (LLM completion + artifact persistence), with no dangling in-progress state.
- [ ] The diagnostics panel correctly reflects the run's completed state alongside any
      watchdog telemetry without contradiction.

## Implementation Notes

- Check `src/threat_modeler/orchestrator.py` and `src/threat_modeler/backend/run_manager.py`
  for ordering between run terminalization and per-stage terminalization.
- Check report writer completion flow to ensure stage terminal state is emitted only
  after LLM completion and artifact write success.
- Ensure Gate 9 pre-completion check from S12-024 is the authoritative block on
  final run completion.
- Check `frontend/src/components/ExecutionProgress.tsx` for how stage color state is
  derived from run state and whether there is a guard for completed runs.

## Expected Primary Files

- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/orchestrator.py
- src/threat_modeler/services/openai_compatible_adapter.py
- frontend/src/components/ExecutionProgress.tsx
- frontend/src/components/ExecutionProgress.test.tsx
- Requirements/10_GUI_Requirements.md

## Validation Plan

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: run full HITL pipeline, verify run does not complete before Gate 9 decision,
  verify report-writer stage transitions to terminal only after actual completion,
  verify timeline clears and watchdog telemetry remains coherent after completion

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active pipeline run is complete.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md
