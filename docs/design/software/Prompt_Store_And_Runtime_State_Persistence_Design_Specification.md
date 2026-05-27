# Prompt Store and Runtime State Persistence Design Specification

Date: 2026-05-25
Version: 0.1 (Draft)
Status: Active software design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Logical_Decomposition.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`
- `Runtime_And_Orchestration_Design_Specification.md`
- `Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md`

## Purpose

Define the software design authority for persisted run state, prompt-version storage, checkpoint continuity, and recovery behavior so execution state and behavioral inputs remain durable, auditable, and recoverable across sessions.

## Related Requirements

- PRJ-007 Immutable Auditability: persisted prompts and run history must preserve trustworthy provenance.
- PRJ-019 Asynchronous Backend State Authority: runtime continuity and resume support depend on backend-owned authoritative state.
- PRJ-020 Live-Mode Integrity Halt on Provider Degradation: persisted state must capture failed live-mode integrity conditions rather than masking them.
- PRJ-021 Component Semantic Version Authority: persisted state and evidence need stable component-version references.
- PRJ-023 LangGraph Native Orchestration: persisted checkpoints must support the orchestrated runtime path without losing control-state integrity.
- INT-005 Stage Event Contract: persistence must retain stage transition and checkpoint information in a recoverable form.

## 1. Scope

This design covers:

- persisted run-state storage boundaries
- prompt store structure and version retention
- checkpoint and resume data requirements
- recovery behavior after interruption or restart
- auditability and provenance expectations for persisted control data

This design does not redefine orchestration control flow or canonical-graph mutation rules. Those remain governed by runtime and canonical-state design authorities.

## 2. Persistence Objectives

The persistence subsystem shall:

1. preserve enough execution state to resume or inspect controlled runs
1. retain prompt versions used by the agent subsystem during a run
1. support recovery after interruption without inventing missing state
1. distinguish authoritative persisted state from transient UI cache state

## 3. Persisted State Domains

### 3.1 Run-State Domain

The run-state domain holds execution-control information such as:

- run identifier
- current stage and status
- gate and decision checkpoints
- last validated canonical-state reference, including enough information to identify which authoritative canonical graph snapshot the runtime is allowed to resume from
- degraded or halted execution markers

### 3.2 Prompt Store Domain

The prompt store domain holds controlled prompt content and metadata such as:

- agent identifier
- prompt body or reference
- version identifier tied to the authoritative prompt revision used during execution
- timestamp and change provenance
- active versus historical designation

### 3.3 Recovery Metadata Domain

The recovery metadata domain holds the minimal information needed to determine whether resumption is allowed and where it may continue.

Examples:

- last completed validated stage
- unresolved HITL gate status
- blocked provider-validation status
- artifact packaging completion markers

## 4. Authority Rules

1. Persisted backend state is authoritative for run continuity and gate status.
1. UI session state may mirror persisted values but shall not supersede them.
1. Prompt versions associated with a run shall be preserved as evidence-bearing control inputs.
1. Recovery logic shall resume only from validated checkpoints, not from inferred transient state.

## 5. Checkpoint and Resume Design

Checkpoint persistence shall occur at controlled boundaries, including:

1. run initialization
1. completion of a validated stage
1. entry into a HITL gate hold condition
1. gate decision acceptance and continuation approval
1. final artifact packaging completion or terminal failure

Resume logic shall verify persisted checkpoint integrity before allowing the run to continue.

## 6. Failure and Recovery Behavior

If persisted state is missing, inconsistent, or stale, the system shall:

1. surface the recovery defect explicitly
1. prevent silent continuation from an unverified checkpoint
1. preserve still-valid evidence and prompt history where available
1. require explicit operator action when authoritative continuation cannot be proven

## 7. Implementation Surfaces

Expected implementation surfaces include:

- `src/threat_modeler/backend/run_manager.py`
- `src/threat_modeler/backend/prompt_store.py`
- persisted JSON or future persistence backends used for run and prompt continuity
- API surfaces that expose recovery and state-inspection operations

## 8. Verification Expectations

Verification for this design should include:

- restart and resume regression tests
- prompt-version retention checks
- checkpoint integrity tests for halt and recovery scenarios
- evidence checks confirming persisted state aligns with resumed execution behavior
