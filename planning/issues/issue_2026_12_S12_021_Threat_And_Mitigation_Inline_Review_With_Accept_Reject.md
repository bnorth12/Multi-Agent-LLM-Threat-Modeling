# Issue S12-021: Inline Threat and Mitigation Review with Per-Item Accept/Reject and Non-Blocking Default
Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-021-UNKNOWN_REQ-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_021_Threat_And_Mitigation_Inline_Review_With_Accept_Reject.md
Verification Method: Sprint traceability verification
Status: In Review


Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

The Threat viewer currently does not open a detail dialog on click, does not surface
per-threat mitigations inline when they are generated, and does not provide per-item
accept/reject decisions for threats or mitigations.

This issue delivers:
1. Threat detail dialog on click, showing threat fields and — once the mitigation stage
   has run — the mitigations generated for that threat inline.
2. Per-threat and per-mitigation accept/reject/pending decision controls.
3. Non-blocking default: pending items are treated as accepted so that the diagram generator
   and report generator always have a complete working set on first pass even with no user input.
4. Downstream filtering: only accepted threats (and their accepted mitigations) are passed
   to the diagram and report generation stages.

## Motivation

- Without inline mitigations the analyst must cross-reference a separate artifact to validate
  mitigation adequacy against the originating threat.
- Without per-item decisions individual mitigations and threats cannot be excluded from
  downstream output without full gate reject.
- The pending-as-accepted default ensures the pipeline never blocks on user inaction while
  still giving the analyst explicit control when they want it.

## Affected Requirements

- GUI-005 in Requirements/10_GUI_Requirements.md
  (Threat Artifact Review Screen — must be extended to include mitigation inline population
  and per-item decision controls)
- HITL-004 in Requirements/03_HITL_Requirements.md
  (Threat Plausibility Gate — per-item accept/reject at the threat level extends gate resolution)
- HITL-005 in Requirements/03_HITL_Requirements.md
  (Mitigation Adequacy Gate — per-item accept/reject at the mitigation level extends gate resolution)
- HITL-007 in Requirements/03_HITL_Requirements.md
  (Override Rationale Capture — optional rationale for reject decisions)
- HITL-008 in Requirements/03_HITL_Requirements.md
  (Signed Decision Records — per-item decisions must be recorded in run records)
- New requirements needed for GUI-005 extensions and per-item decision API contract
  (pending new ID assignment during implementation sprint)

## Scope

### Part 1 — Threat Detail Dialog and Inline Mitigations

- Clicking any threat row in the Threat viewer opens a detail dialog (or expand-in-place panel).
- Dialog shows all threat fields: ID, name, STRIDE category, score, rationale, affected
  components, data flows.
- When the mitigation stage has completed, the dialog also renders the list of mitigations
  mapped to that threat with full mitigation fields (ID, name, description, control type,
  implementation guidance).
- Mitigations appear with a status chip: Pending, Accepted, Rejected.

### Part 2 — Per-Threat and Per-Mitigation Accept/Reject Controls

- Threat viewer table shows per-row status chip (Pending / Accepted / Rejected) and
  inline Approve/Reject buttons.
- Threat detail dialog shows per-mitigation Approve/Reject buttons.
- Reject action prompts for optional rationale text (consistent with HITL-007).
- All decisions are persisted in run state as signed decision records (consistent with HITL-008).
- Bulk-accept and bulk-reject actions for the full threat or mitigation list are out of scope
  for this issue unless separately scoped.

### Part 3 — Pending-as-Accepted Default and Downstream Filtering

- Any threat with status Pending is treated as Accepted for the purposes of passing to
  diagram and report stages.
- Any mitigation with status Pending is treated as Accepted for the purposes of passing to
  diagram and report stages.
- Explicitly Rejected threats are excluded from diagram and report input.
- Explicitly Rejected mitigations are excluded from diagram and report input.
- The pipeline never blocks waiting for per-item decisions.

## Acceptance Criteria

### Threat Viewer and Dialog

- [ ] Clicking a threat row opens a detail dialog or expanded inline panel.
- [ ] Dialog shows all threat fields.
- [ ] After the mitigation stage completes, the dialog populates with the mitigations mapped to
      that threat.
- [ ] Mitigations in the dialog show status chip: Pending, Accepted, or Rejected.
- [ ] Closing and reopening the dialog preserves the current per-item decision state.

### Per-Item Decision Controls

- [ ] Threat table shows per-row status chip and Approve/Reject buttons.
- [ ] Reject action offers an optional rationale text field before confirming.
- [ ] Per-item decisions are persisted in run state and survive page navigation.
- [ ] Per-item decisions are reflected in the HITL audit record for the run.

### Pending-as-Accepted Default and Downstream Filtering

- [ ] Diagram and report stages receive all threats and mitigations that are Accepted
      or Pending (non-blocking).
- [ ] Diagram and report stages exclude only explicitly Rejected items.
- [ ] Behavior is identical when no per-item decisions have been made (full pass-through).
- [ ] Snapshot export captures the decision state for all items.

## Implementation Notes

- The backend needs a per-item decision store keyed by run_id → threat_id / mitigation_id.
- The API needs endpoints (or a run-state field) to read and write per-item decisions.
- The orchestrator's output assembly for diagram/report generation needs to filter by
  effective acceptance state before passing context to those agents.
- Consider whether per-item decisions replace or complement the existing HITL-004/005 gate
  flow (most likely they are complementary: the gate confirms overall readiness, per-item
  decisions are the specific selections made during that review).

## Expected Primary Files

- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/ThreatReviewer.tsx (new or refactored from existing)
- frontend/src/components/ArtifactsViewer.test.tsx
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- src/threat_modeler/orchestrator.py (or agent output assembly layer)
- Requirements/10_GUI_Requirements.md
- Requirements/03_HITL_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md

## Validation Plan

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- manual: run a full pipeline, click a threat, verify mitigation inline population,
  reject one mitigation, confirm excluded from diagram/report, confirm snapshot captures
  decision state

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



