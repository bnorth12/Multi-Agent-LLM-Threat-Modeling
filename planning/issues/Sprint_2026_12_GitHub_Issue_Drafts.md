# Sprint 2026-12 GitHub Issue Drafts

Use these issue bodies to populate the GitHub repository so Sprint 2026-12 governance is mirrored in the repo issue tracker.

---

## S12-011

Title: Sprint 2026-12: Ordered HITL Gate ledger with lifecycle summary

Body:

```md
## Summary

Sprint 2026-12 introduced a gate-centric HMI workflow refinement. The HITL Gate page must show all defined gates in pipeline order and provide lifecycle counts so the operator has one authoritative ledger during review and resume workflows.

## Related Requirement

- GUI-030 in Requirements/10_GUI_Requirements.md

## Acceptance Criteria

- All HITL gates are shown in pipeline order on one page.
- Lifecycle counts are shown for Approved, Rejected, Bypassed, and Pending.
- Row-level gate actions remain available for the active workflow state.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- frontend: npm run test -- --run src/components/HITLGateManager.test.tsx

## Closure Evidence

- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- Requirements/10_GUI_Requirements.md
```

---

## S12-018

Title: Sprint 2026-12: React input file parsing parity and spreadsheet binary-injection guard

Body:

```md
## Summary

Full UAS suite runs in the React HMI degraded because CSV/XLSX uploads were forwarded as raw file text only, and XLSX payload bytes could be injected into `initial_state.raw_text` rather than parsed into structured table rows. This reduced Agent 01 parse quality and cascaded into sparse context-builder, trust-boundary, STRIDE, and threat outputs.

This issue restores ingestion parity with the Streamlit path by parsing CSV/XLSX client-side into `initial_state.tables` and keeping `initial_state.raw_text` for narrative text inputs.

## Related Requirements

- RHMI-017 in Requirements/11_React_HMI_Refactor_Requirements.md
- S12-REQ-018 in planning/Sprint_2026_12_Traceability_Matrix.md

## Acceptance Criteria

- React run creation parses CSV and XLSX files into structured row dictionaries under `initial_state.tables`.
- Raw spreadsheet binary payloads are not injected into `initial_state.raw_text`.
- Narrative files (md/txt/yaml/yml) remain available in `initial_state.raw_text`.
- Full UAS suite run shows restored downstream data richness in context, trust boundaries, STRIDE, and threat generation stages.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- frontend: npm install
- frontend: npm run test -- --run src/components/HITLGateManager.test.tsx
- manual: run full UAS suite through React wizard and verify populated trust boundaries / STRIDE / threats

## Closure Evidence

- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/package.json
- Requirements/11_React_HMI_Refactor_Requirements.md
- Requirements/12_React_HMI_Traceability_To_Tests.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-012

Title: Sprint 2026-12: Persistent monitoring status, watchdog telemetry, and HITL-page continuity

Body:

```md
## Summary

Operators should be able to stay on the HITL Gate page while a run continues or resumes, with the persistent execution-status chrome providing centered plain-language status text, visible watchdog heartbeat telemetry, and an animated header running indicator while a stage is active.

## Related Requirements

- GUI-031 in Requirements/10_GUI_Requirements.md
- RHMI-005 in Requirements/11_React_HMI_Refactor_Requirements.md

## Acceptance Criteria

- Resuming from a gate does not force navigation back to the execution page.
- Footer timeline shows centered plain-language run status.
- Watchdog telemetry remains visible beside the execution timeline with explicit heartbeat age versus timeout.
- An animated running-state indicator is visible in the header while a stage is actively running.
- Backend/runtime state and footer status remain coherent for paused, running, and completed states.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- frontend: npm run test -- --run src/App.test.tsx src/components/ExecutionProgress.test.tsx src/components/HITLGateManager.test.tsx
- PYTHONPATH=src python -m pytest Tests/test_hmi_backend_api.py -q

## Closure Evidence

- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- Requirements/10_GUI_Requirements.md
- Requirements/11_React_HMI_Refactor_Requirements.md

---

## S12-012 Implementation Note

Use this issue to track the post-refinement monitoring polish that restores a visible watchdog surface near the execution timeline and the animated header running cue from the earlier operator experience, rather than opening a separate issue unless monitoring scope expands beyond the current runtime-status surfaces.
```

---

## D-S12-011

Title: Decide whether to retain, repurpose, or remove the Execution page after Sprint 2026-12 HMI workflow refinement

Body:

```md
## Summary

The footer timeline and HITL Gate page now cover most live-monitoring needs. The remaining Execution page appears to provide minimal unique value and should be reviewed as an explicit product/program decision rather than silently removed as part of another change.

## Decision Needed

- Retain the page as-is
- Repurpose the page for unique execution diagnostics
- Remove the page and update requirements/navigation accordingly

## Acceptance Criteria

