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

- PRJ-005 Core Threat Modeling Pipeline: orchestration must execute trust-boundary analysis, STRIDE scoring, threat generation, mitigation mapping, STIX packaging, diagram generation, and report generation as an integrated governed sequence.
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

1. C01-ORCH-003 / F-C01_ORCH_003-L2

- Checkpoints SHALL be persisted immediately after each approved stage transition and SHALL be recoverable for resume paths governed by INT-007.
- Checkpoint continuity SHALL be treated as a runtime control-plane invariant.

1. GUI-003A / F-GUI_003A-TRACE-L2

- Paused-by-gate runtime state SHALL be projected as paused with gate context and completed-stage context; it SHALL not be projected as failed absent a terminal failure condition.

1. GUI-012A / F-GUI_012A-TRACE-L2

- Stage-selection configuration SHALL persist across sessions and enforce at-least-one-stage enabled before run initiation.

1. GUI-029 / F-GUI_029-TRACE-L2

- Prompt-response rendering SHALL be key-correlated by prompt record identifier; stale responses from prior attempts SHALL be suppressed from the active view.

1. PRJ-024 / F-PRJ_024-TRACE-L2

- Visible-browser validation scenarios SHALL be treated as governed verification flows for UI upload behavior and fixture compatibility.

1. RHMI-016 / F-S12-017-RHMI_016-L2

- Restart-safe completed-run artifact retrieval SHALL preserve run lineage context across restarts and SHALL reject retrieval of stale or mismatched run artifacts.

1. RHMI-017 / F-S12-018-RHMI_017-L2

- React input file parsing SHALL enforce binary-injection guard controls with deterministic validation failure surfaces before runtime execution.

1. PRJ-001 / F-S12-033-ORCH_001-L2

- Orchestration baseline controls mapped to PRJ-001 SHALL preserve deterministic run-state governance when architecture disposition updates are applied.

## 8. Governance and State Continuity Design Allocations

The following requirement IDs are allocated to runtime governance control behavior and are part of the active architecture/design baseline:

1. ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006

- Governance workflow controls SHALL enforce issue-linked branch execution, pull-request linkage, checklist retention, release-readiness aggregation, and recurring cadence reviews through the orchestrated governance execution path.

1. C01-ORCH-004, C01-ORCH-005

- Orchestrator control logic SHALL preserve gate-context persistence and approved handoff record continuity across every stage transition.

1. C01-STATE-001, C01-STATE-002, C01-STATE-003

- Runtime state authority SHALL version stage snapshots, preserve approved baselines as immutable history entries, and block handoff on schema-validation failure with structured error signaling.

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Runtime and Orchestration Design Specification satisfies PRJ-005 (core pipeline orchestration), PRJ-006 (HITL governance), PRJ-011 (export), PRJ-021 (component versions), PRJ-023 (LangGraph), PRJ-026 (handoff), INT-005 (stage events), INT-007 (re-run), INT-010/INT-011 (STIX/report contracts), C01-ORCH-00x, C01-STATE-00x, ADM-00x governance controls
- Orchestrator control logic, state machine, checkpointing, and gate integration satisfy the C01-ORCH-001 / C12-HITL-001 / C16-PRJ-001 family and their L2 refinements
- Governance and state continuity allocations (ADM, C01-ORCH-004/5, C01-STATE) satisfy ADM-001..006 and C01-ORCH/C01-STATE requirements per the allocations table in this document

### Realizes

- Runtime_And_Orchestration_Design_Specification (this document) realizes C01-ORCH-001, C12-HITL-001, C16-PRJ-001, C01-ORCH-002-CAP, C01-ORCH-003-CAP, C18-ADM-001 (via governance allocations) and supporting C15-INT slices for contract surfaces
- LangGraph-compatible execution, checkpoint persistence, and stage control design elements realize the corresponding L2 capability refinements (C01-ORCH-00x-CAP)
- HITL gate integration and resume paths in the design realize C12-HITL-001
- Export completion, snapshot, and evidence packaging in orchestration realize packaging/export and verification governance (M4/M5, C14-VER-001)

### Provides / Requires

- Design Provides: orchestrator state machine definition, checkpoint contract, gate integration points, run manager responsibilities, prompt/snapshot authority boundaries, export handoff contract
- Requires: stable canonical graph schema, ICD contracts (INT-00x), approved gate decisions (HITL), and upstream normalized input
- Stage transition and handoff Provide: ExecutionEdge / ExecutionNode plan and immutable snapshot handoff; Require: prior stage result + validation pass + gate approval
- Governance allocations Provide: executable policy linkage for branch/PR/checklist/release; Require: config/ json policies, planning artifacts, and issue state

### Implemented By

- Core orchestrator and graph execution : src/threat_modeler/orchestrator.py (FrameworkOrchestrator, LangGraphStateGraph, stage wiring, _MANDATORY_POST_STAGE_GATES, build_execution_plan, etc.)
- Run management, state, checkpoints, resume : src/threat_modeler/backend/run_manager.py
- HITL integration : src/threat_modeler/hitl/service.py (HitlService, gate lifecycle, decision recording)
- Validation at boundaries : src/threat_modeler/validation.py
- Prompt and snapshot persistence (design authority) : prompt store backend + snapshot logic in run_manager + evidence packaging (cross-ref Export_And_Evidence_Packaging_Design_Specification.md)
- Governance execution (ADM controls) : scripts/governance_autoflow.py ; scripts/verify_administration_controls.py ; scripts/run_governance_*.ps1
- UI-facing orchestration state projection : frontend/src/components/ (ExecutionProgress, HITLGateManager, run dashboard wiring)

### Depends On

- This design Depends On: governing architecture docs (Multi_Agent_Threat_Modeler_Architecture_Baseline.md and related decompositions) and the requirement sources listed in "Related Requirements" and "Governance and State Continuity Design Allocations"
- Depends On: 15_End_To_End_Traceability_Attributes_Registry.md rows that cite this document as Design Artifact with matching Source File Path and Verification Artifact
- Stage and gate contracts Depend On: canonical schema, state schema (docs/schemas/), and FrameworkState definition
- Governance allocations Depend On: config/governance_autoflow_routing.json , independent_review_* policy/exception files, and sprint planning artifacts
- All implementation claims Depend On: executable tests (Tests/unit/test_framework_orchestrator_langgraph.py, Tests/integration/test_agent_pipeline_completeness.py, Tests/integration/test_hitl_gate_set_2.py, etc.) and FQT evidence that the designed behaviors are present and verified
