# Issue S12-029: Split Threat Artifact Viewer and Threats-with-Mitigations Review Viewer
Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-029-GUI_005-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_029_Split_Threat_Artifact_Viewer_And_Threats_With_Mitigations_Review_Viewer.md
Verification Method: Sprint traceability verification
Status: In Review


Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

The current direction in S12-021 adds inline per-item threat/mitigation review controls,
but the UI still needs clearer separation between artifact browsing and analyst review workflow.

We need two distinct surfaces:

- Keep the existing Threat Artifact Viewer focused on artifact inspection.
- Add a new Threats-with-Mitigations Review Viewer focused on analyst decisions and workflow.

This separation keeps artifact rendering concerns independent from decision workflow concerns,
reduces UI coupling risk, and allows each surface to evolve independently.

## User Intent Captured

- "we likely need a separate artifact viewer for threat which currently exists, then a new
  threats with mitigations viewer so we can maintain the workflow and artifacts somewhat
  independently"

## Affected Requirements

- GUI-005 in Requirements/10_GUI_Requirements.md
  (Threat Review Screen behavior; S12-021 extends item-level controls)
- INT-008 in Requirements/02_Interface_Requirements.md
  (Visualization Read Contract for threats/mitigations data access)
- S12-021 dependency
  (Per-item accept/reject decision model is upstream of the new review viewer)
- New requirement needed: GUI-040 (or next available GUI ID) to formally define
  dual-surface behavior (Artifact Viewer vs Review Viewer) and allowed actions per surface

## Scope

### Surface 1: Threat Artifact Viewer (retain)

- Preserve the existing threat artifact browsing surface for read-focused inspection.
- No workflow-critical accept/reject controls are required on this surface beyond
  basic navigation or quick links.
- This viewer remains the canonical location for artifact representation fidelity.

### Surface 2: Threats-with-Mitigations Review Viewer (new)

- Introduce a dedicated review surface that lists threats and nested/linked mitigations.
- Provide per-item accept/reject controls inherited from S12-021 decision semantics.
- Support reviewer-focused affordances: filtering by status, sorting by risk/score,
  and batch navigation across pending items.
- Decision state changes update downstream eligibility for diagram/report inclusion
  exactly as defined by S12-021 (pending defaults to accepted; only explicit rejection excludes).

### Separation Rules

- Artifact viewer must not become the primary workflow gate-control surface.
- Review viewer must not be required to render every artifact representation mode.
- Both surfaces consume the same canonical decision state source to avoid divergence.

## Acceptance Criteria

- [ ] Existing threat artifact viewer remains available and functionally intact.
- [ ] New threats-with-mitigations review viewer is available as a distinct navigation target.
- [ ] Review viewer supports per-item accept/reject actions and status filtering.
- [ ] Decision behavior matches S12-021 semantics (pending=accepted default,
      explicit rejection excludes from downstream outputs).
- [ ] Decision state is consistent between both surfaces (single source of truth).
- [ ] UI text/tooltips clearly distinguish artifact inspection vs workflow review purposes.
- [ ] New GUI requirement (GUI-040 or equivalent) added and traceability matrix updated.

## Expected Primary Files

- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/ThreatMitigationReviewViewer.tsx (new)
- frontend/src/App.tsx
- frontend/src/components/ArtifactsViewer.test.tsx
- frontend/src/components/ThreatMitigationReviewViewer.test.tsx (new)
- Requirements/10_GUI_Requirements.md (new GUI-040 requirement)
- Requirements/04_Traceability_Matrix.md (traceability row updates)

## Validation Plan

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- frontend: npm run test -- --run src/components/ThreatMitigationReviewViewer.test.tsx
- Tests/test_hmi_backend_api.py (explicit sprint verification evidence reference)
- manual: verify navigation separation, verify decision-state consistency across both
  surfaces, verify downstream report/diagram exclusion behavior for explicitly rejected items

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active pipeline run is complete.
- This issue is an additive UX/governance refinement on top of S12-021 and should be
  implemented after S12-021 data model decisions are merged.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md




