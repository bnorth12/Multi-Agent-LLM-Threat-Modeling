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
