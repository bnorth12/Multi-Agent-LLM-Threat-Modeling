# Sprint 2026-12 Issue Tracker

Date: 2026-05-21
Status: Open for late-scope governance reconciliation
Sprint Goal: Keep Sprint 2026-12 React HMI/API delivery fully traceable through implementation, GitHub issue sync, and sprint-close closure evidence.

## 0. S12 Closeout Matrix (Updated 2026-05-26)

This matrix provides owner assignment, target close date, and defer disposition for all active S12 scope.
Minor findings may be deferred only when logged with explicit next-sprint intake linkage.

| ID | GitHub Issue | Current Status | Owner | Target Close | Disposition |
|---|---|---|---|---|---|
| S12-011 | #64 | In Review | bnorth12 | 2026-05-28 | Close in Sprint 2026-12 after evidence refresh |
| S12-012 | #63 | In Review | bnorth12 | 2026-05-28 | Close in Sprint 2026-12 after evidence refresh |
| S12-013 | #67 | In Progress | bnorth12 | 2026-05-31 | Complete implementation and close |
| S12-014 | #66 | Closed | bnorth12 | 2026-05-26 | Closed with Sprint 2026-12 evidence and requirement trace links |
| S12-015 | #68 | In Review | bnorth12 | 2026-05-28 | Close in Sprint 2026-12 after evidence refresh |
| S12-016 | #69 | In Review | bnorth12 | 2026-05-28 | Close in Sprint 2026-12 after evidence refresh |
| S12-017 | #70 | In Review | bnorth12 | 2026-05-28 | Close in Sprint 2026-12 after evidence refresh |
| S12-018 | #71 | In Review | bnorth12 | 2026-05-29 | Close with evidence refresh |
| S12-019 | #72 | Proposed | bnorth12 | 2026-06-07 | Defer to Sprint 2026-13 Wave 1 |
| S12-020 | #73 | Proposed (Post-Run) | bnorth12 | 2026-06-10 | Defer to Sprint 2026-13 Wave 3 |
| S12-021 | #74 | Proposed (Post-Run) | bnorth12 | 2026-06-10 | Defer to Sprint 2026-13 Wave 2 |
| S12-022 | #75 | Proposed (Post-Run) | bnorth12 | 2026-06-12 | Defer to Sprint 2026-13 Wave 2 |
| S12-023 | #76 | Proposed (Post-Run) | bnorth12 | 2026-06-07 | Defer to Sprint 2026-13 Wave 1 |
| S12-024 | #77 | Proposed (Post-Run) | bnorth12 | 2026-06-07 | Defer to Sprint 2026-13 Wave 1 |
| S12-025 | #78 | Proposed (Post-Run) | bnorth12 | 2026-06-07 | Defer to Sprint 2026-13 Wave 1 |
| S12-026 | #79 | Closed | bnorth12 | 2026-05-26 | Closed as non-blocking RC1 catch-up disposition; residual refinements may continue post-RC |
| S12-027 | #80 | Closed | bnorth12 | 2026-05-26 | Closed after mitigations viewer plus export control delivery |
| S12-028 | #81 | Proposed (Post-Run) | bnorth12 | 2026-06-14 | Defer to Sprint 2026-13 Wave 3 |
| S12-029 | #82 | Proposed (Post-Run) | bnorth12 | 2026-06-12 | Defer to Sprint 2026-13 Wave 2 |
| S12-030 | #83 | Proposed (Post-Run) | bnorth12 | 2026-06-12 | Defer to Sprint 2026-13 Wave 2 |
| S12-031 | #84 | In Progress | bnorth12 | 2026-06-02 | Complete implementation and close |
| S12-032 | #85 | Proposed (Post-Run) | bnorth12 | 2026-06-14 | Defer to Sprint 2026-13 Wave 3 |
| D-S12-011 | #65 | Proposed | bnorth12 | 2026-06-05 | Defer decision to Sprint 2026-13 governance review |

### Defer Documentation Rule

- Any deferred minor finding must be recorded in `planning/Sprint_2026_13_Skills_Layer_and_Avionics_Specialization.md` and linked from this tracker row before Sprint 2026-12 closure.
- Deferred items must include: rationale, risk level, verification impact, and explicit next-sprint owner.

## 1. Sprint 2026-12 Late-Scope HMI/HITL Issues

| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |
|---|---|---|---|---|---|---|---|
| S12-011 | #64 | UI Workflow / HITL | P1 | In Review | Convert the HITL screen into an ordered gate ledger with lifecycle counts and clear row-level review behavior. | GUI-030 | frontend/src/components/HITLGateManager.tsx, frontend/src/components/HITLGateManager.test.tsx, Requirements/10_GUI_Requirements.md |
| S12-012 | #63 | UI Workflow / Monitoring | P1 | In Review | Keep operators on the HITL Gate page during execution, show centered plain-language footer status text across pages, restore timeline-adjacent watchdog heartbeat telemetry, and restore an animated header running indicator while a stage is active. | GUI-031, RHMI-005 | frontend/src/App.tsx, frontend/src/App.test.tsx, frontend/src/components/ExecutionProgress.tsx, frontend/src/components/ExecutionProgress.test.tsx, Requirements/10_GUI_Requirements.md, Requirements/11_React_HMI_Refactor_Requirements.md |
| S12-013 | #67 | HITL Governance / Preflight | P1 | In Progress | Enforce Gate 0 preflight review with human-readable parsed input summaries before Stage 1 execution. | GUI-032 | src/threat_modeler/orchestrator.py, src/threat_modeler/hitl/service.py, frontend/src/components/HITLGateManager.tsx, Requirements/10_GUI_Requirements.md |
| S12-014 | #66 | HITL Governance / Stage Handoff | P1 | Closed | Mandatory post-Stage-1 normalization review gate blocks Stage 2 until analyst decision and exposes readable normalization summaries. | GUI-033 | src/threat_modeler/hitl/gate_engine.py, src/threat_modeler/orchestrator.py, frontend/src/components/HITLGateManager.tsx, frontend/src/components/ExecutionProgress.tsx, Requirements/10_GUI_Requirements.md |
| S12-015 | #68 | Artifact UX / Mermaid Review | P1 | In Review | Add parsed Mermaid diagram selector, split/diagram/text modes, editable source plus rendered preview, and visible `x of n - diagram name` indicator. | GUI-034, RHMI-010 | frontend/src/components/ArtifactsViewer.tsx, Requirements/10_GUI_Requirements.md, Requirements/11_React_HMI_Refactor_Requirements.md |
| S12-016 | #69 | Run Selection UX / Wizard Continuity | P1 | In Review | Ensure setup-wizard run creation pins and auto-selects the exact new run ID, add temporary `Created by wizard` row badge, and keep nav/status surfaces visible during first polling cycles. | GUI-037, RHMI-015 | frontend/src/App.tsx, frontend/src/App.test.tsx, scripts/live_browser_e2e_smoke_react.py, Requirements/10_GUI_Requirements.md, Requirements/11_React_HMI_Refactor_Requirements.md |
| S12-017 | #70 | Runtime Persistence / Artifact Retrieval | P1 | In Review | Preserve artifact endpoint availability for completed or paused runs after backend restart by persisting and restoring restorable runtime state (no run-list ghost entries). | RHMI-016 | src/threat_modeler/backend/run_manager.py, src/threat_modeler/server/api.py, Requirements/11_React_HMI_Refactor_Requirements.md, Requirements/12_React_HMI_Traceability_To_Tests.md |
| S12-018 | #71 | Input Ingestion / File Injection Guard | P1 | In Review | Restore React input-ingestion parity with Streamlit by parsing CSV/XLSX uploads into structured table rows and preventing raw spreadsheet binary payload injection into `initial_state.raw_text`, which degraded Agent 01 parsing and downstream trust-boundary/STRIDE/threat completeness for full UAS suite runs. | RHMI-017 | frontend/src/App.tsx, frontend/src/api/client.ts, frontend/package.json, Requirements/11_React_HMI_Refactor_Requirements.md, Requirements/12_React_HMI_Traceability_To_Tests.md |
| S12-019 | #72 | Artifact UX / Gate-State Coupling | P1 | Proposed | Ensure artifact-view navigation and viewer status colors update deterministically when artifact data becomes available and when related HITL gates transition to accepted, rather than remaining in stale pre-availability state. | GUI-003C, GUI-031, Pending latest color-state requirement ID mapping | frontend/src/App.tsx, frontend/src/components/ArtifactsViewer.tsx, frontend/src/components/HITLGateManager.tsx, Requirements/10_GUI_Requirements.md, Requirements/11_React_HMI_Refactor_Requirements.md |
| S12-020 | #73 | Runtime Telemetry / Stage Latency Persistence | P1 | Proposed (Post-Run) | Track per-stage LLM latency from prompt dispatch to model response and persist those timing data points with per-stage token usage in run records for trend analysis, triage, and governance evidence. | GUI-015, INT-005, GUI-027, Pending requirement ID for persisted stage latency metrics | src/threat_modeler/services/openai_compatible_adapter.py, src/threat_modeler/backend/run_manager.py, src/threat_modeler/server/api.py, frontend/src/components/TokenUsageView.tsx, Requirements/10_GUI_Requirements.md, Requirements/02_Interface_Requirements.md |
| S12-021 | #74 | Artifact UX / Per-Item Threat & Mitigation Review | P1 | Proposed (Post-Run) | Add threat detail dialog (click to open), inline mitigation population once the mitigation stage completes, and per-item accept/reject decision controls for threats and mitigations. Pending items default to accepted so the pipeline never blocks; only explicitly rejected items are excluded from diagram and report generation. | GUI-005, HITL-004, HITL-005, HITL-007, HITL-008, Pending new GUI-005 extension IDs | frontend/src/components/ArtifactsViewer.tsx, src/threat_modeler/backend/run_manager.py, src/threat_modeler/server/api.py, src/threat_modeler/orchestrator.py, Requirements/10_GUI_Requirements.md, Requirements/03_HITL_Requirements.md |
| S12-022 | #75 | Artifact UX / Mermaid Diagram Lightbox Zoom and Pan | P2 | Proposed (Post-Run) | Clicking a Mermaid diagram preview opens a full-viewport dialog. The dialog supports mouse-wheel zoom in/out, click-and-drag pan, and a reset-to-fit action. The inline preview panel is unchanged. | GUI-020, GUI-034, RHMI-010 | frontend/src/components/ArtifactsViewer.tsx, frontend/src/components/MermaidLightbox.tsx (new), Requirements/10_GUI_Requirements.md |
| S12-023 | #76 | Runtime Stability / Watchdog Stale + Timeline Stuck Active | P1 | Proposed (Post-Run) | Run transitioned to Completed before stage terminalization was resolved, and the report writer stage never received a proper completion trigger (LLM completion + artifact persistence), leaving timeline state blue and watchdog telemetry stale against a non-terminal stage. This is coupled with S12-024 Gate 9 sequencing defect. | GUI-026, GUI-027, GUI-031, RHMI-005 (plus S12-024 coupling) | src/threat_modeler/orchestrator.py, src/threat_modeler/backend/run_manager.py, src/threat_modeler/services/openai_compatible_adapter.py, frontend/src/components/ExecutionProgress.tsx, Requirements/10_GUI_Requirements.md |
| S12-024 | #77 | HITL Compliance / Gate 9 Final Release Gate Not Firing | P1 | Proposed (Post-Run) | Pipeline completed and report was published without HITL Gate 9 (Final Release Gate, HITL-006) firing. Run transitioned to Completed without an analyst approve/reject decision for the final gate. No signed decision record exists for this run's final gate. Includes explicit governance synchronization work: update HITL requirements + traceability mapping and synchronize all S12-024 issue artifacts with those requirement updates. | HITL-006, HITL-008, GUI-030, HITL gate-index mapping sync | src/threat_modeler/orchestrator.py, src/threat_modeler/backend/run_manager.py, frontend/src/components/HITLGateManager.tsx, Requirements/03_HITL_Requirements.md, Requirements/10_GUI_Requirements.md, Requirements/04_Traceability_Matrix.md, planning/issues/issue_2026_12_S12_024_HITL_Gate_9_Final_Release_Gate_Not_Firing.md |
| S12-025 | #78 | Report Quality / Generated Report Missing TOC and Section Structure | P1 | Proposed (Post-Run) | Generated markdown report is poorly formatted and does not follow the required table of contents structure. Required sections (executive summary, scope, boundaries, findings, mitigations, residual risk) are absent or malformed, approved diagram references are not reliably represented, and formatting readability is inconsistent. Diagram handling for this issue is reference-only (embedding deferred). Prompt engineering defect in agent_09 configuration. | C10-A09-001, C10-A09-002, C10-A09-003, INT-011, PRJ-011 | data/models/ (agent_09 prompt), src/threat_modeler/agents/agent_09_report_writer.py, Requirements/Components/C10_Agent_09_Report_Requirements.md, Requirements/02_Interface_Requirements.md |
| S12-026 | #79 | Artifact Export Panel Partial Delivery and Remaining Gaps | P1 | Closed | Core export surface is delivered and accepted for RC1; remaining token usage export, inline quick preview, snapshot export, and export-surface version inventory are treated as non-blocking catch-up scope. | GUI-006, GUI-007, GUI-023, GUI-024, PRJ-011, PRJ-017, INT-010, INT-011 | frontend/src/App.tsx, frontend/src/components/ResultsExportPanel.tsx, frontend/src/api/client.ts, src/threat_modeler/server/api.py, Requirements/10_GUI_Requirements.md, Requirements/04_Traceability_Matrix.md |
| S12-027 | #80 | Mitigations Artifact Viewer and Export | P1 | Closed | Mitigations are now reviewable in a dedicated React viewer and exportable through the Results Export surface (`Export Mitigations JSON`). | INT-008, GUI-042 | frontend/src/components/MitigationViewer.tsx, frontend/src/components/ResultsExportPanel.tsx, frontend/src/App.tsx, Requirements/10_GUI_Requirements.md |
| S12-028 | #81 | Prior Canonical Graph as Optional Run Input for Incremental Enrichment | P1 | Proposed (Post-Run) | New runs cannot optionally ingest a prior canonical graph from an earlier run of the same system. The intended behavior is baseline + new input: preserve approved prior elements, then add/update only new details from the new run. PRJ-013 requires this incremental enrichment flow, but the setup wizard input and orchestrator baseline injection path do not exist yet. | PRJ-013, INT-002, HITL-010; new GUI-039 req needed | frontend/src/components/ (setup wizard), src/threat_modeler/orchestrator.py, src/threat_modeler/backend/run_manager.py, src/threat_modeler/server/api.py, Requirements/10_GUI_Requirements.md, Requirements/02_Interface_Requirements.md, Requirements/04_Traceability_Matrix.md |
| S12-029 | #82 | Artifact UX / Split Threat Artifact Viewer and Threats-with-Mitigations Review Viewer | P1 | Proposed (Post-Run) | Keep the existing threat artifact viewer for read-focused artifact inspection, and add a separate threats-with-mitigations review viewer for workflow decisions. This separates artifact rendering concerns from analyst review controls so both surfaces can evolve independently while sharing a single decision-state source. | GUI-005, INT-008, S12-021 dependency; new GUI-040 req needed | frontend/src/components/ArtifactsViewer.tsx, frontend/src/components/ThreatMitigationReviewViewer.tsx (new), frontend/src/App.tsx, Requirements/10_GUI_Requirements.md, Requirements/04_Traceability_Matrix.md |
| S12-030 | #83 | UI Navigation / Header Artifact Nav Consolidation and Icon Migration | P1 | Proposed (Post-Run) | Remove the redundant in-panel artifact nav bar after migrating its icons into the header artifact navigation. Add two new header icons for threats-with-mitigations review and export. This makes header nav authoritative for artifact-domain sub-navigation (while left nav remains global app navigation), opens additional content space, and requires requirement/traceability synchronization for new nav/icon contracts. | GUI-003, GUI-005, GUI-006, S12-026, S12-029; new GUI-041 and GUI-042 req needed | frontend/src/App.tsx, frontend/src/components/HeaderNavigation.tsx, frontend/src/components/ArtifactsViewer.tsx, frontend/src/components/ThreatMitigationReviewViewer.tsx, frontend/src/components/ResultsExport.tsx, Requirements/10_GUI_Requirements.md, Requirements/04_Traceability_Matrix.md |
| S12-031 | #84 | Timeline UX / Parse-Phase Segment Visibility and Gate Readiness Coupling | P1 | In Progress | Add a narrow parsing segment before each gate boundary (including Gate 0) on the execution timeline, with brown for parse-in-progress and green for parse-complete. Ensure the visual state is coherent with readiness-coupled gate-open behavior so analysts can distinguish parsing from gate review without race ambiguity. | GUI-043, GUI-031, HITL-012 | frontend/src/components/ExecutionProgress.tsx, frontend/src/components/ExecutionProgress.test.tsx, src/threat_modeler/orchestrator.py, Requirements/10_GUI_Requirements.md, Requirements/03_HITL_Requirements.md |
| S12-032 | #85 | Diagram Generation / Mermaid Decomposition Depth Collapse | P1 | Proposed (Post-Run) | Complex canonical graphs are emitting only Level 0 Mermaid output (or too few levels), indicating parser contract and decomposition-budget misalignment in Agent 08. Enforce scalable level markers, robust parser handling, and minimum complexity-based decomposition so reviewers receive usable multi-level diagram coverage. | C10-A08-001, C10-A08-002, C10-A08-003, INT-009, PRJ-011 | src/threat_modeler/agents/agent_08_diagram_generator.py, src/threat_modeler/backend/prompt_store.py, Tests/unit/test_agent_prompt_contracts.py, Tests/integration/test_agent_pipeline_completeness.py, Requirements/Components/C10_Agent_08_Diagram_Requirements.md |
| S12-ADMIN-001 | N/A | Repo Administration / Dev Stack Operations | P3 | Logged | Cross-reference entry for operational use of `scripts/restart_dev_stack.ps1` to restart backend/frontend with readiness checks; see execution log Update 10 (2026-05-22). | Sprint governance evidence linkage | scripts/restart_dev_stack.ps1, planning/Sprint_2026_12_Execution_Log.md |
| D-S12-011 | #65 | UX Rationalization | P2 | Proposed | Decide whether the Execution page is retained, repurposed, or removed now that footer monitoring and gate-resident workflow exist. | Pending follow-on requirement | frontend/src/App.tsx, planning/issues/issue_2026_12_S12_011_HITL_Gate_Ledger_And_Execution_Page_Rationalization.md |

