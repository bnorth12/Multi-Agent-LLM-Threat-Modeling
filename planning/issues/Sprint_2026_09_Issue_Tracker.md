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
- `planning/Sprint_2026_09_Traceability_Matrix.md`
- `planning/Release_Planning_2026_09.md`
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
| S09-4 | TBD | RC1 Release Documentation Preparation | Tech Writer and Release Manager | Open | Update User Manual with new viewers, capture screenshots, finalize release notes | 2026-05-09 BN: Added to release planning phase; executes May 23-27 |
| S09-5 | TBD | Manual RC1 Validation and Packaging | QA Lead and Release Manager | Open | Execute full manual RC validation campaign (functionality + docs), publish RC1 artifacts, and archive evidence bundle | 2026-05-09 BN: Updated to manual-only RC policy; no automation gating in RC1; target <=2 validation loops |
| S09-6 | TBD | RC1 Deployment Guide Delivery | Tech Writer and DevOps | Open | Create and validate deployment guide for installation, configuration, rollback, and operations handoff | 2026-05-09 BN: Added per release planning update |
| S09-7 | TBD | Markdown Viewer and Editor | UI Engineer and QA Lead | Open | Provide in-app markdown viewer/editor for tool-generated markdown files with preview and save validation | 2026-05-09 BN: Added for GUI-025 and documentation workflow support |

## 3. S09 Defect and Feature Log

| Defect ID | Severity | Area | Reproduction | Status | Fix Commit | Verification | Disposition Comment |
|-----------|----------|------|--------------|--------|------------|--------------|---------------------|
| D-S09-001 | Medium | STIX Viewer | Need dedicated STIX object viewer in GUI; current path is raw/export-only | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-018 |
| D-S09-002 | Medium | Canonical Graph Viewer | Need navigable canonical graph viewer; current path is raw/export-only | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-019 |
| D-S09-003 | Medium | Mermaid Diagram Viewer | Need in-app Mermaid render/source viewer for generated diagrams | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-020 |
| D-S09-004 | Medium | STRIDE Viewer and Export | Need dedicated STRIDE viewer plus standalone export artifact | Open | Pending | Pending | 2026-05-09 BN: New feature issue linked to GUI-021 and GUI-022 |
| D-S09-005 | Low | Results Export Quick Preview | Quick preview options do not function reliably for active run artifacts | Open | Pending | Pending | 2026-05-09 BN: Deferred from S08 closeout; linked to GUI-023 |
| D-S09-006 | Medium | Component/File Version Governance | Need component semantic version manifest and component-file version inventory for RC evidence and traceable release auditing | Open | Pending | Pending | 2026-05-09 BN: Added for PRJ-021, PRJ-022, GUI-024 enforcement |
| D-S09-007 | Medium | Deployment Guide for RC1 | Need release-specific deployment guide covering install, config, operations checks, and rollback | Open | Pending | Pending | 2026-05-09 BN: Added for RC1 documentation completeness |
| D-S09-008 | Medium | Manual RC Validation Campaign and Documentation Proof | Need full manual release-candidate validation evidence including user manual, product documentation, and deployment guide verification without automation gating | Open | Pending | Pending | 2026-05-09 BN: Added to enforce manual RC proof and bounded iteration policy |
| D-S09-009 | Medium | Markdown Viewer and Editor | Need integrated markdown viewer/editor for tool-managed files to support in-app updates during requirements and implementation phases | Open | Pending | Pending | 2026-05-09 BN: Added for GUI-025 and sprint documentation update workflows |
