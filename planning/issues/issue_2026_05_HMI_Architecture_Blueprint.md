# Issue: Sprint 2026-05 HMI Architecture Blueprint

## Sprint
2026-05

## Issue ID
S05-10

## GitHub Issue
GH #17

## Owner Role
HMI Architect and Documentation Owner

## Description
Consolidate all GUI requirements (GUI-001 through GUI-014) into a unified HMI architecture blueprint that defines the overall look, feel, navigation model, shared component library, and role-based screen visibility before HITL gate UI implementation begins. This issue was added 2026-05-03 after recognizing that major new requirements (model provider configuration GUI-012–014, agent prompt editor GUI-009–010, HITL gate screens GUI-002, export interfaces GUI-006–008) collectively define an HMI that must be architected holistically before individual screens are built.

## Background
The following GUI requirements have been defined and require consolidation into a coherent HMI design:
- GUI-001: Input Entry Form
- GUI-002: HITL Gate Screens (multiple gates)
- GUI-003: Pipeline Status Dashboard
- GUI-004: Stage Results Viewer
- GUI-005: Threat and Mitigation Review Screen
- GUI-006: Results Export Interface
- GUI-007: Run Snapshot Export
- GUI-008: Run Snapshot Restore
- GUI-009: Agent Prompt Editor
- GUI-010: Agent Prompt Version History
- GUI-011: Role-Enforced GUI Access Control
- GUI-012: Model Provider Selection Screen (new)
- GUI-013: Model Connection Details Configuration (new)
- GUI-014: Model Connection Validation (new)

## Scope
- Define the overall HMI application structure: primary navigation (tabs, drawers, or pages), screen hierarchy, and transition flows.
- Identify shared UI components used across multiple screens (e.g., status banners, decision action bars, artifact viewers, export controls, role-gated button states).
- Define role-based screen visibility and action availability consistent with INT-013 and GUI-011.
- Define the configuration section that groups GUI-009, GUI-010, GUI-012, GUI-013, GUI-014 as a unified settings/configuration area.
- Define the analysis workflow section that groups GUI-001, GUI-003, GUI-004, GUI-005 as the primary analyst pipeline workflow.
- Define the HITL review section that groups GUI-002 (all gate instances) with audit trail access.
- Define the results and archive section that groups GUI-006, GUI-007, GUI-008.
- Create navigation flow diagrams using Mermaid for the primary analyst workflows.
- Create screen inventory table cross-referencing GUI requirement IDs to screen names and layout areas.
- Specify UI technology choice (framework recommendation: Streamlit for MVP, extensible to React/Qt for production).
- Define state management model: which HMI data comes from pipeline API, which is local UI state.

## Acceptance Criteria
- HMI architecture blueprint document exists at docs/HMI_Architecture_Blueprint.md.
- Blueprint contains a screen inventory table mapping all GUI-001 through GUI-014 to their location in the HMI.
- Blueprint defines primary navigation structure with at least one Mermaid flow diagram.
- Blueprint defines shared component patterns for at minimum: status indicator, action bar (approve/reject/edit), artifact viewer, and role-gated button.
- Blueprint explicitly calls out the ordering dependency: configuration screens (GUI-012–014) must be reachable before pipeline run initiation.
- Blueprint is acknowledged as the design authority for S05-04 HITL gate screen implementation.
- Requirements/10_GUI_Requirements.md and docs/INDEX.md are updated to reference the blueprint.

## Requirement Links
- PRJ-006 (HITL Governance)
- PRJ-008 (Configurable Model Selection)
- PRJ-012 (Role-Based Access)
- PRJ-016 (Analyst GUI)
- PRJ-017 (Snapshot Portability)
- PRJ-018 (Agent Prompt Configurability)
- INT-013 (Authorization Contract)
- INT-015 (Model Connection Contract)
- GUI-001 through GUI-014

## Blocking Relationships
- **Blocks:** S05-04 (HITL Gate Set 1) — gate screens must conform to HMI framework
- **Extends:** S05-06 (Documentation Synchronization) — blueprint is part of S05-06 deliverables
- **Depends on:** Requirements/10_GUI_Requirements.md complete (done)

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Progress Notes
2026-05-03 BN: docs/HMI_Architecture_Blueprint.md created (v0.1). Covers §1 Purpose, §2 Technology (Streamlit MVP), §3 Application Structure (sidebar nav), §4 Screen Inventory (SCR-001 to SCR-014), §5 Navigation Flows (3 Mermaid diagrams), §6 Shared Components (6 patterns), §7 Role-Based Access, §8 State Management, §9 Wireframes, §10 S05-04 implementation notes, §11 Requirements cross-reference. docs/INDEX.md and Requirements/10_GUI_Requirements.md updated to reference blueprint.
