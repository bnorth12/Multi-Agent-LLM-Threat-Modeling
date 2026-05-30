# Capability Function Architecture Traceability Matrix

## Purpose

Provide a single architecture-level capture area that traces capabilities and functional decomposition across abstraction levels and allocates each function to architecture elements.

This matrix is the architecture anchor for the left side of the end-to-end chain:

- capability
- function (L0/L1/L2)
- architecture allocation
- governing interfaces and data-flow responsibilities

## Usage Rule

- Add or update rows whenever a sprint introduces new capability/function scope.
- Keep IDs stable after publication; deprecate instead of renaming.
- Each function row must link to at least one requirement ID.
- Each row must reference capability/function IDs that exist in both `Capability_Hierarchy_Baseline.md` and `Function_Hierarchy_Registry.md`.

## Root Artifact Prerequisites

Traceability in this matrix is valid only when the upstream hierarchy artifacts are present and current:

- `docs/architecture/Capability_Hierarchy_Baseline.md`
- `docs/architecture/Function_Hierarchy_Registry.md`

## Matrix

| Capability ID | Capability Description | Function Level | Function ID | Function Description | Architecture Element(s) | Interface / Data-Flow Responsibility | Governing Requirement IDs | Notes |
|---|---|---|---|---|---|---|---|---|
| C01-ORCH-001 | LangGraph orchestrator routes execution with explicit next-state transitions | L1 | F-ORCH-STATE-TRANSITIONS | Advance run state through stage graph with deterministic transition control | Orchestrator runtime control plane | Stage-to-stage state transition control and checkpoint handoff | C01-ORCH-001, INT-005 | Seed row; extend as decomposition deepens |
| C12-HITL-001 | HITL gate controls enforce analyst intervention points | L1 | F-HITL-GATE-CONTROL | Pause/resume/reject control at governed gate boundaries | HITL gate service and orchestrator integration | Gate snapshot publication, decision ingestion, and resume path | HITL-001, HITL-009, GUI-032 | Seed row; extend with gate-level L2 rows |
| C11-LLM-001 | Live-model integration governs request budget, timeout, and retry behavior | L2 | F-C11_LLM_004-TRACE-L2 | Enforce live LLM timeout/retry budget with deterministic fallback behavior | LLM adapter runtime boundary (`src/threat_modeler/llm/openai_compatible_adapter.py`) | Runtime call budget enforcement and timeout/retry telemetry flow | C11-LLM-004, LLM-004 | Remediation slice R01-003 closed for architecture allocation coverage |
| C13-UI-001 | Wizard run continuity keeps the newly-created run selected and visible during initial polling | L2 | F-S12-016-GUI_037-L2 | Pin and preserve wizard-created run selection with operator-visible continuity cues | React HMI run selection shell | Run selection state continuity and wizard-created run marker propagation | GUI-037, RHMI-015 | Added for planned concept architecture trace closure |
| C10-A09-001 | Report writer generates required markdown sections and findings narrative | L2 | F-S12-025-C10_A09_001-L2 | Produce structured report sections with complete findings and mitigation narrative | Report writer subsystem (`agent_09`) | Approved artifact-to-report section mapping and output section integrity | C10-A09-001 | Added for planned concept architecture trace closure |
| C10-A09-001 | Report writer includes artifact-backed references and avoids stale diagram/report linkage | L2 | F-S12-025-C10_A09_002-L2 | Enforce report reference integrity for approved artifacts only | Report writer subsystem (`agent_09`) | Artifact reference resolution and section-level inclusion guardrails | C10-A09-002 | Added for planned concept architecture trace closure |
| C10-A09-001 | Report writer output supports downstream conversion and document-quality checks | L2 | F-S12-025-C10_A09_003-L2 | Preserve conversion-ready structure and deterministic formatting constraints | Report writer subsystem (`agent_09`) | Conversion compatibility and document structure invariants | C10-A09-003 | Added for planned concept architecture trace closure |
| C01-ORCH-001 | LangGraph-compatible execution mode support for routed state progression | L2 | F-C01_ORCH_002-L2 | Preserve equivalent stage routing semantics in langgraph-compatible orchestration mode | Orchestrator runtime execution mode adapter | Execution-mode transition contract and routed state continuity | C01-ORCH-002 | Added for as-built architecture trace closure |
| C01-ORCH-001 | Checkpoint persistence at stage boundaries | L2 | F-C01_ORCH_003-L2 | Persist and recover stage-level checkpoints after every orchestrator transition | Run manager and orchestrator checkpoint integration | Checkpoint write/read continuity across transitions | C01-ORCH-003 | Added for as-built architecture trace closure |
| C13-UI-001 | Paused-state timeline projection behavior for gate-controlled execution | L2 | F-GUI_003A-TRACE-L2 | Render paused gate state as paused (not failed) with completed-stage context | React HMI execution status projection | Paused-state projection and gate context rendering | GUI-003A | Added for as-built architecture trace closure |
| C13-UI-001 | Stage-selection controls with persistence and at-least-one-stage guardrail | L2 | F-GUI_012A-TRACE-L2 | Persist operator stage toggle selections and enforce non-empty enabled-stage set | React HMI configuration subsystem | Pipeline stage-selection policy and persistence behavior | GUI-012A | Added for as-built architecture trace closure |
| C13-UI-001 | Prompt-response correlation by prompt record identifier | L2 | F-GUI_029-TRACE-L2 | Display only response content matching selected prompt record and suppress stale responses | React HMI prompt diagnostics subsystem | Prompt/response record-key correlation and stale payload suppression | GUI-029 | Added for as-built architecture trace closure |
| C16-PRJ-001 | Visible-browser validation workflow for fixture upload verification | L2 | F-PRJ_024-TRACE-L2 | Execute visible-browser input upload validation against approved fixture sets | Browser-validation automation harness and HMI upload surface | Upload-path validation evidence and fixture compatibility verification | PRJ-024, VS-009 | Added for as-built architecture trace closure |
| C13-UI-001 | User interface control surface governance for gate and execution-page behavior | L2 | F-S12-011-GUI_030-L2 | S12-011 Requirement-Bound Decomposition | HITL gate ledger and execution page shell | Requirement-bound allocation for gate ledger and execution-page rationalization | GUI-030 | Focused remediation round closure for baseline guard coverage |
| C13-UI-001 | User interface continuity for runtime monitoring and status projection | L2 | F-S12-012-GUI_031-L2 | S12-012 Requirement-Bound Decomposition | Runtime monitoring panel and execution status projection | Requirement-bound allocation for paused-state continuity and monitoring status projection | GUI-031, RHMI-005 | Focused remediation round closure for baseline guard coverage |
| C13-UI-001 | User interface gate disposition and governance controls | L2 | F-S12-013-GUI_032-L2 | S12-013 Requirement-Bound Decomposition | HITL gate control surface | Requirement-bound allocation for gate-0 design disposition behavior | GUI-032 | Focused remediation round closure for baseline guard coverage |
| C13-UI-001 | User interface restart-safe execution artifact retrieval | L2 | F-S12-017-RHMI_016-L2 | S12-017 Requirement-Bound Decomposition | Run history retrieval and artifact access projection | Requirement-bound allocation for restart-safe completed-run artifact retrieval flows | RHMI-016 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime input validation and parsing safeguards | L2 | F-S12-018-RHMI_017-L2 | S12-018 Requirement-Bound Decomposition | React input ingestion and payload validation boundary | Requirement-bound allocation for file parsing parity and binary-injection guard behavior | RHMI-017 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime artifact-viewer state coupling integrity | L2 | F-S12-019-GUI_003C-L2 | S12-019 Requirement-Bound Decomposition | Artifact viewer state synchronization boundary | Requirement-bound allocation for viewer color-state coupling to gate and data acceptance state | GUI-003C, GUI-031 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime latency and token telemetry persistence controls | L2 | F-S12-020-GUI_015-L2 | S12-020 Requirement-Bound Decomposition | Runtime telemetry capture and persistence boundary | Requirement-bound allocation for stage latency and token-usage persistence behavior | GUI-015, INT-005, GUI-027 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime inline threat and mitigation review controls | L2 | F-S12-021-GUI_005-L2 | S12-021 Requirement-Bound Decomposition | Threat and mitigation inline review surface | Requirement-bound allocation for inline accept/reject controls and HITL-coupled review state | GUI-005, HITL-004, HITL-005, HITL-007, HITL-008 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime mermaid diagram exploration controls | L2 | F-S12-022-GUI_020-L2 | S12-022 Requirement-Bound Decomposition | Mermaid diagram lightbox boundary | Requirement-bound allocation for zoom/pan diagram interaction behavior | GUI-020, GUI-034, RHMI-010 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime watchdog stale-state governance | L2 | F-S12-023-GUI_026-L2 | S12-023 Requirement-Bound Decomposition | Execution timeline and watchdog state monitor | Requirement-bound allocation for stale-while-active watchdog detection and timeline projection | GUI-026, GUI-027, GUI-031, RHMI-005 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime final release gate control integrity | L2 | F-S12-024-HITL_006-L2 | S12-024 Requirement-Bound Decomposition | HITL final release gate controller | Requirement-bound allocation for gate-9 trigger and release-control continuity | HITL-006, HITL-008, GUI-030 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime report structure and TOC conformance controls | L2 | F-S12-025-INT_011-L2 | S12-025 Requirement-Bound Decomposition | Report generation and format conformance boundary | Requirement-bound allocation for report structure conformance and TOC fidelity | INT-011, PRJ-011 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime artifact export panel controls | L2 | F-S12-026-GUI_006-L2 | S12-026 Requirement-Bound Decomposition | Artifact export interaction boundary | Requirement-bound allocation for export panel behavior and governed artifact emission paths | GUI-006, GUI-007, GUI-023, GUI-024, PRJ-011, PRJ-017, INT-010, INT-011 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime mitigation viewer and export coverage controls | L2 | F-S12-027-INT_008-L2 | S12-027 Requirement-Bound Decomposition | Mitigation viewer and export interface boundary | Requirement-bound allocation for mitigation viewer presence and export readiness behavior | INT-008, GUI-042 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime optional prior canonical-graph ingestion | L2 | F-S12-028-PRJ_013-L2 | S12-028 Requirement-Bound Decomposition | Canonical graph intake and run bootstrap boundary | Requirement-bound allocation for optional prior canonical-graph run input behavior | PRJ-013, INT-002, HITL-010, GUI-039 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime split viewer decomposition for threat evidence | L2 | F-S12-029-GUI_005-L2 | S12-029 Requirement-Bound Decomposition | Threat artifact viewer and mitigation review viewer surfaces | Requirement-bound allocation for split-viewer decomposition and synchronized review behavior | GUI-005, INT-008, GUI-040 | Focused remediation round closure for baseline guard coverage |
| C16-PRJ-001 | Product runtime header navigation and artifact icon governance | L2 | F-S12-030-GUI_003-L2 | S12-030 Requirement-Bound Decomposition | Header navigation and artifact icon presentation layer | Requirement-bound allocation for navigation consolidation and artifact icon migration consistency | GUI-003, GUI-005, GUI-006, GUI-041, GUI-042 | Focused remediation round closure for baseline guard coverage |
| C01-ORCH-001 | Orchestration architecture disposition and baseline parity governance | L2 | F-S12-033-ORCH_001-L2 | S12-033 Requirement-Bound Decomposition | Orchestrator control plane and stage routing boundary | Requirement-bound allocation for langgraph orchestrator disposition and baseline parity controls | ORCH-001, INT-005, PRJ-001 | Focused remediation round closure for baseline guard coverage |
| C01-ORCH-001 | Sprint governance baseline hierarchy alignment for orchestrator traceability | L2 | F-S13-001-ORCH_001-L2 | S13-001 Requirement-Bound Decomposition | Governance hierarchy baseline and orchestrator traceability boundary | Requirement-bound allocation for sprint 2026-013 hierarchy alignment controls | ORCH-001, INT-005 | Focused remediation round closure for baseline guard coverage |

## Decomposition Guidance

- L0: mission or product outcome function.
- L1: subsystem behavior function.
- L2: implementation-proximate functional behavior used to constrain design and tests.

## Review Gate

Before implementation closeout for a slice, confirm:

- capability IDs are present
- governing function IDs are present
- architecture allocation is explicit
- requirement links are complete

## Remediation Slice Updates

- R01-003 (`C11-LLM-004`) updated to include explicit L2 allocation row and requirement compatibility alias linkage (`LLM-004`).