- A decision is recorded with rationale.
- Any resulting requirement updates are made in the actual requirement documents.
- Navigation and tests are updated if the page changes.

## Closure Evidence

- planning/issues/Sprint_2026_12_Issue_Tracker.md
- planning/issues/issue_2026_12_S12_011_HITL_Gate_Ledger_And_Execution_Page_Rationalization.md
```

---

## S12-013

Title: Sprint 2026-12: Enforce Gate 0 input integrity preflight review

Body:

```md
## Summary

Gate 0 must become an explicit analyst-reviewed preflight gate before Stage 1 execution. The reviewer needs human-readable parsed input summaries and checks to approve or reject intent and integrity before model execution begins.

## Related Requirement

- GUI-032 in Requirements/10_GUI_Requirements.md

## Acceptance Criteria

- Pipeline pauses at Gate 0 before Stage 1 executes when HITL is enabled.
- Gate 0 dialog shows human-readable preflight summaries and checks.
- Analyst rationale is required for final approve/reject decisions.
- Timeline shows Gate 0 marker before Stage 1.

## Validation

- PYTHONPATH=src python -m pytest Tests/integration/test_avionics_expected_results.py -q
- PYTHONPATH=src python -m pytest Tests/test_hmi_backend_api.py -q

## Closure Evidence

- Requirements/10_GUI_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
```

---

## S12-014

Title: Sprint 2026-12: Add mandatory post-Stage-1 normalization review gate

Body:

```md
## Summary

Add a dedicated normalization review gate after Stage 1 and before Stage 2 so analysts validate Stage 1 normalized canonical output before context building continues.

## Related Requirement

- GUI-033 in Requirements/10_GUI_Requirements.md

## Acceptance Criteria

- New normalization review gate opens immediately after Stage 1 completes.
- Stage 2 remains blocked until normalization gate is approved.
- Gate dialog shows human-readable normalization summary (system, counts, interfaces, checks).
- Timeline gate markers reflect before/after stage control points with deterministic ordering.

## Validation

- frontend: npm run test -- --run src/components/HITLGateManager.test.tsx
- PYTHONPATH=src python -m pytest Tests/integration/test_avionics_expected_results.py -q

## Closure Evidence

- Requirements/10_GUI_Requirements.md
- docs/HMI_Architecture_Blueprint.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
```

---

## S12-015

Title: Sprint 2026-12: Mermaid artifact reviewer with parsed selector and split view

Linked GitHub Issue: #68 (https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/68)

Body:

```md
## Summary

Improve Mermaid artifact review usability by parsing multi-diagram payloads into a named selector, supporting split/diagram/text display modes, keeping source text editable, and rendering the selected diagram with a clear position indicator (`x of n - diagram name`).

## Related Requirements

- GUI-034 in Requirements/10_GUI_Requirements.md
- RHMI-010 in Requirements/11_React_HMI_Refactor_Requirements.md

## Acceptance Criteria

- Mermaid payloads containing multiple diagrams are parsed into selectable named entries.
- The currently selected diagram is shown in rendered and editable-source forms.
- UI supports split/diagram/text viewing modes without losing selected diagram context.
- The selector area shows position and name using `x of n - diagram name`.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe scripts/live_browser_e2e_smoke_react.py
- Tests/e2e/test_frontend_react_mui_full_workflow.py (frontend_full lane)

## Closure Evidence

- Requirements/10_GUI_Requirements.md
- Requirements/11_React_HMI_Refactor_Requirements.md
- Requirements/12_React_HMI_Traceability_To_Tests.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
```

---

## S12-031

Title: Sprint 2026-12: Timeline parsing segments before every gate with readiness-coupled visualization

Body:

```md
## Summary

Execution timeline gate diamonds moved, but parse-phase visibility is still ambiguous during gate handoff windows. Add narrow parsing segments before every gate boundary (including Gate 0), and color them by parse lifecycle so analysts can tell whether the system is still preparing data or is truly gate-ready.

## Related Requirements

- GUI-043 in Requirements/10_GUI_Requirements.md
- GUI-031 in Requirements/10_GUI_Requirements.md
- HITL-012 in Requirements/03_HITL_Requirements.md

## Acceptance Criteria

- Timeline shows a narrow pre-gate segment before every gate boundary including Gate 0.
- Segment does not render text labels inside the narrow bar.
- Segment color is brown while parsing is in progress.
- Segment color turns green when parsing is complete.
- Gate-open behavior and segment state are coherent with backend readiness guards (no gate opens with empty reviewer payload).
- Timeline legend includes parsing-state entries so the color semantics are explicit.

## Validation

- frontend: npm run test -- --run src/components/ExecutionProgress.test.tsx
- backend: PYTHONPATH=src python -m pytest Tests/unit/test_run_manager.py Tests/test_hmi_backend_api.py -q
- manual: live run walkthrough through Gate 0 -> Gate 4 confirming parse-state segment transitions and non-empty gate payload at pause.