## 2. Closure Policy

Each Sprint 2026-12 issue is only closed when all are true:

- In-repo implementation is merged.
- The actual requirement documents are updated.
- Sprint 2026-12 traceability documentation references the actual requirement IDs.
- Verification evidence is recorded with exact test commands and outcomes.
- A matching GitHub issue exists and is closed with PR/commit/evidence references.

## 3. GitHub Sync Checklist

- Create or update the matching GitHub issue for each tracker row.
- Replace `TBD` in the `GitHub Issue` column with the repository issue number.
- Link the implementation PR using closing keywords.
- On sprint close, add closure comments referencing:
  - `planning/Sprint_2026_12_Traceability_Matrix.md`
  - `planning/Sprint_2026_12_Execution_Log.md`
  - verification commands and pass results

## 4. Current State

- Actual requirement updates completed for GUI-030, GUI-031, and RHMI-005 runtime monitoring continuity refinement.
- Actual requirement updates completed for GUI-034 and RHMI-010.
- Actual requirement updates completed for GUI-037 and RHMI-015.
- Actual requirement updates completed for RHMI-016 (restart-safe artifact addressability).
- Actual requirement updates completed for RHMI-017 (React CSV/XLSX parsing parity and binary spreadsheet injection guard).
- Sprint 2026-12 traceability updated to reference the implemented HMI/HITL refinement scope.
- GitHub synchronization completed for issues #63, #64, #65, #66, #68, and #69.
- GitHub synchronization completed for S12-018 as issue #71.
- GitHub synchronization completed for S12-019 as issue #72.
- GitHub synchronization completed for S12-020 as issue #73.
- GitHub synchronization completed for S12-021 as issue #74.
- GitHub synchronization completed for S12-022 as issue #75.
- GitHub synchronization completed for S12-023 as issue #76.
- GitHub synchronization completed for S12-024 as issue #77.
- GitHub synchronization completed for S12-025 as issue #78.
- GitHub synchronization completed for S12-026 as issue #79.
- Issue #79 closed on 2026-05-26 as a non-blocking catch-up disposition for RC1 progression, with residual scope retained as post-RC refinement work if needed.
- GitHub synchronization completed for S12-027 as issue #80.
- Issue #80 closed on 2026-05-26 after mitigations viewer plus export-control delivery evidence was recorded.
- GitHub synchronization completed for S12-028 as issue #81.
- GitHub synchronization completed for S12-029 as issue #82.
- GitHub synchronization completed for S12-030 as issue #83.
- GitHub synchronization completed for S12-031 as issue #84.
- GitHub synchronization completed for S12-032 as issue #85.
- S12-ADMIN-001 logged as sprint administration cross-reference for dev stack restart evidence in `planning/Sprint_2026_12_Execution_Log.md` Update 10.
- Remediation branch planning for issue #67 is captured in `planning/Sprint_Remediation_Issue_67.md` and is the authoritative issue-keyed remediation slice.
- Final issue closure remains a Sprint 2026-12 closeout activity after the implementation PR and closure evidence are finalized, including assignment of a GitHub issue number for S12-015.
