# Sprint 2026-12: S12-030 Overnight Implementation and Verification Plan

Date: 2026-05-21
Owner: GitHub Copilot execution plan
Scope: S12-030 primary, with dependency alignment to S12-026 and S12-029

## 1. Objective

Implement and verify header artifact-domain navigation consolidation so that:
- Header is authoritative for artifact-domain sub-navigation in the main workspace.
- Existing in-panel artifact nav bar is removed after icon migration.
- Existing artifact icons are migrated to header navigation.
- Two new header icons are added for:
  - Threats-with-mitigations review destination (S12-029).
  - Export destination (S12-026).
- Left nav remains global app/workspace navigation.

## 2. Governance Deliverables (Mandatory)

Deliver and synchronize all of the following before closure:
- Requirements updates:
  - Requirements/10_GUI_Requirements.md
  - Requirements/04_Traceability_Matrix.md
  - Any additional requirement files referenced by changed behavior.
- Architecture/design documentation updates:
  - docs/HMI_Architecture_Blueprint.md
  - docs/Model_Configuration_Design_Specification.md (only if impacted)
  - docs/INDEX.md links if new design/decision notes are added.
- User/developer docs updates:
  - README.md (if navigation behavior or usage path changes)
  - docs/User_Manual.md and/or docs/user_manual/* sections for navigation changes.
- Verification artifacts and matrices:
  - Requirements/04_Traceability_Matrix.md
  - planning/Sprint_2026_12_Traceability_Matrix.md (if present in branch)
  - planning/Test_Execution_Summary_Sprint_2026_12.md (or next active summary file)
  - FQT report artifact under planning/ and/or test_reports/.

## 3. Execution Sequence

### Phase A: Baseline and Change Control
- Capture baseline screenshots of current header nav + in-panel artifact nav.
- Record baseline failing/passing status for relevant tests.
- Confirm active S12 issues and requirement IDs to avoid drift.

Exit criteria:
- Baseline evidence saved under docs/screenshots/ or test_reports/.
- Baseline test status recorded in execution log.

### Phase B: Requirements and Design First (Before Code)
- Add/confirm GUI-041 requirement text for header artifact-domain nav consolidation.
- Add/confirm GUI-042 requirement text for header iconography contract.
- Update traceability entries mapping GUI-041/042 to target files/tests.
- Update architecture/design docs to reflect two-level nav model:
  - Left nav: global app/workspace navigation.
  - Header nav: artifact-domain sub-navigation.

Exit criteria:
- Requirement IDs and SHALL statements are finalized.
- Traceability rows for GUI-041/042 exist and are linked to planned tests.

### Phase C: Implementation
- Header navigation component changes:
  - Migrate existing in-panel artifact icons into header.
  - Add new icons for review and export destinations.
  - Add accessible labels/tooltips and keyboard focus support.
- Main display cleanup:
  - Remove redundant in-panel artifact nav bar.
  - Preserve artifact content behavior and routes.
- Route/state synchronization:
  - Ensure active-route styling remains correct.
  - Ensure left nav remains unchanged for global routing.
- Cross-issue destination integration:
  - Route to S12-026 export surface.
  - Route to S12-029 review surface.

Exit criteria:
- UI behavior matches S12-030 acceptance criteria.
- No loss of destination reachability.

### Phase D: Test Development and Update
- Update/create targeted frontend tests:
  - Header nav rendering and icon set.
  - Route transition tests for migrated and new icons.
  - Accessibility label/tooltips tests.
  - Regression test ensuring in-panel artifact nav no longer renders.
- Update impacted existing tests to new navigation assumptions.

Exit criteria:
- New/updated tests compile and run.
- Assertions explicitly cover GUI-041/042 behavior.

### Phase E: Verification Stack (Execution)
Run in this order:
1. Fast targeted frontend tests (new/modified components).
2. Full frontend regression subset for navigation/artefact surfaces.
3. Backend API regression for artifact endpoints (existing suite).
4. End-to-end smoke test with live browser flow.
5. FQT execution for impacted scenarios.

Required command set (adapt if scripts differ):
- frontend: npm run test -- --run src/components/AppHeader.test.tsx
- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- frontend: npm run test -- --run src/components/ThreatMitigationReviewViewer.test.tsx
- frontend: npm run test -- --run src/components/ResultsExport.test.tsx
- backend: PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- regression: PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- smoke: PYTHONPATH=src .venv\Scripts\python.exe scripts/live_browser_e2e_smoke_react.py
- FQT: run sprint FQT scenario set and capture report evidence.

Exit criteria:
- No critical regressions.
- Smoke and FQT pass for impacted scenarios or are triaged with documented disposition.

### Phase F: Evidence, Matrices, and Closeout Package
- Update verification matrices linking requirement IDs to test evidence.
- Record exact commands, pass/fail, and artifact paths.
- Save screenshots for:
  - Header icon set.
  - No in-panel artifact nav.
  - Review/export icon navigation destinations.
- Update sprint test execution summary and FQT report.

Exit criteria:
- Traceability and verification artifacts are complete and auditable.
- S12-030 issue, tracker row, and GitHub draft remain synchronized.

## 4. Regression and Risk Controls

- Do not modify left nav global behavior under S12-030.
- Do not regress S12-026 export reachability.
- Do not regress S12-029 review reachability.
- If route regressions occur, block closure and log defect split issue(s).

## 5. Definition of Done

S12-030 is complete only when all are true:
- Requirements and traceability docs are updated with GUI-041/042 (or approved equivalent).
- Architecture/design docs and user docs reflect final navigation model.
- Implementation is merged and behavior verified.
- Unit/regression/smoke/FQT evidence is recorded.
- Verification matrices map requirements to passing evidence artifacts.

## 6. Overnight Handoff Package

At completion, produce one handoff summary containing:
- Files changed grouped by category (requirements/docs/code/tests).
- Commands executed with outcomes.
- Known residual risks or deferred follow-ups.
- Exact evidence artifact paths.
- Recommended go/no-go statement for next-day review.
