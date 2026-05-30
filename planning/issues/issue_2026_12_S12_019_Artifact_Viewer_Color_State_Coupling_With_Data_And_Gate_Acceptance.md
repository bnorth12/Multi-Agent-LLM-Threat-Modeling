# Issue S12-019: Artifact Viewer Color-State Coupling With Data Availability and HITL Gate Acceptance

Status: Proposed
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

Artifact-view navigation and viewer status colors are not transitioning when artifact
payloads become available and when related HITL gate decisions move to accepted.
The UI remains in a stale pre-availability visual state, which can mislead operators
into believing artifacts are still unavailable.

## Problem Statement

- Artifact color state appears to be rendered from static or incomplete readiness conditions.
- Gate-decision transitions (especially accepted states) are not consistently reflected in
  artifact-view color updates.
- Polling/refresh updates are not reliably driving color recomputation across artifact surfaces.

## Expected Behavior

- When artifact data for the selected run becomes available, artifact-view color status updates.
- When a related HITL gate is accepted, linked artifact-view color status updates if that gate
  controls artifact readiness.
- Color state remains coherent across run polling cycles, page changes, and run reselection.

## Initial Scope

1. Trace color-source derivation in React shell and artifact-view components.
1. Wire color-state computation to backend-authoritative artifact readiness and gate state.
1. Add regression tests for data-available and gate-accepted transitions.
1. Update sprint traceability and execution logs with final requirement IDs.

## Acceptance Criteria

- [ ] Artifact-view colors transition from unavailable to available when artifact payloads resolve.
- [ ] Artifact-view colors transition appropriately when related HITL gate state becomes accepted.
- [ ] Color state does not remain stale after polling refreshes.
- [ ] Automated tests cover both transition triggers (artifact availability and gate acceptance).
- [ ] Sprint governance artifacts are updated with final requirement traceability.

## Related Requirements

- GUI-003C in Requirements/10_GUI_Requirements.md
- GUI-031 in Requirements/10_GUI_Requirements.md
- Pending latest artifact color-state requirement IDs from recent sprint requirement updates

## Primary Files (Expected)

- frontend/src/App.tsx
- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/HITLGateManager.tsx
- frontend/src/components/ArtifactsViewer.test.tsx
- frontend/src/App.test.tsx

## Validation Plan

- frontend: npm run test -- --run src/App.test.tsx src/components/ArtifactsViewer.test.tsx src/components/HITLGateManager.test.tsx
- Tests/test_hmi_backend_api.py (explicit sprint verification evidence reference)
- manual: run HITL flow, accept related gate, verify artifact-view color transitions when artifact data appears

## GitHub Tracking

- Repository issue: TBD

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md