## Closure Evidence

- frontend/src/components/ExecutionProgress.tsx
- frontend/src/components/ExecutionProgress.test.tsx
- src/threat_modeler/orchestrator.py
- Requirements/10_GUI_Requirements.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
```

---

## S12-017

Title: Sprint 2026-12: Preserve completed-run artifact retrieval after backend restart

Linked GitHub Issue: #70 (https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/70)

Body:

```md
## Summary

Completed and paused runs remained visible in the run list after backend restart but artifact endpoints returned `404 Unknown or incomplete run_id` because only metadata persisted and in-memory runtime state was unavailable.

This issue hardens restart behavior by persisting a restorable run-state projection and rehydrating artifact-serving state when needed.

## Related Requirements

- RHMI-016 in Requirements/11_React_HMI_Refactor_Requirements.md
- S12-REQ-017 in planning/Sprint_2026_12_Traceability_Matrix.md

## Acceptance Criteria

- Completed and paused runs listed by `GET /runs` remain artifact-addressable after backend restart.
- `GET /runs/{run_id}/artifacts/canonical`, `/mermaid`, `/stix`, and `/report` succeed for restorable historical runs.
- API no longer exhibits run-list-only ghost entries for completed runs.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- Manual restart probe of health endpoint and artifact endpoint retrieval for historical run IDs

## Closure Evidence

- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- Requirements/11_React_HMI_Refactor_Requirements.md
- Requirements/12_React_HMI_Traceability_To_Tests.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-019

Title: Sprint 2026-12: Wire artifact viewer color states to artifact availability and HITL gate acceptance

Body:

```md
## Summary

Artifact-view surfaces currently retain stale colors even after artifact data becomes available and related HITL gate decisions are accepted. This creates a false negative operator signal and breaks gate-to-artifact workflow confidence.

This issue wires artifact status color rendering to backend-authoritative run/artifact readiness plus gate decision state, so colors transition deterministically as the run advances.

## Related Requirements

- GUI-003C in Requirements/10_GUI_Requirements.md
- GUI-031 in Requirements/10_GUI_Requirements.md
- Latest artifact color-state requirement IDs added in sprint governance docs (to be linked during implementation PR)

## Acceptance Criteria

- Artifact navigation/viewer status colors update when artifact data becomes available for the selected run.
- Color transitions also reflect related HITL gate acceptance state where applicable.
- Colors no longer remain in stale pre-availability state after data arrival or gate acceptance.
- Behavior is resilient across run polling refreshes and page navigation.
- Sprint 2026-12 traceability and execution log are updated with final requirement ID mapping.

## Validation

- frontend: npm run test -- --run src/App.test.tsx src/components/ArtifactsViewer.test.tsx src/components/HITLGateManager.test.tsx
- manual: execute a HITL-gated run, accept the related gate, and verify artifact-view color transitions as artifacts become available

## Closure Evidence

- frontend/src/App.tsx
- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/HITLGateManager.tsx
- Requirements/10_GUI_Requirements.md
- Requirements/11_React_HMI_Refactor_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-020

Title: Sprint 2026-12: Persist per-stage LLM latency and token telemetry with run records

Body:

```md
## Summary

Capture and persist per-stage LLM latency data points, measured from prompt dispatch to model response completion, alongside per-stage token usage already tracked for live runs.

This extends telemetry from display-only diagnostics into durable run-level evidence that supports performance trend analysis, timeout tuning, and governance audits.

## Related Requirements

- GUI-015 in Requirements/10_GUI_Requirements.md
- GUI-027 in Requirements/10_GUI_Requirements.md
- INT-005 in Requirements/02_Interface_Requirements.md
- Pending sprint requirement ID for persisted stage latency metrics

## Acceptance Criteria

- Each LLM-backed stage records prompt_sent timestamp and response_received timestamp (or equivalent monotonic duration fields).
- Persisted run data includes per-stage latency metrics and per-stage token metrics in one queryable structure.
- Telemetry survives backend restart and remains available through run retrieval/export surfaces.
- Non-LLM or bypassed stages are represented with explicit null or skipped semantics (no misleading zero durations).
- Sprint traceability and execution log are updated with final requirement mapping and verification evidence.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- manual: execute at least one live run, verify persisted per-stage latency + token fields in run API/export payloads

## Closure Evidence

- src/threat_modeler/services/openai_compatible_adapter.py
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- frontend/src/components/TokenUsageView.tsx
- Requirements/10_GUI_Requirements.md
- Requirements/02_Interface_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-021

Title: Sprint 2026-12: Inline threat/mitigation review with per-item accept/reject and non-blocking pending default

Body:

```md
## Summary

The Threat viewer is missing three interconnected capabilities:

1. Clicking a threat row should open a detail dialog showing all threat fields and — after the mitigation stage completes — the mitigations mapped to that threat inline.
2. Per-threat and per-mitigation accept/reject decision controls so individual items can be excluded from diagram and report generation.
3. A non-blocking default where pending (unreviewed) threats and mitigations count as accepted, keeping the pipeline running on first pass with no user input required.

## Related Requirements

- GUI-005 in Requirements/10_GUI_Requirements.md
- HITL-004 in Requirements/03_HITL_Requirements.md
- HITL-005 in Requirements/03_HITL_Requirements.md
- HITL-007 in Requirements/03_HITL_Requirements.md
- HITL-008 in Requirements/03_HITL_Requirements.md
- Pending new GUI-005 extension requirement IDs to be assigned during implementation

## Acceptance Criteria

### Threat Detail Dialog and Inline Mitigations

- Clicking a threat row opens a detail dialog or expanded inline panel with all threat fields.
- Once the mitigation stage completes, the dialog renders the mitigations mapped to that threat with full mitigation fields and a status chip: Pending, Accepted, or Rejected.
- Dialog state is preserved across open/close cycles.

### Per-Item Decision Controls

- Threat table shows per-row status chip and Approve/Reject buttons.
- Reject action offers optional rationale text before confirming.
- Per-item decisions are persisted in run state and survive page navigation.
- Per-item decisions are captured in the HITL audit record for the run.

### Pending-as-Accepted Default and Downstream Filtering

- Diagram and report stages receive all Accepted and Pending threats and mitigations (non-blocking).
- Only explicitly Rejected items are excluded from diagram and report generation.
- Behavior is identical with no per-item decisions made (full pass-through).
- Snapshot export captures the full decision state.

## Validation

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- manual: run full pipeline, click threat, verify inline mitigation population, reject one mitigation, confirm excluded from diagram/report output

## Closure Evidence

- frontend/src/components/ArtifactsViewer.tsx
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- src/threat_modeler/orchestrator.py
- Requirements/10_GUI_Requirements.md
- Requirements/03_HITL_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-022

Title: Sprint 2026-12: Mermaid diagram lightbox with wheel/keyboard/button zoom and drag/button pan

Body:

```md
## Summary

Large Mermaid diagrams (Level 1, Level 2) are unreadable at the fixed inline preview
size. Clicking the diagram preview should open a full-viewport dialog with flexible
navigation controls: mouse-wheel zoom, keyboard `+`/`-` zoom, clickable `+`/`-` zoom
buttons, click-and-drag pan, and directional pan buttons (up/down/left/right).

This provides multiple interaction paths so analysts can inspect component labels, edge
annotations, and trust boundary markers without leaving the tool.

## Related Requirements

- GUI-020 in Requirements/10_GUI_Requirements.md — Mermaid Diagram Viewer (extension)
- GUI-034 in Requirements/10_GUI_Requirements.md — Mermaid Multi-Diagram Review Workspace (extension)
- RHMI-010 in Requirements/11_React_HMI_Refactor_Requirements.md (extension)

## Acceptance Criteria

- Clicking a Mermaid diagram preview opens a full-viewport MUI Dialog.
- The dialog renders the same diagram as the inline preview without quality loss.
- Mouse-wheel zoom in/out works within the dialog, centered on the cursor position.
- Keyboard `+` and `-` zoom controls work while the dialog has focus.
- Clickable `+` and `-` zoom controls are visible and functional.
- Click-and-drag pan works within the dialog.
- Directional pan controls (`Up`, `Down`, `Left`, `Right`) are visible and functional.
- A reset button or double-click returns the diagram to fit-to-dialog.
- Escape or the close button dismisses the dialog without affecting the inline preview.
- The lightbox works for all diagrams in the selector (Level 0, Level 1, Level 2).

## Implementation Notes

- CSS transform: scale + translate on the SVG container is the preferred approach to
  avoid additional npm dependencies.
- Place zoom and directional controls in a persistent control strip so users can operate
  without drag gestures.
- If a pan/zoom library (e.g., react-zoom-pan-pinch) is used, document it in the PR.
- MUI Dialog with `maxWidth="xl"` and `fullWidth` provides a suitable container.

## Validation

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- manual: open a completed run, click each diagram level, verify zoom/pan/close behavior

## Closure Evidence

- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/MermaidLightbox.tsx (new)
- Requirements/10_GUI_Requirements.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-023

Title: Sprint 2026-12: Premature run completion leaves report-writer stage non-terminal; timeline stuck blue and watchdog stale

Body:

