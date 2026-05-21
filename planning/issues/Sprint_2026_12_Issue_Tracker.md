# Sprint 2026-12 Issue Tracker

Date: 2026-05-21
Status: Open for late-scope governance reconciliation
Sprint Goal: Keep Sprint 2026-12 React HMI/API delivery fully traceable through implementation, GitHub issue sync, and sprint-close closure evidence.

## 1. Sprint 2026-12 Late-Scope HMI/HITL Issues

| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |
|---|---|---|---|---|---|---|---|
| S12-011 | #64 | UI Workflow / HITL | P1 | In Review | Convert the HITL screen into an ordered gate ledger with lifecycle counts and clear row-level review behavior. | GUI-030 | frontend/src/components/HITLGateManager.tsx, frontend/src/components/HITLGateManager.test.tsx, Requirements/10_GUI_Requirements.md |
| S12-012 | #63 | UI Workflow / Monitoring | P1 | In Review | Keep operators on the HITL Gate page during execution and show centered plain-language footer status text across pages. | GUI-031 | frontend/src/App.tsx, frontend/src/components/ExecutionProgress.tsx, Requirements/10_GUI_Requirements.md |
| S12-013 | #67 | HITL Governance / Preflight | P1 | In Progress | Enforce Gate 0 preflight review with human-readable parsed input summaries before Stage 1 execution. | GUI-032 | src/threat_modeler/orchestrator.py, src/threat_modeler/hitl/service.py, frontend/src/components/HITLGateManager.tsx, Requirements/10_GUI_Requirements.md |
| S12-014 | #66 | HITL Governance / Stage Handoff | P1 | In Progress | Add mandatory post-Stage-1 normalization review gate and block Stage 2 until analyst decision with readable normalization summaries. | GUI-033 | src/threat_modeler/hitl/gate_engine.py, src/threat_modeler/orchestrator.py, frontend/src/components/HITLGateManager.tsx, frontend/src/components/ExecutionProgress.tsx, Requirements/10_GUI_Requirements.md |
| S12-015 | #68 | Artifact UX / Mermaid Review | P1 | In Review | Add parsed Mermaid diagram selector, split/diagram/text modes, editable source plus rendered preview, and visible `x of n - diagram name` indicator. | GUI-034, RHMI-010 | frontend/src/components/ArtifactsViewer.tsx, Requirements/10_GUI_Requirements.md, Requirements/11_React_HMI_Refactor_Requirements.md |
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

- Actual requirement updates completed for GUI-030 and GUI-031.
- Actual requirement updates completed for GUI-034 and RHMI-010.
- Sprint 2026-12 traceability updated to reference the implemented HMI/HITL refinement scope.
- GitHub synchronization completed for issues #63, #64, and #65.
- Final issue closure remains a Sprint 2026-12 closeout activity after the implementation PR and closure evidence are finalized, including assignment of a GitHub issue number for S12-015.
