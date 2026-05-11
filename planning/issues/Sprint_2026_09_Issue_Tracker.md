# Sprint 2026-09 Issue Tracker

This tracker is the canonical in-repo status view for Sprint 2026-09 planning and execution.

## 1. Tracking Rules

- Update issue file status checkboxes first.
- Update this tracker table in the same commit.
- Include date and initials in Notes for each status change.
- Every issue must reference at least one requirement ID.
- Every resolved issue must include verification evidence.

## 2. Sprint 2026-09 Checklist

| ID | GitHub Issue | Workstream | Owner Role | Status | Acceptance Criteria Summary | Notes |
|----|--------------|-----------|------------|--------|-----------------------------|-------|
| S09-1 | TBD | UI Artifact Viewer Expansion | HMI Architect and UI Engineer | Open | Add STIX, canonical graph, Mermaid, and STRIDE viewers in GUI | 2026-05-09 BN: Sprint seed issue set created from GUI-018 through GUI-022 |
| S09-2 | TBD | STRIDE Export Capability | UI Engineer and Test Lead | Open | Add standalone STRIDE export artifact and verification coverage | 2026-05-09 BN: Tracked under D-S09-004 |
| S09-3 | TBD | Results Export Quick Preview Defect | UI Engineer | Open | Fix non-functional quick preview controls in Results Export | 2026-05-09 BN: Deferred from S08 closeout to S09 as D-S09-005 |
| S09-4 | TBD | Streamlit Decoupling and Backend Execution Engine | Backend Engineer | **Closed** | backend/run_manager.py and backend/prompt_store.py delivered; ui/execution.py refactored; python -m threat_modeler entry point; 259 tests passing | 2026-05-11: Completed. See issue_2026_09_Streamlit_Decoupling_Backend_Engine.md. Requirement PRJ-019 implemented. |

## 3. S09 Defect and Feature Log

| Defect ID | Severity | Area | Reproduction | Status | Fix Commit | Verification | Disposition Comment |
|-----------|----------|------|--------------|--------|------------|--------------|---------------------|
| D-S09-001 | Medium | STIX Viewer | Need dedicated STIX object viewer in GUI; current path is raw/export-only | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-018 |
| D-S09-002 | Medium | Canonical Graph Viewer | Need navigable canonical graph viewer; current path is raw/export-only | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-019 |
| D-S09-003 | Medium | Mermaid Diagram Viewer | Need in-app Mermaid render/source viewer for generated diagrams | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-020 |
| D-S09-004 | Medium | STRIDE Viewer and Export | Need dedicated STRIDE viewer plus standalone export artifact | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-021 and GUI-022 |
| D-S09-005 | Low | Results Export Quick Preview | Quick preview options do not function reliably for active run artifacts | Open | Pending | Pending | 2026-05-09 BN: Deferred from S08 closeout; linked to GUI-023 |
