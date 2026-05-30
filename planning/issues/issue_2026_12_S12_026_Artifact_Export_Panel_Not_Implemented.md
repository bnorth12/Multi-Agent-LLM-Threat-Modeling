# Issue S12-026: Artifact Export Panel Not Implemented in React HMI
Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-026-GUI_006-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_026_Artifact_Export_Panel_Not_Implemented.md
Verification Method: Sprint traceability verification
Status: In Review


Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

The React HMI does not implement the artifact export panel. There is no always-visible
header-level export navigation control and no reliable way to download generated artifacts
mid-run. Canonical JSON, STIX 2.1 bundle, Mermaid diagrams, markdown report, token usage
artifact, or the mitigations artifact are not consistently exportable from the GUI.

This is a deferred implementation gap — GUI-006, GUI-007, and GUI-023 are marked ⏳ in the
traceability matrix and have never been delivered in the React HMI sprint.

## Affected Requirements

- GUI-006 in Requirements/10_GUI_Requirements.md
  (Results Export Interface — SHALL provide canonical JSON, STIX, Mermaid, report download;
  DEFERRED since S07-06, still unimplemented in React HMI)
- GUI-007 in Requirements/10_GUI_Requirements.md
  (Run Snapshot Export — SHALL capture complete run state into a portable file;
  DEFERRED since S07-06, still unimplemented in React HMI)
- GUI-023 in Requirements/10_GUI_Requirements.md
  (Results Export Quick Preview — expand-and-render previews for all artifact types;
  not functional in React HMI)
- GUI-024 in Requirements/10_GUI_Requirements.md
  (Component and File Version Visibility — versions visible in Results Export view)
- PRJ-011 in Requirements/01_Project_Requirements.md
  (Export Artifact Set — SHALL produce exportable outputs for all four artifact types)
- PRJ-017 in Requirements/01_Project_Requirements.md
  (Run Snapshot Portability — SHALL support export and import of complete run state snapshots)
- INT-010 in Requirements/02_Interface_Requirements.md
  (STIX Export Contract — STIX 2.1 bundle with validation result metadata)
- INT-011 in Requirements/02_Interface_Requirements.md
  (Report Export Contract — markdown report with structured section index)

## Scope

### Export Panel Implementation

- Add an always-visible header export navigation control to the right of the report control.
  The control opens the Results Export surface at any run state (pre-run, mid-run,
  post-run) so analysts can export artifacts as soon as they are generated.
- The Results Export screen (or panel within the artifact viewer) must provide download
  buttons for each artifact type: canonical JSON, STIX 2.1, Mermaid diagrams
  (all levels as a zip or individual files), markdown report, token usage JSON.
- Mitigations artifact export is tracked separately in S12-027 but must be coordinated.
- Each download button is enabled only when the corresponding artifact has been generated;
  disabled/grayed for stages not yet completed, skipped, or not yet started.
- Export triggers a backend endpoint that serves the artifact as a file download
  (Content-Disposition: attachment).

### Quick Preview

- Each export row should include an expand-preview control that renders the artifact
  inline (as defined by GUI-023): canonical JSON collapsible tree, STIX object list,
  Mermaid rendered preview (links to existing Mermaid viewer), report markdown render,
  token usage table.

### Snapshot Export

- A separate "Export Full Snapshot" action captures the entire run state (inputs, all
  intermediate stage results, HITL decisions, prompt config, run metadata) into a single
  JSON file for archival and restore.

### Traceability Note

- The traceability matrix in Requirements/04_Traceability_Matrix.md must be updated to
  mark GUI-006, GUI-007, and GUI-023 as Delivered once this issue is closed.

## Acceptance Criteria

- [ ] Header includes an always-visible Export navigation control to the right of the
  report control.
- [ ] Export surface is reachable at any run state (including mid-run and pre-run).
- [ ] Download buttons present for canonical JSON, STIX 2.1, Mermaid (all levels),
      markdown report, token usage.
- [ ] Downloads are enabled only when the artifact exists; disabled otherwise.
- [ ] Mid-run export works for already-generated artifacts without waiting for full
  run completion.
- [ ] Each download produces a valid file of the correct format.
- [ ] Quick preview expands inline for each artifact type.
- [ ] Snapshot export produces a single file containing full run state.
- [ ] Component version inventory visible in the Results Export view (GUI-024).

## Backend Dependencies

- Backend export endpoints must exist at:
  `GET /runs/{run_id}/artifacts/{artifact_type}/download`
  (or equivalent) returning the artifact as a file attachment.
- Confirm or implement these endpoints in `src/threat_modeler/server/api.py`.

## Expected Primary Files

- frontend/src/components/ResultsExport.tsx (new or existing stub)
- frontend/src/components/ResultsExport.test.tsx
- src/threat_modeler/server/api.py
- Requirements/04_Traceability_Matrix.md (update delivery status for GUI-006/007/023)

## Validation Plan

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- frontend: npm run test -- --run src/components/ResultsExport.test.tsx
- manual: complete a run, download each artifact type, verify file content matches
  in-app viewer content, verify snapshot restore works

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




