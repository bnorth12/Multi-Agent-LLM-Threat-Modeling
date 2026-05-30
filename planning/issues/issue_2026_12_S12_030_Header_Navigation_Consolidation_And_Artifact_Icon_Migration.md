# Issue S12-030: Header Navigation Consolidation and Artifact Icon Migration

Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

The main content area still renders a secondary artifact navigation bar even though the
header now carries primary artifact navigation. This duplicates controls, consumes
vertical space, and creates visual ambiguity about which navigation surface is authoritative.

The requested behavior is:
- Keep a single authoritative artifact-domain navigation surface in the header
  (while retaining left nav as global app/workspace navigation).
- Migrate the existing in-panel artifact navigation icons to the header navigation.
- Add two new header icons for new workflow destinations: threats-with-mitigations
  review and export.
- Remove the redundant in-panel artifact nav bar after icon migration is complete.

## User Intent Captured

- "the main viewing area still has a nav bar displayed, this nav bar is no longer needed
  since the header now has the artifact nav bar"
- "i do like the icons on the main display area artifact nav bar, move those icons to
  the header nav bar before the main display area nav bar is removed"
- "two new icons will need to be created for mitigated threats and exports"

## Affected Requirements

- GUI-003 in Requirements/10_GUI_Requirements.md
  (Main Navigation and Workspace Structure; header-level navigation authority)
- GUI-005 in Requirements/10_GUI_Requirements.md
  (Threat review workflow surface alignment with S12-029)
- GUI-006 in Requirements/10_GUI_Requirements.md
  (Export navigation entry alignment with S12-026 export surface)
- S12-026 dependency
  (always-visible header Export navigation behavior)
- S12-029 dependency
  (dedicated threats-with-mitigations review viewer navigation target)
- New requirement needed: GUI-041 (or next available GUI ID)
  (Header Artifact Navigation Consolidation: single nav surface, in-panel nav removal,
  icon migration)
- New requirement needed: GUI-042 (or next available GUI ID)
  (Header Iconography Contract for new review/export controls, accessible labels,
  tooltips, keyboard focus order)

## Scope

### Header Becomes Authoritative Artifact-Domain Navigation Surface

- Header artifact navigation is the only persistent artifact-level sub-navigation surface
  inside the main working area.
- Left navigation remains available for global app/workspace routing and is not removed
  by this issue.
- The main display area artifact nav bar is removed after icon migration is complete.
- Existing navigation behavior and route targets remain functionally equivalent.

### Icon Migration

- Move all existing in-panel artifact nav icons into the header artifact navigation.
- Preserve recognizability and semantic mapping for existing icons.
- Ensure icon buttons keep accessible names and tooltips.

### New Header Icons

- Add a dedicated header icon for threats-with-mitigations review (S12-029 surface).
- Add a dedicated header icon for export (S12-026 surface).
- Both icons route to their respective surfaces and show correct active-state styling.

### Layout and Space Recovery

- Removing the in-panel nav bar increases vertical working space in the main content area.
- Verify no regression in artifact viewer readability or interaction reachability.

### Requirements and Traceability Synchronization

- Update existing GUI requirements where wording assumes in-panel artifact nav.
- Add GUI-041 and GUI-042 (or equivalent IDs) with explicit acceptance language.
- Update Requirements/04_Traceability_Matrix.md and link implementation/tests.
- Synchronize this issue, sprint tracker row, and GitHub draft body with final requirement IDs.

## Acceptance Criteria

- [ ] Header artifact navigation is the single authoritative artifact-domain
  sub-navigation surface in the main workspace area.
- [ ] Left nav continues to provide global app/workspace routing without duplicating the
  removed in-panel artifact nav bar.
- [ ] Existing in-panel artifact nav icons are migrated to header nav with no destination loss.
- [ ] Main display area artifact nav bar is removed.
- [ ] New header icon exists for threats-with-mitigations review (S12-029 destination).
- [ ] New header icon exists for export (S12-026 destination).
- [ ] Icon controls include accessible labels/tooltips and keyboard-focus support.
- [ ] Main content area gains measurable vertical space versus prior layout.
- [ ] GUI requirements updated/added (GUI-041, GUI-042 or approved equivalent IDs).
- [ ] Traceability matrix updated and linked to implementation/test evidence.

## Expected Primary Files

- frontend/src/App.tsx
- frontend/src/components/HeaderNavigation.tsx (new or existing)
- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/ThreatMitigationReviewViewer.tsx
- frontend/src/components/ResultsExport.tsx
- frontend/src/components/AppHeader.test.tsx (new or existing)
- Requirements/10_GUI_Requirements.md
- Requirements/04_Traceability_Matrix.md

## Validation Plan

- frontend: npm run test -- --run src/components/AppHeader.test.tsx
- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- frontend: npm run test -- --run src/components/ThreatMitigationReviewViewer.test.tsx
- frontend: npm run test -- --run src/components/ResultsExport.test.tsx
- Tests/test_hmi_backend_api.py (explicit sprint verification evidence reference)
- manual: confirm header icon routing, confirm in-panel nav removed, verify active-state
  behavior, confirm added vertical space and no loss of artifact/review/export reachability

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active pipeline run is complete.
- This issue depends on S12-026 and S12-029 surface availability and should be sequenced
  after those destination contracts are finalized.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md

