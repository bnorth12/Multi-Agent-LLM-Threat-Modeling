# D-S09-016: HITL Gate Not Displayed in Threat Review UI Despite Pipeline Paused

## Issue Summary

During live LLM run with all 9 stages and HITL gates required, the pipeline correctly paused at gate_1_scope_confirmation. However, the Threat Review screen shows "No HITL gates recorded for this run", preventing the user from approving/rejecting the gate through the UI.

The Home Dashboard correctly shows the run is PAUSED at gate_1_scope_confirmation, but the gate data is not populated in the Threat Review HITL Gate Review section.

## Related Requirements

- GUI-002
- HITL-001
- GUI-002A

## Severity

**Critical** - blocks user from resuming pipeline execution after HITL pause; no UI path exists to approve/reject gate.

## Reproduction

1. Configure pipeline with all 9 stages enabled and HITL gates required.
1. Use live LLM provider (xAI/Grok).
1. Start threat model run with minimal system architecture.
1. Wait for run to reach Gate 1 (Scope Confirmation) - typically after stages 01-02 complete (~2-3 min).
1. Observe Home Dashboard shows status: 🟠 PAUSED at gate_1_scope_confirmation.
1. Open Threat Review screen.
1. Observe HITL Gate Review section shows "No HITL gates recorded for this run."
1. No gate approval/rejection buttons are visible.

## Expected Behavior

When pipeline is paused at a HITL gate:

- HITL Gate Review section SHALL display the paused gate with its metadata.
- Gate artifact data (scope confirmation, review context) SHALL be visible.
- Approve/Reject/Edit action buttons SHALL be present and functional.
- User SHALL be able to submit a gate decision to resume execution.

## Scope

1. Trace gate data population path from backend run registry to Threat Review screen.
1. Identify why gate data is not being queried or rendered in HITL Gate Review section.
1. Implement gate-present state UI rendering with gate metadata and action controls.
1. Test gate visibility and interactivity for all defined HITL gates in pipeline.

## Acceptance Criteria

- [ ] HITL gates are visible in Threat Review when pipeline is paused.
- [ ] Gate metadata (gate ID, type, status) is displayed.
- [ ] Gate artifact preview or summary is shown for analyst context.
- [ ] Approve, Reject, Edit, and Resume buttons are present and functional.
- [ ] Gate decision submission resumes pipeline execution to next stage.
- [ ] Test coverage includes all 9-stage run path with all gates.

## Status

Deferred

## Deferral Rationale (2026-05-10)

- Critical blocker discovered during live automated run test.
- Requires investigation into gate data flow and UI state sync.
- Deferred for immediate fix in next implementation slice to unblock HITL workflow.
- This issue prevents completion of full 9-stage run and all HITL gate transitions.
