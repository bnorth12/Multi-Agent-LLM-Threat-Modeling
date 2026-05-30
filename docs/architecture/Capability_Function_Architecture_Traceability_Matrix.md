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
