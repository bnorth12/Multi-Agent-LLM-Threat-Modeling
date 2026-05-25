# Sprint 2026-09 Issue Tracker

This tracker is the canonical in-repo status view for Sprint 2026-09 planning and execution.

## 0. Execution Start Record

- S09 kickoff date: 2026-05-09
- Functional baseline tag: `baseline-s08-functional-2026-05-09`
- S09 branch: `feature/sprint-2026-09-kickoff`
- S09 kickoff PR: #37
- Execution mode: autonomous S09 implementation after planning baseline merge

## 1. Tracking Rules

- Update issue file status checkboxes first.
- Update this tracker table in the same commit.
- Include date and initials in Notes for each status change.
- Every issue must reference at least one requirement ID.
- Every resolved issue must include verification evidence.
- During both Requirements Phase and Implementation Phase, all S09 governance docs SHALL be reviewed and updated in-place as scope or acceptance criteria change.
- If a blocking issue is discovered during execution: document issue first, update requirements as needed, implement fix, and document resolution evidence before marking issue resolved.

## 1.1 S09 Documentation Governance (Requirements + Implementation)

The following documents are controlled artifacts for Sprint 2026-09 and SHALL be verified, edited, and updated during both phases:

- `Requirements/10_GUI_Requirements.md`
- `Requirements/01_Project_Requirements.md`
- `Requirements/05_Verification_Strategy.md`
- `Requirements/07_Release_Process.md`
- `Tests/Test_Plan.md`
- `planning/archives/2026-05/Sprint_2026_09_Traceability_Matrix.md`
- `planning/archives/2026-05/Release_Planning_2026_09.md`
- `Releases/Deployment_Guide_v1.0.0-rc1.md`

Phase checkpoints:

- Requirements Phase checkpoint: requirement IDs, acceptance criteria, and verification mappings are complete and internally consistent.
- Implementation Phase checkpoint: test cases, evidence instructions, and release readiness checklists reflect implemented behavior.

## 1.2 S09 New Requirements and Feature Baseline

S09 scope baseline that SHALL be tracked through completion:

- GUI-018 STIX Threat Model Viewer
- GUI-019 Canonical Graph Viewer
- GUI-020 Mermaid Diagram Viewer
- GUI-021 STRIDE Threat Model Viewer
- GUI-022 STRIDE Threat Model Export
- GUI-023 Results Export Quick Preview Functionality
- GUI-024 Component and File Version Visibility
- GUI-025 Markdown Viewer and Editor
- PRJ-021 Component Semantic Version Authority
- PRJ-022 Component File Version Traceability
- VS-008 Manual RC Validation Campaign

## 2. Sprint 2026-09 Checklist

