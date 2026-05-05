# Issue: Sprint 2026-06 User Manual

## Sprint
2026-06

## Issue ID
S06-06

## GitHub Issue
TBD

## Owner Role
Documentation Owner and HMI Architect

## Description
Write and publish the end-user manual for the Multi-Agent LLM Threat Modeler tool. The manual must be usable by analysts who have no prior knowledge of the codebase and must cover all delivered functionality through Sprint 2026-06, including the Streamlit HMI screens, pipeline execution flow, HITL gate interaction workflow, results export, and model/prompt configuration.

## Background
Sprint 2026-05 delivered the HMI Architecture Blueprint defining screen inventory, navigation, shared components, and role-based access. Sprint 2026-06 (S06-01 through S06-05) delivers the first runnable pipeline and Streamlit screens. The user manual depends on those deliverables being functional and is the final documentation artifact required for operational readiness.

## Scope
- Tool overview: what the threat modeler does, the 9-agent pipeline, HITL governance model, and output artifacts (STIX bundle, Mermaid diagram, human report).
- Installation and setup: prerequisites, virtual environment, offline vs. hybrid model profiles, first-run configuration.
- Step-by-step workflow walkthrough:
  - Providing input (ICD spreadsheet, narrative document, or both) via GUI-001 (Input Entry Form)
  - Monitoring pipeline execution via GUI-003 (Pipeline Status Dashboard)
  - Reviewing stage outputs via GUI-004 (Stage Results Viewer)
  - Responding to HITL Gate 0 (Input Integrity), Gate 1 (Scope Confirmation), Gate 2 (Trust Boundary Approval) via GUI-002
  - Reviewing threats and mitigations via GUI-005
  - Exporting results via GUI-006 (Results Export Interface)
  - Saving and restoring run snapshots via GUI-007/008
- Configuration reference: model provider selection (GUI-012), connection details (GUI-013), connection validation (GUI-014), agent prompt editing (GUI-009/010).
- Role-based access guide: what Viewer, Analyst, PromptEditor, and Admin roles can do.
- Troubleshooting: common error states, Gate 0 trigger conditions, pipeline halt recovery, offline model fallback.
- Annotated screenshots for each major workflow step, sourced from `docs/screenshots/` (delivered by S06-05).
- Glossary: threat modeling terms, STRIDE categories, HITL gate terminology, STIX terminology.

## Acceptance Criteria
- User manual exists at `docs/User_Manual.md`.
- Manual contains a tool overview section explaining the 9-agent pipeline and HITL governance model.
- Manual contains installation and setup instructions reproducible by a new analyst from a clean environment.
- Manual contains step-by-step walkthrough for the primary analyst workflow (input → pipeline → HITL review → export).
- Manual contains HITL gate interaction guide covering Gate 0, Gate 1, and Gate 2 decision options (Accept As-Is, Accept Changes, Save Draft, Reject).
- Manual contains a role-based access reference table.
- Manual contains a troubleshooting section with at minimum 5 documented error scenarios.
- Manual includes annotated screenshots (or screenshot placeholders with captions) for each major workflow step.
- Manual includes a glossary.
- `docs/INDEX.md` is updated to reference the manual.

## Requirement Links
- PRJ-006 (HITL Governance)
- PRJ-009 (Operational Runbook)
- PRJ-012 (Role-Based Access)
- PRJ-016 (Analyst GUI)
- GUI-001 through GUI-014

## Blocking Relationships
- **Depends on:** S06-01 (Agent Pipeline Completeness) — pipeline must be runnable to document
- **Depends on:** S06-02 (HITL Gate Set 2) — HITL screens must exist to document and screenshot
- **Depends on:** S06-05 (Release & Operational Readiness) — screenshots must be captured before manual is finalized

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- HTML user manual delivered at `docs/user_manual/index.html` (primary — styled, sidebar nav, per-screen descriptions, HITL gate guide, glossary).
- Markdown user manual at `docs/User_Manual.md` (secondary — same content in plain Markdown).
- `docs/INDEX.md` updated to reference both manual locations.
- Manual covers: tool overview, 9-agent pipeline, HITL governance, installation, step-by-step workflow (SCR-004 Input Entry → SCR-001 Dashboard → HITL gates → export), gate interaction guide (Gates 0–2), role-based access table, troubleshooting (5+ scenarios), glossary.
- Screenshots embedded for SCR-001, SCR-002, SCR-003, SCR-004 screens.
- All 9 acceptance criteria met.
