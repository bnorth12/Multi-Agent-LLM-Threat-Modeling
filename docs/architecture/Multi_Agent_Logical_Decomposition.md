# Multi-Agent Threat Modeler Logical Decomposition

## 1. Logical Domains

| Domain ID | Logical Domain | Responsibilities |
|---|---|---|
| L-D1 | Ingestion Logic | Parse and normalize narrative and ICD inputs into canonical-ready payloads. |
| L-D2 | Canonical Graph Logic | Construct and maintain authoritative canonical graph state. |
| L-D3 | Analysis Logic | Execute STRIDE, threat generation, mitigation synthesis. |
| L-D4 | Governance Logic | Apply validation gates, HITL decisions, and fail-closed controls. |
| L-D5 | Orchestration Logic | Manage sequencing, checkpoints, reruns, and run lifecycle controls. |
| L-D6 | Presentation Logic | Render analyst views and collect analyst decisions/edits. |
| L-D7 | Artifact Logic | Package export artifacts and evidence bundles. |
| L-D8 | Persistence Logic | Persist run state, prompt state, snapshots, and version evidence. |

## 2. Core Logical Objects

| Object ID | Logical Object | Description |
|---|---|---|
| O-001 | CanonicalGraph | Authoritative run data object for system model and threats. |
| O-002 | StageOutputEnvelope | Stage payload plus status, version, and correlation metadata. |
| O-003 | ValidationResult | Pass/fail result with error code, field path, and severity. |
| O-004 | HitlDecisionRecord | Decision, rationale, actor, role, timestamp, and gate context. |
| O-005 | RunControlState | Runtime status, active stage, gate state, heartbeat, and errors. |
| O-006 | PromptConfigRecord | Prompt text, temperature, version history, rollback lineage. |
| O-007 | ExportArtifactManifest | Artifact file list, checks, and source references to canonical IDs. |
| O-008 | SnapshotPackage | Serialized run state for transfer and restore. |

For readability in the flow descriptions below, each logical object is referenced by both its identifier and its plain-language name. The identifier remains useful for traceability, but readers should be able to understand the sentence without having to jump back to this table every time.

## 3. Logical Flow Decomposition

### 3.1 Primary Data Flow

1. Ingestion logic creates normalized payload.
1. Canonical graph logic initializes and enriches the canonical graph authority, O-001 CanonicalGraph.
1. Analysis logic reads and writes controlled subsets of O-001 CanonicalGraph at each processing stage.
1. Artifact logic transforms O-001 CanonicalGraph into export-specific payloads while preserving the canonical graph as the authoritative source.
1. Presentation logic renders outputs and accepts analyst inputs.

### 3.2 Governance Flow

1. Stage output emits O-002 StageOutputEnvelope, which carries the stage payload together with status, version, and correlation metadata.
1. Governance logic validates both O-002 StageOutputEnvelope and O-001 CanonicalGraph by producing O-003 ValidationResult.
1. Gate decision logic captures the analyst or reviewer decision in O-004 HitlDecisionRecord.
1. Orchestration logic updates O-005 RunControlState and then either continues execution or halts the run under fail-closed control.

### 3.3 Persistence Flow

1. Runtime and prompt services persist O-005 RunControlState and O-006 PromptConfigRecord.
1. Snapshot service persists O-008 SnapshotPackage for controlled transfer and restore.
1. Export service persists O-007 ExportArtifactManifest together with the generated output artifacts.

## 4. Internal Control and Feedback Loops

### 4.1 Validation Feedback Loop

- Trigger: schema or semantic validation error.
- Path: O-003 ValidationResult -> gate decision -> rerun point selection.
- Effect: controlled correction before downstream propagation.

### 4.2 Analyst Review Loop

- Trigger: HITL gate open.
- Path: rendered context -> analyst decision recorded in O-004 HitlDecisionRecord -> orchestration update of O-005 RunControlState.
- Effect: governed stage continuation or halt.

### 4.3 Runtime Health Loop

- Trigger: heartbeat staleness, provider degradation, fallback risk.
- Path: runtime telemetry -> fail-closed control -> operator diagnostics.
- Effect: preserve evidence integrity and prevent silent degraded execution.

### 4.4 Prompt Tuning Loop

- Trigger: prompt update from authorized role.
- Path: O-006 PromptConfigRecord update -> next run execution -> comparative output review.
- Effect: controlled model behavior tuning with rollback support.

## 5. Interface Segmentation (Logical)

- `I-L1`: UI-to-runtime control and status interfaces.
- `I-L2`: Runtime-to-agent stage handoff interfaces.
- `I-L3`: Runtime-to-governance validation interfaces.
- `I-L4`: Runtime-to-persistence state interfaces.
- `I-L5`: Runtime/artifact-to-external export interfaces.
- `I-L6`: External-provider invocation interfaces.

Detailed ICD records:

- `Multi_Agent_Interface_Control_Document.md`

## 6. Logical Requirements Anchors

- PRJ-002 Canonical Graph Authority; PRJ-003 Deterministic Pipeline; PRJ-004 Stage Validation Gate; PRJ-006 HITL Governance; PRJ-014 Selective Re-Run; PRJ-015 Fail-Safe Halting.
- PRJ-019 Asynchronous Backend State Authority; PRJ-020 Live-Mode Integrity Halt on Provider Degradation; PRJ-026 Inter-Agent Handoff Integrity; PRJ-028 Orchestrator Gate Enforcement and Resume Control; PRJ-029 Live Run Liveness Fail-Closed; PRJ-030 Prompt Store Authority and Fail-Closed Loading.
- INT-002 Agent Input Contract; INT-003 Agent Output Contract; INT-004 Validation Result Contract; INT-005 Stage Event Contract; INT-006 HITL Decision Contract; INT-007 Re-Run Contract; INT-008 Visualization Read Contract; INT-009 Visualization Edit Contract; INT-012 Provider Config Contract; INT-013 Authorization Contract; INT-014 Audit Retrieval Contract; INT-015 Model Connection Contract.
- GUI-002 HITL Gate Screens; GUI-003 Pipeline Status Dashboard; GUI-016 Backend Runtime State Projection; GUI-017 Live Mode Failover Hard-Stop Visibility; GUI-027 Run Diagnostics Panel; GUI-028 Execution Error Rendering.
