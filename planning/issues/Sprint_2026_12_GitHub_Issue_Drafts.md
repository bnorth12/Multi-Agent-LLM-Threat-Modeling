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

## S12-012

Title: Sprint 2026-12: Persistent footer status and HITL-page monitoring continuity

Body:

```md
## Summary

Operators should be able to stay on the HITL Gate page while a run continues or resumes, with the persistent footer timeline providing centered plain-language status text across the application.

## Related Requirement

- GUI-031 in Requirements/10_GUI_Requirements.md

## Acceptance Criteria

- Resuming from a gate does not force navigation back to the execution page.
- Footer timeline shows centered plain-language run status.
- Backend/runtime state and footer status remain coherent for paused, running, and completed states.
- Sprint 2026-12 traceability and execution log are updated.

## Validation

- frontend: npm run test -- --run src/components/HITLGateManager.test.tsx
- PYTHONPATH=src python -m pytest Tests/test_hmi_backend_api.py -q

## Closure Evidence

- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- Requirements/10_GUI_Requirements.md
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