```md
## Summary

Two coupled defects observed during a live run:

1. The run transitioned to Completed before final sequencing was satisfied (coupled to S12-024 Gate 9 defect).
2. The report writer stage did not receive a terminal completion trigger (LLM completion + artifact persistence), so timeline state remained blue and watchdog telemetry went stale against a non-terminal stage.

## Related Requirements

- GUI-026 in Requirements/10_GUI_Requirements.md — Run Liveness Telemetry
- GUI-027 in Requirements/10_GUI_Requirements.md — Run Diagnostics Panel
- GUI-031 in Requirements/10_GUI_Requirements.md — Persistent Timeline Status
- RHMI-005 in Requirements/11_React_HMI_Refactor_Requirements.md

## Acceptance Criteria

- Run cannot transition to Completed before Gate 9 decision flow is satisfied (cross-validated with S12-024).
- Report writer stage transitions to terminal state only after actual completion signal (LLM completion + artifact persistence).
- When a run transitions to Completed, all In Progress timeline stages transition to their terminal state (Success or Failure) within one polling cycle.
- No stage remains blue in the timeline on a run in Completed or Failed state.
- Diagnostics panel correctly reflects the completed run state without contradiction from stale watchdog data.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: run full HITL pipeline, verify run does not complete before Gate 9 decision, verify report-writer stage terminalization, confirm timeline clears and watchdog telemetry remains coherent

## Closure Evidence

- src/threat_modeler/orchestrator.py
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/services/openai_compatible_adapter.py
- frontend/src/components/ExecutionProgress.tsx
- frontend/src/components/ExecutionProgress.test.tsx
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-024

Title: Sprint 2026-12: HITL Gate 9 (Final Release Gate) not firing — run completes without final approval

Body:

```md
## Summary

HITL Gate 9 (Final Release Gate, HITL-006) did not fire during the active run. The pipeline
completed and the report artifact was published without pausing for an analyst approve/reject
decision. No signed gate decision record exists for this run's final gate.

This is a hard HITL compliance defect — HITL-006 is a SHALL requirement.

There is also requirement-anchor drift between gate indices in the current implementation
(Gate 0 through Gate 9) and HITL requirement IDs. This issue includes synchronization of
requirements/traceability mapping so Gate 9 and related gates are unambiguous.

## Related Requirements

- HITL-006 in Requirements/03_HITL_Requirements.md — Final Release Gate (SHALL)
- HITL-008 in Requirements/03_HITL_Requirements.md — Signed Decision Records
- GUI-030 in Requirements/10_GUI_Requirements.md — Ordered HITL Gates Ledger

## Acceptance Criteria

- After agent_09 completes, execution pauses and Gate 9 appears as Pending in the HITL Gates ledger.
- Run does not transition to Completed until an Approve, Reject, or explicit Bypass decision is submitted for Gate 9.
- A signed decision record for Gate 9 is present in the run audit output after every HITL-mode run.
- Gate 9 row is present in the frontend HITL Gates ledger in all run states.
- Reject at Gate 9 halts the run and records rationale.
- Requirements and traceability docs include explicit Gate Index -> Requirement ID mapping aligned to current Gate 0..9 workflow.
- `Requirements/03_HITL_Requirements.md` is updated to match current gate workflow mapping.
- `Requirements/04_Traceability_Matrix.md` is updated with matching references.
- S12-024 issue artifacts are synchronized after requirement edits (issue spec, tracker row, and GitHub draft).

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: run full HITL pipeline, confirm Gate 9 pauses execution, confirm signed record in snapshot export

## Closure Evidence

- src/threat_modeler/orchestrator.py
- src/threat_modeler/backend/run_manager.py
- frontend/src/components/HITLGateManager.tsx
- frontend/src/components/HITLGateManager.test.tsx
- Requirements/03_HITL_Requirements.md
- Requirements/04_Traceability_Matrix.md
- planning/issues/issue_2026_12_S12_024_HITL_Gate_9_Final_Release_Gate_Not_Firing.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-025

Title: Sprint 2026-12: Generated report missing table of contents and required section structure

Body:

```md
## Summary

The markdown report generated by agent_09 is poorly formatted and does not follow the
required table of contents structure. Required sections (executive summary, scope, system
boundaries, threat findings, mitigations, residual risk) are absent or malformed.

This violates C10-A09-001 and breaks downstream section-index and conversion workflows.

For this issue scope, diagrams are reference-only (approved artifact references).
Inline diagram embedding in the report is deferred to a follow-on enhancement.

## Related Requirements

- C10-A09-001 in Requirements/Components/C10_Agent_09_Report_Requirements.md — Structured Report Generation (SHALL)
- C10-A09-002 in Requirements/Components/C10_Agent_09_Report_Requirements.md — Approved Artifact Referencing (approved diagrams/threats/controls only)
- C10-A09-003 in Requirements/Components/C10_Agent_09_Report_Requirements.md — Conversion-Ready Output
- INT-011 in Requirements/02_Interface_Requirements.md — Report Export Contract
- PRJ-011 in Requirements/01_Project_Requirements.md — Export Artifact Set

## Acceptance Criteria

- Generated report contains a table of contents with links to each required section.
- Required sections present: Executive Summary, Scope, System Boundaries, Threat Findings, Mitigations, Residual Risk.
- Section headings use consistent H2 (##) level matching table of contents entries.
- Threat findings section contains a structured entry per threat (ID, STRIDE, score, rationale, affected components, mitigations).
- Report references approved diagram artifacts only (or explicitly states none available for the run).
- Report markdown formatting is readability-oriented: no malformed heading/list structures, no dense unbroken text blocks in core sections, and consistent subsection formatting.
- Report passes section-presence automated tests.
- Report renders correctly with heading hierarchy in the Markdown viewer.

## Implementation Notes

The fix is primarily a prompt template update for agent_09. A post-generation validator
asserting required sections should also be considered. Do not change the section set
without updating the INT-011 section index contract.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
  (section-presence tests must pass)
- manual: run full pipeline, open report in Markdown viewer, verify TOC and all sections present

## Closure Evidence

- data/models/ (agent_09 prompt configuration)
- src/threat_modeler/agents/agent_09_report_writer.py
- Requirements/Components/C10_Agent_09_Report_Requirements.md
- Requirements/02_Interface_Requirements.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-026

Title: Sprint 2026-12: Artifact export panel not implemented in React HMI (GUI-006 deferred, never delivered)

Body:

```md
## Summary