| ID | GitHub Issue | Workstream | Owner Role | Status | Acceptance Criteria Summary | Notes |
|----|--------------|-----------|------------|--------|-----------------------------|-------|
| S09-1 | TBD | UI Artifact Viewer Expansion | HMI Architect and UI Engineer | Open | Add STIX, canonical graph, Mermaid, and STRIDE viewers in GUI | 2026-05-09 BN: Sprint seed issue set created from GUI-018 through GUI-022 |
| S09-2 | TBD | STRIDE Export Capability | UI Engineer and Test Lead | Open | Add standalone STRIDE export artifact and verification coverage | 2026-05-09 BN: Tracked under D-S09-004 |
| S09-3 | TBD | Results Export Quick Preview Defect | UI Engineer | Open | Fix non-functional quick preview controls in Results Export | 2026-05-09 BN: Deferred from S08 closeout to S09 as D-S09-005 |
| S09-4 | TBD | Streamlit Decoupling and Backend Execution Engine | Backend Engineer | **Closed** | backend/run_manager.py and backend/prompt_store.py delivered; ui/execution.py refactored; python -m threat_modeler entry point; 259 tests passing | 2026-05-11: Completed. See issue_2026_09_Streamlit_Decoupling_Backend_Engine.md. Requirement PRJ-019 implemented. |
| S09-5 | TBD | RC1 Release Documentation Preparation | Tech Writer and Release Manager | Open | Update User Manual with new viewers, capture screenshots, finalize release notes | 2026-05-09 BN: Added to release planning phase; executes May 23-27 |
| S09-6 | TBD | Manual RC1 Validation and Packaging | QA Lead and Release Manager | Open | Execute full manual RC validation campaign (functionality + docs), publish RC1 artifacts, and archive evidence bundle | 2026-05-10 BN: Updated policy: manual RC starts only after clean automated pass across all RC-included features; target <=2 manual validation loops |
| S09-7 | TBD | RC1 Deployment Guide Delivery | Tech Writer and DevOps | Open | Create and validate deployment guide for installation, configuration, rollback, and operations handoff | 2026-05-09 BN: Added per release planning update |
| S09-8 | TBD | Markdown Viewer and Editor | UI Engineer and QA Lead | Open | Provide in-app markdown viewer/editor for tool-generated markdown files with preview and save validation | 2026-05-09 BN: Added for GUI-025 and documentation workflow support |
| S09-9 | TBD | API Connection Validation Hardening | UI Engineer and QA Lead | Deferred | Validate configured API key/endpoint via authenticated provider request; reject invalid credentials during SCR-014 | 2026-05-10 BN: Manual smoke found false-positive validation with invalid key; deferred as D-S09-013 |
| S09-10 | TBD | Raw Payload Data Display Consistency | UI Engineer and QA Lead | Deferred | Ensure raw gate/preview controls render meaningful payload data or explicit empty-state messaging | 2026-05-10 BN: Manual smoke found empty raw payload display; deferred as D-S09-014 |
| S09-11 | TBD | Dark-Mode Raw Payload Contrast Readability | UI Engineer and QA Lead | Deferred | Ensure raw gate artifact payload text and labels are readable with sufficient contrast in dark mode | 2026-05-10 BN: Manual smoke found low-contrast raw payload text in dark mode; deferred as D-S09-015 |
| S09-12 | TBD | HITL Gate UI Display and Interaction | UI Engineer and QA Lead | Blocking | HITL gates must be displayed in Threat Review when pipeline is paused at gate; provide approve/reject/edit/resume controls | 2026-05-10 BN: Live 9-stage run with HITL gates showed gate paused in backend but not displayed in UI; critical blocker for gate workflow; deferred as D-S09-016 |

## 3. S09 Defect and Feature Log

