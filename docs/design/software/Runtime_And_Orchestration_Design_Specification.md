# Runtime and Orchestration Design Specification

Date: 2026-05-24
Version: 0.1 (Draft)
Status: Active software design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Structural_Decomposition.md`
- `../../architecture/Multi_Agent_Logical_Decomposition.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`

## Purpose

Define the software design for the runtime control plane that executes, governs, pauses, resumes, validates, and packages a multi-agent threat-modeling run.

## Related Requirements

- PRJ-006 HITL Governance: the runtime must pause, collect, and apply governed human decisions at required control points.
- PRJ-011 Export Artifact Set: orchestration must close each run with the expected export bundle or an explicit degraded-artifact record.
- PRJ-021 Component Semantic Version Authority: runtime evidence must capture which versioned components produced the delivered run outputs.
- PRJ-023 LangGraph Native Orchestration: the control plane must remain compatible with the governed graph-native runtime path.
- PRJ-026 Inter-Agent Handoff Integrity: stage boundaries must preserve approved content, correlation identifiers, and handoff metadata.
- INT-005 Stage Event Contract: stage transitions must be emitted in an observable and auditable form.
- INT-007 Re-Run Contract: controlled restart and resume behavior must preserve authoritative run context.
- INT-010 STIX Export Contract: orchestration must hand off validated content suitable for STIX packaging.
- INT-011 Report Export Contract: orchestration must close with report-ready data and supporting section metadata.

## 1. Design Scope

This design covers:

- runtime state authority and persistence boundaries that keep backend control authoritative
- stage sequencing and handoff control between ordered pipeline stages
- HITL pause and resume behavior under governed continuation rules
- validation and checkpoint enforcement at each critical transition
- artifact assembly and evidence capture at run closeout

It does not replace detailed UI behavior design, provider-specific configuration design, or the agent-subsystem behavior authority in `Agent_Subsystem_Design_Specification.md`.

## 2. Primary Design Elements

### 2.1 Run Manager

The run manager is the authoritative controller for run lifecycle state.

Responsibilities:

- create and initialize run state
- dispatch stage execution in approved sequence
- apply gate and validation outcomes
- own resume checkpoints and terminal run status
- coordinate artifact assembly and evidence capture

Design rule:

The user interface may request state changes, but the run manager alone commits stage progression and gate outcomes.

### 2.2 Validation and Contract Enforcement

Validation services shall execute at stage boundaries and before controlled handoff to downstream stages.

Responsibilities:

- schema validation of canonical-graph content
- required-field and stage-contract verification
- detection of non-parseable or incomplete stage output
- conversion of recoverable failures into explicit fallback or halt behavior

### 2.3 HITL Gate Controller

The HITL controller mediates analyst decision points and records the resulting approval, edit, reject, or override action.

Design rules:

1. Gate decisions shall be persisted outside transient UI session state.
1. Override actions shall require recorded rationale.
1. Resume shall re-enter at the next approved continuation point, not at an earlier uncontrolled stage.

### 2.4 Snapshot and Evidence Manager

The snapshot and evidence manager packages run outputs into restorable and auditable artifacts.

Responsibilities:

- save checkpoint-compatible run context
- emit export bundle members
- preserve token and version evidence when available
- support later reconstruction of run provenance

## 3. Stage Control Flow

The orchestration flow shall follow this control sequence:

1. Initialize run context and selected execution mode.
1. Validate prerequisites for input set and provider configuration.
1. Execute stage in configured order.
1. Validate produced artifact and canonical-graph updates.
1. Trigger HITL gate when gate policy requires review.
1. Record decision and either halt, resume, or continue.
1. Package outputs and close the run with an auditable final state.

## 4. Fallback and Recovery Behavior

The design shall favor explicit degraded outputs over silent success when a stage produces malformed content.

Examples:

- if structured stage output cannot be parsed, export the canonical graph subset that is still authoritative
- if a downstream artifact cannot be produced, preserve the validation result and causal evidence in the run record
- if provider validation fails, prevent execution start and surface the failure through the controlling interface contract

## 5. Implementation Surfaces

Expected implementation surfaces include:

- `src/threat_modeler/backend/run_manager.py`
- `src/threat_modeler/backend/prompt_store.py`
- `src/threat_modeler/server/api.py`
- supporting orchestration, validation, and export modules under `src/threat_modeler/`

## 6. Verification Expectations

Verification for this design should include:

- unit coverage for run-state transitions and fallback paths
- integration coverage for gate pause/resume sequences
- export verification against canonical-graph authority
- operational evidence showing artifact and snapshot packaging behavior

## 7. Round 5 and 6 Design Baseline Extensions

The following design extensions are now part of the runtime and orchestration baseline and are not trace-only placeholders:

1. C01-ORCH-002 / F-C01_ORCH_002-L2
- LangGraph-compatible mode SHALL preserve deterministic transition semantics equivalent to controlled linear mode for approved stage sets.
- Stage transition event emission SHALL continue to satisfy INT-005 in both execution modes.

2. C01-ORCH-003 / F-C01_ORCH_003-L2
- Checkpoints SHALL be persisted immediately after each approved stage transition and SHALL be recoverable for resume paths governed by INT-007.
- Checkpoint continuity SHALL be treated as a runtime control-plane invariant.

3. GUI-003A / F-GUI_003A-TRACE-L2
- Paused-by-gate runtime state SHALL be projected as paused with gate context and completed-stage context; it SHALL not be projected as failed absent a terminal failure condition.

4. GUI-012A / F-GUI_012A-TRACE-L2
- Stage-selection configuration SHALL persist across sessions and enforce at-least-one-stage enabled before run initiation.

5. GUI-029 / F-GUI_029-TRACE-L2
- Prompt-response rendering SHALL be key-correlated by prompt record identifier; stale responses from prior attempts SHALL be suppressed from the active view.

6. PRJ-024 / F-PRJ_024-TRACE-L2
- Visible-browser validation scenarios SHALL be treated as governed verification flows for UI upload behavior and fixture compatibility.

7. RHMI-016 / F-S12-017-RHMI_016-L2
- Restart-safe completed-run artifact retrieval SHALL preserve run lineage context across restarts and SHALL reject retrieval of stale or mismatched run artifacts.

8. RHMI-017 / F-S12-018-RHMI_017-L2
- React input file parsing SHALL enforce binary-injection guard controls with deterministic validation failure surfaces before runtime execution.

9. PRJ-001 / F-S12-033-ORCH_001-L2
- Orchestration baseline controls mapped to PRJ-001 SHALL preserve deterministic run-state governance when architecture disposition updates are applied.