The React HMI does not implement the artifact export panel as an always-visible workflow
surface. There is no header-level export navigation control and no reliable way to
download generated artifacts mid-run. Canonical JSON, STIX 2.1 bundle, Mermaid diagrams,
markdown report, token usage artifact, or the mitigations artifact are not consistently
exportable from the GUI.

GUI-006 (Results Export Interface) and GUI-007 (Run Snapshot Export) were explicitly
deferred since Sprint S07-06 and have never been implemented in the React HMI refactor.
This is a high-priority deferred SHALL requirement.

## Related Requirements

- GUI-006 in Requirements/10_GUI_Requirements.md — Results Export Interface (SHALL; deferred ⏳ since S07-06)
- GUI-007 in Requirements/10_GUI_Requirements.md — Run Snapshot Export (SHALL; deferred ⏳ since S07-06)
- GUI-023 in Requirements/10_GUI_Requirements.md — Results Export Quick Preview
- GUI-024 in Requirements/10_GUI_Requirements.md — Component and File Version Visibility in export view
- PRJ-011 in Requirements/01_Project_Requirements.md — Export Artifact Set
- PRJ-017 in Requirements/01_Project_Requirements.md — Run Snapshot Portability
- INT-010 in Requirements/02_Interface_Requirements.md — STIX Export Contract
- INT-011 in Requirements/02_Interface_Requirements.md — Report Export Contract

## Acceptance Criteria

- Header includes an always-visible Export navigation control to the right of the report control.
- Export surface is reachable at any run state (pre-run, mid-run, post-run).
- Download buttons present for canonical JSON, STIX 2.1, Mermaid (all levels), markdown report, token usage.
- Downloads are enabled only when the artifact exists; disabled otherwise.
- Mid-run export works for already-generated artifacts without waiting for run completion.
- Each download produces a valid file of the correct format.
- Quick preview (GUI-023) expands inline for each artifact type.
- Snapshot export produces a single file containing full run state (GUI-007 / PRJ-017).
- Component version inventory visible in the Results Export view (GUI-024).
- Traceability matrix updated to mark GUI-006, GUI-007, GUI-023 as Delivered on closure.

## Implementation Notes

- Add backend export endpoints: `GET /runs/{run_id}/artifacts/{artifact_type}/download`
  returning the artifact as a file attachment in `src/threat_modeler/server/api.py`.
- New component: `frontend/src/components/ResultsExport.tsx`.
- Coordinate mitigations export button with S12-027.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- frontend: npm run test -- --run src/components/ResultsExport.test.tsx
- manual: complete a run, download each artifact type, verify file content, verify snapshot restore works

## Closure Evidence

- frontend/src/components/ResultsExport.tsx
- src/threat_modeler/server/api.py
- Requirements/04_Traceability_Matrix.md (GUI-006/007/023 marked Delivered)
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-027

Title: Sprint 2026-12: Mitigations artifact has no viewer and no export capability in the React HMI

Body:

