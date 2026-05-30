# Issue S12-024: HITL Gate 9 (Final Release Gate) Not Firing Before Run Completion
Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-024-UNKNOWN_REQ-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_024_HITL_Gate_9_Final_Release_Gate_Not_Firing.md
Verification Method: Sprint traceability verification
Status: In Review


Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

During the active run the pipeline completed and the report artifact was populated without
HITL Gate 9 (the Final Release Gate defined by HITL-006) firing. The gate was expected
to pause execution between the report generator (agent_09) and the final release of output
artifacts, requiring explicit analyst approval before the run transitions to Completed.

This is a HITL compliance defect. HITL-006 is a SHALL requirement and its absence means
the run completed without an accountable approval record, which is a governance gap.

## Motivation

The Final Release Gate is the last control point before output artifacts (report, STIX)
are considered released. Without it, a run can produce and expose output artifacts without
analyst review. This violates the HITL gate contract, removes the audit record for final
approval, and means any report quality defects are not gated before release.

## Affected Requirements

- HITL-006 in Requirements/03_HITL_Requirements.md
  (Final Release Gate — SHALL provide a Final Release Gate before report and STIX
  publication; this is a hard compliance requirement)
- HITL-008 in Requirements/03_HITL_Requirements.md
  (Signed Decision Records — final gate decision must be preserved as a signed run record;
  absent gate means no signed record exists for this run)
- GUI-030 in Requirements/10_GUI_Requirements.md
  (Ordered HITL Gates Ledger — Gate 9 must appear in the ledger and must not be
  silently skipped)

### Requirement/Gate Index Drift Note

- Current implementation uses explicit gate indices (Gate 0 through Gate 9), while
  requirement identifiers use HITL-00X IDs that are not numerically aligned to gate index.
- This issue keeps the core defect scope (Gate 9 not firing) and adds a governance
  synchronization requirement: requirement text and traceability must explicitly map
  gate index to requirement ID to remove ambiguity.

## Scope

### Gate 9 Not Triggering

- Investigate whether Gate 9 is defined in the gate configuration and whether the
  orchestrator is checking for it after agent_09 completes.
- Determine whether the gate is being silently bypassed due to a missing condition
  check, an exception swallowed during gate evaluation, or a misconfigured gate index.
- Investigate whether the run_manager is emitting the gate_pending event for Gate 9
  and whether the frontend is listening for it.

### Gate 9 Not Blocking Completion

- Even if the gate fires, verify that the orchestrator correctly blocks the run from
  transitioning to Completed until the analyst submits an approve or reject decision.
- Verify that a bypass path exists but is clearly recorded in the audit log.

### Frontend Gate Ledger

- Confirm Gate 9 appears in the HITL Gates ledger and shows its correct state
  (Pending, Approved, Rejected, Bypassed) after a run.
- A gate row for Gate 9 must never be absent from the ledger when HITL mode is active.

### Requirement and Traceability Synchronization

- Update HITL requirement wording or supporting mapping notes so the current
  implementation workflow (Gate 0..Gate 9) is explicitly synchronized with
  HITL requirement IDs.
- Add/refresh a gate mapping table that clearly states: Gate Index -> Requirement ID ->
  Gate Name -> Trigger Position.
- Ensure S12-024 references the synchronized mapping in closure evidence.
- Explicitly update the affected requirement artifacts as part of this issue:
  `Requirements/03_HITL_Requirements.md` and `Requirements/04_Traceability_Matrix.md`.
- Explicitly update this issue package after requirement edits so governance artifacts
  remain synchronized (`planning/issues/issue_2026_12_S12_024_HITL_Gate_9_Final_Release_Gate_Not_Firing.md`,
  `planning/issues/Sprint_2026_12_Issue_Tracker.md`, and
  `planning/issues/Sprint_2026_12_GitHub_Issue_Drafts.md`).

## Acceptance Criteria

- [ ] After agent_09 completes, execution pauses and Gate 9 appears as Pending in the
      HITL Gates ledger.
- [ ] The run does not transition to Completed until an Approve, Reject, or explicit
      Bypass decision is submitted for Gate 9.
- [ ] A signed decision record for Gate 9 is present in the run audit output after
      every HITL-mode run.
- [ ] Gate 9 row is present in the frontend HITL Gates ledger in all run states
      (Pending, Approved, Rejected, Bypassed).
- [ ] Reject at Gate 9 halts the run and records rationale.
- [ ] HITL requirements and traceability documents include an explicit Gate Index ->
  Requirement ID mapping that matches the current Gate 0..Gate 9 workflow.
- [ ] `Requirements/03_HITL_Requirements.md` is updated to reflect the synchronized
  gate-index-to-requirement mapping for the current implementation.
- [ ] `Requirements/04_Traceability_Matrix.md` is updated with matching mapping/
  references.
- [ ] S12-024 governance artifacts are synchronized after requirement edits (issue spec,
  sprint tracker row, and GitHub draft).

## Implementation Notes

- Check `src/threat_modeler/orchestrator.py` (or equivalent gate dispatch logic) for
  whether the gate event is emitted after agent_09 completes.
- Check `src/threat_modeler/backend/run_manager.py` for gate index ordering and
  whether gate 9 (final release) is correctly indexed and checked.
- Check `frontend/src/components/HITLGateManager.tsx` for whether Gate 9 is
  included in the rendered gate list.
- Confirm that the gate configuration in `data/models/` or equivalent includes Gate 9.
- Treat requirement ID updates as synchronization, not gate-behavior redesign:
  the implementation behavior remains anchored on Gate 9 final release semantics.

## Expected Primary Files

- src/threat_modeler/orchestrator.py (or gate dispatch layer)
- src/threat_modeler/backend/run_manager.py
- frontend/src/components/HITLGateManager.tsx
- frontend/src/components/HITLGateManager.test.tsx
- Requirements/03_HITL_Requirements.md
- Requirements/10_GUI_Requirements.md
- Requirements/04_Traceability_Matrix.md
- planning/issues/issue_2026_12_S12_024_HITL_Gate_9_Final_Release_Gate_Not_Firing.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
- planning/issues/Sprint_2026_12_GitHub_Issue_Drafts.md

## Validation Plan

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: run a full pipeline in HITL mode, confirm Gate 9 fires after agent_09 completes,
  confirm run is Paused until Gate 9 decision, confirm signed record in snapshot export

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