| Defect ID | Severity | Area | Reproduction | Status | Fix Commit | Verification | Disposition Comment |
|-----------|----------|------|--------------|--------|------------|--------------|---------------------|
| D-S09-001 | Medium | STIX Viewer | Need dedicated STIX object viewer in GUI; current path is raw/export-only | Resolved | Pending commit | Tests/integration/test_stix_viewer_screen.py (8 passed) | 2026-05-10 BN: Verified in automated sweep `406 passed, 11 deselected` |
| D-S09-002 | Medium | Canonical Graph Viewer | Need navigable canonical graph viewer; current path is raw/export-only | Resolved | Pending commit | Tests/integration/test_canonical_graph_viewer.py (4 passed) | 2026-05-10 BN: Viewer + hierarchy/trust-boundary correctness tests implemented and passing |
| D-S09-003 | Medium | Mermaid Diagram Viewer | Need in-app Mermaid render/source viewer for generated diagrams | Resolved | Pending commit | Tests/integration/test_mermaid_viewer_screen.py (3 passed) | 2026-05-10 BN: Viewer with source toggle and invalid-source handling validated |
| D-S09-004 | Medium | STRIDE Viewer and Export | Need dedicated STRIDE viewer plus standalone export artifact | Resolved | Pending commit | Tests/integration/test_stride_viewer_screen.py + test_stride_export_artifact.py (5 passed) | 2026-05-10 BN: Viewer and standalone JSON/CSV export implemented and passing |
| D-S09-005 | Low | Results Export Quick Preview | Quick preview options do not function reliably for active run artifacts | Resolved | Pending commit | Tests/integration/test_results_export_quick_preview.py (2 passed) | 2026-05-10 BN: Quick preview coverage expanded and validated against current run payload expectations |
| D-S09-006 | Medium | Component/File Version Governance | Need component semantic version manifest and component-file version inventory for RC evidence and traceable release auditing | Resolved | Pending commit | Tests/integration/test_component_version_manifest.py + test_component_file_version_inventory.py + test_version_inventory_visibility.py (6 passed) | 2026-05-10 BN: Generators implemented, GUI visibility added, consistency checks passing |
| D-S09-007 | Medium | Deployment Guide for RC1 | Need release-specific deployment guide covering install, config, operations checks, and rollback | Resolved | Pending commit | Releases/Deployment_Guide_v1.0.0-rc1.md updated | 2026-05-10 BN: Guide aligned to automated-first policy and operational sections completed |
| D-S09-008 | Medium | Manual RC Validation Campaign and Documentation Proof | Need full manual release-candidate validation evidence including user manual, product documentation, and deployment guide verification after clean automated pass for all RC-included features | In Progress | Pending | Automated gate pass recorded in planning/archives/2026-05/Test_Execution_Summary_Sprint_2026_09.md | 2026-05-10 BN: Automated prerequisite satisfied; manual campaign remains pending user execution |
| D-S09-009 | Medium | Markdown Viewer and Editor | Need integrated markdown viewer/editor for tool-managed files to support in-app updates during requirements and implementation phases | Resolved | 0bd0b89 | Tests/integration/test_markdown_viewer_editor.py (14 passed) | 2026-05-10 BN: Verified in automated sweep `406 passed, 11 deselected` |
| D-S09-010 | Medium | Automated Test Collection and Browser Token Validation | Automated sweep encountered invalid legacy import paths and browser token-usage validation type handling failure | Resolved | Pending commit | Automated sweep: `pytest Tests/unit Tests/integration Tests/e2e -m "not llm_live"` -> 406 passed, 11 deselected | 2026-05-10 BN: Import and token-validation blockers fixed; non-manual gate clean |
| D-S09-013 | High | SCR-014 Connection Validation | Invalid API key is accepted as validated; no authenticated provider test call appears to be performed | Deferred | N/A | Manual smoke evidence (invalid key accepted by Validate Connection) | 2026-05-10 BN: Logged and deferred for next implementation slice before release sign-off |
| D-S09-014 | Medium | Raw Payload Display Content | Raw payload controls can open with empty/no useful data for selected gate or preview context | Deferred | N/A | Manual smoke evidence (raw gate section opened with no data) | 2026-05-10 BN: Deferred data-content gap; interaction blockers handled separately in active fix |
| D-S09-015 | Medium | Dark-Mode Raw Payload Contrast | Raw gate artifact payload text appears low-contrast in dark mode, reducing readability | Deferred | N/A | Manual smoke evidence (raw payload text difficult to read in dark mode) | 2026-05-10 BN: Deferred visual/readability adjustment for follow-up implementation before release sign-off |
| D-S09-016 | Critical | HITL Gate UI Display/Interaction | Pipeline paused at gate_1_scope_confirmation but gate not displayed in Threat Review HITL Gate Review section; no UI path to approve/reject gate | Blocking | N/A | Live 9-stage run with xAI provider; Home dashboard showed PAUSED status, Threat Review showed "No HITL gates recorded"; gate data not populated in UI | 2026-05-10 BN: Critical blocker prevents HITL workflow; gate exists in backend but unreachable through UI; requires gate data flow fix and Threat Review render update; deferred for immediate next fix slice before manual RC can proceed |