```md
## Summary

The mitigations artifact produced by agent_08 (mitigation mapper) has no dedicated
viewer in the React HMI and is not included in the export panel. Analysts cannot review
mitigation records outside the inline threat detail dialog (S12-021), and there is no
mechanism to download the mitigations artifact.

This is both a requirements gap (no explicit mitigation export requirement; INT-008
covers visualization read of mitigations but the viewer is absent) and an implementation
gap.

## Related Requirements

- INT-008 in Requirements/02_Interface_Requirements.md — Visualization Read Contract
  (SHALL provide read access to graph nodes, flows, boundaries, threats, mitigations,
  and evidence references; viewer is absent)
- GUI-006 in Requirements/10_GUI_Requirements.md — Results Export Interface
  (mitigations export is a gap in this requirement; text must be extended)
- PRJ-011 in Requirements/01_Project_Requirements.md — Export Artifact Set
  (mitigations export is a gap; text must be extended)
- New requirement: GUI-038 (or equivalent) — Standalone Mitigations Artifact Viewer

## Acceptance Criteria

- Mitigations subview renders all mitigations in a sortable/filterable table after the mitigation stage completes.
- Row expand shows full mitigation detail (description, implementation guidance, linked threat IDs, control type).
- Status column (Pending/Accepted/Rejected) reflects S12-021 decision state when available.
- Export panel includes a mitigations JSON download button, enabled when artifact exists.
- GUI-006 and PRJ-011 requirement text updated to explicitly include mitigations export.
- New GUI-038 requirement added to Requirements/10_GUI_Requirements.md.
- Traceability matrix updated with GUI-038 row.

## Implementation Notes

- Coordinate with S12-021 (per-item accept/reject state) so status column is wired to the same decision store from the start.
- Coordinate with S12-026 (export panel) so mitigations download button lands in the same export surface.
- Mitigations export is accessed through the always-visible header Export navigation introduced in S12-026.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- manual: complete a run, navigate to mitigations viewer, verify all records present, verify export downloads valid JSON

## Closure Evidence

- frontend/src/components/ArtifactsViewer.tsx (or MitigationsViewer.tsx)
- src/threat_modeler/server/api.py
- Requirements/10_GUI_Requirements.md (GUI-038 added, GUI-006 extended)
- Requirements/01_Project_Requirements.md (PRJ-011 extended)
- Requirements/04_Traceability_Matrix.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-028

Title: Sprint 2026-12: Prior canonical graph as optional run input for incremental enrichment (PRJ-013 mechanism missing)

Body:

```md
## Summary

There is no way to start a new run with an optional prior canonical graph baseline from a
previous run of the same system.

The intended behavior is baseline + new input:
- Use prior canonical graph as baseline context.
- Preserve approved prior elements.
- Add/update only new details inferred from the new run input.

PRJ-013 (Incremental Enrichment) requires this flow, but the setup wizard baseline input,
orchestrator baseline injection, and conflict-gate path are missing.

## Related Requirements

- PRJ-013 in Requirements/01_Project_Requirements.md — Incremental Enrichment (SHALL; mechanism not implemented)
- INT-002 in Requirements/02_Interface_Requirements.md — Agent Input Contract
  (must accept optional prior canonical graph as baseline field)
- HITL-010 in Requirements/03_HITL_Requirements.md — Conditional Merge Conflict Resolution Gate
  (fires when new model conflicts with baseline elements)
- New requirement: GUI-039 (or equivalent) — Prior Canonical Graph Optional Input Field in setup wizard
- New requirement: INT-002 extension or new INT-015 — Baseline Graph Input Contract

## Acceptance Criteria

- Setup wizard includes an optional "Prior Canonical Graph" file upload field.
- Uploading an invalid file surfaces a schema validation error before run initiation.
- When a prior canonical graph is provided, the orchestrator injects it as the baseline at the correct pipeline stage.
- Previously approved elements from the baseline are preserved (not destructively overwritten).
- HITL-010 Merge Conflict Gate fires when conflicts are detected between the new model output and baseline elements.
- Run record persists a reference to the prior canonical graph source (run ID or content hash).
- Exported artifacts carry provenance fields distinguishing baseline elements vs. new elements.
- New GUI-039 requirement added for the prior canonical graph input field.
- Traceability matrix updated to link GUI-039 and any new interface requirement to PRJ-013.

## Implementation Notes

- The prior canonical graph input is an optional file upload on the setup wizard, parallel to the existing system description upload.
- Reuse the canonical schema validator for baseline file validation on upload.
- Extend stage context to carry a `baseline_canonical` field alongside `canonical` so agents can reference the prior baseline.
- Merge conflict detection should compare baseline element IDs against newly generated elements and flag divergences in identity, classification, or trust boundary assignment.
- This is a significant new capability — consider whether it warrants a dedicated sprint or feature branch.

## Validation

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: export canonical graph from run A, start run B with it as baseline, verify prior elements preserved, verify conflict gate fires on a modified element

## Closure Evidence

- frontend/src/components/ (setup wizard baseline upload)
- src/threat_modeler/orchestrator.py
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- Requirements/10_GUI_Requirements.md (GUI-039 added)
- Requirements/02_Interface_Requirements.md (INT-002 extended or INT-015 added)
- Requirements/04_Traceability_Matrix.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-029

Title: Sprint 2026-12: Split threat artifact viewer and threats-with-mitigations review viewer

Body:

```md
## Summary

S12-021 introduces per-item threat/mitigation accept-reject behavior, but we also need a
clear UI separation between artifact browsing and analyst review workflow.

Keep the existing threat artifact viewer as a read-focused artifact surface, and add a
separate threats-with-mitigations review viewer as the workflow decision surface.

This avoids coupling artifact rendering concerns with gate/review controls and allows both
surfaces to evolve independently while sharing a single decision-state source.

## Related Requirements

- GUI-005 in Requirements/10_GUI_Requirements.md — Threat Review Screen behavior
- INT-008 in Requirements/02_Interface_Requirements.md — Visualization Read Contract
- S12-021 dependency — per-item decision semantics and state model
- New requirement: GUI-040 (or equivalent) — dual-surface contract
  (Artifact Viewer vs Review Viewer responsibilities)

## Acceptance Criteria

- Existing threat artifact viewer remains available and functionally intact for artifact inspection.
- New threats-with-mitigations review viewer exists as a distinct navigation target.
- Review viewer supports per-item accept/reject controls and status filtering.
- Review semantics match S12-021: pending defaults to accepted; only explicit rejection excludes downstream outputs.
- Decision state remains consistent between both surfaces (single source of truth).
- UI copy/tooltips clearly distinguish artifact inspection from workflow review.
- New GUI-040 requirement added and traceability matrix updated.

## Implementation Notes

- Add a dedicated component, e.g. `frontend/src/components/ThreatMitigationReviewViewer.tsx`.
- Keep `ArtifactsViewer.tsx` focused on artifact representation and navigation.
- Ensure both surfaces read/write the same underlying decision store.
- Implement S12-029 after S12-021 decision-state model is finalized.

## Validation

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- frontend: npm run test -- --run src/components/ThreatMitigationReviewViewer.test.tsx
- manual: verify navigation separation, decision-state consistency, and downstream exclusion behavior for explicitly rejected items

## Closure Evidence

- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/ThreatMitigationReviewViewer.tsx
- frontend/src/App.tsx
- Requirements/10_GUI_Requirements.md (GUI-040 added)
- Requirements/04_Traceability_Matrix.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```

---

## S12-030

Title: Sprint 2026-12: Consolidate artifact navigation into header and migrate icons (remove in-panel nav)

Body:

```md
## Summary

The main display area still renders a secondary artifact navigation bar even though header
artifact navigation now exists. This duplicates controls, consumes vertical space, and
creates ambiguity about which navigation surface is authoritative.

This issue consolidates artifact-domain sub-navigation into the header by:
- Migrating existing in-panel artifact nav icons into the header nav.
- Adding two new header icons for threats-with-mitigations review and export.
- Removing the redundant in-panel artifact nav bar after migration.

Left nav remains global app/workspace navigation and is not removed by this issue.

## Related Requirements

- GUI-003 in Requirements/10_GUI_Requirements.md — Main Navigation and Workspace Structure
- GUI-005 in Requirements/10_GUI_Requirements.md — Threat Review Screen behavior
- GUI-006 in Requirements/10_GUI_Requirements.md — Results Export Interface
- S12-026 dependency — always-visible header Export navigation
- S12-029 dependency — threats-with-mitigations review navigation target
- New requirement: GUI-041 (or equivalent) — Header artifact nav consolidation
- New requirement: GUI-042 (or equivalent) — Header iconography contract for review/export controls

## Acceptance Criteria

- Header artifact navigation is the single authoritative artifact-domain sub-navigation surface in the main workspace area.
- Existing in-panel artifact icons are migrated to header nav without losing destinations.
- Main display area artifact nav bar is removed.
- New header icon routes to threats-with-mitigations review viewer.
- New header icon routes to export surface.
- Left nav remains available for global app/workspace routing without duplicating in-panel artifact nav behavior.
- Icon controls include accessible labels/tooltips and keyboard-focus support.
- Main content area gains additional vertical space after in-panel nav removal.
- GUI-041 and GUI-042 (or approved equivalent IDs) are added/updated in requirements.
- Traceability matrix updated with requirement-to-implementation links.

## Implementation Notes

- Keep header navigation as the only artifact-domain sub-navigation authority in the main workspace area.
- Preserve existing icon semantic mapping while moving from in-panel nav to header nav.
- Ensure active-route styling and route guards still behave correctly after migration.
- Sequence after S12-026 and S12-029 destination contracts are finalized.

## Validation

- frontend: npm run test -- --run src/components/AppHeader.test.tsx
- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- frontend: npm run test -- --run src/components/ThreatMitigationReviewViewer.test.tsx
- frontend: npm run test -- --run src/components/ResultsExport.test.tsx
- manual: verify header icon routing, verify in-panel nav removal, verify added content space, verify no loss of artifact/review/export reachability

## Closure Evidence

- frontend/src/App.tsx
- frontend/src/components/HeaderNavigation.tsx
- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/ThreatMitigationReviewViewer.tsx
- frontend/src/components/ResultsExport.tsx
- Requirements/10_GUI_Requirements.md (GUI-041/042 added or equivalent)
- Requirements/04_Traceability_Matrix.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
```
