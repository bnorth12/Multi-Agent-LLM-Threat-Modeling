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
