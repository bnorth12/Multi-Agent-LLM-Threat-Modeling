# Multi-Agent Threat Modeler Structural Decomposition

## 1. Structural Hierarchy

This structure decomposes the application from system level to module-level segments.
Readers should treat the S0 through S3 labels as traceability handles rather than as the only meaningful names. The table below therefore keeps the identifiers, but each layer is written so the purpose of the segment is understandable without decoding the shorthand first.

| Level | Structure ID | Structural Element | Description |
|---|---|---|---|
| S0 | S0 | Multi-Agent Threat Modeler System | Complete software platform for governed threat modeling. |
| S1 | S1-A | Interaction Segment | Analyst-facing GUI and workflow interaction surfaces. |
| S1 | S1-B | Runtime Segment | Orchestration runtime and execution lifecycle authority. |
| S1 | S1-C | Agent Processing Segment | Stage pipeline for graph enrichment and threat synthesis. |
| S1 | S1-D | Governance Segment | Validation, gate control, and audit controls. |
| S1 | S1-E | Artifact Segment | Export and packaging services for output artifacts. |
| S1 | S1-F | Persistence Segment | Run state, prompt state, and snapshot storage controls. |

## 2. S2 Segment Decomposition

The S2 layer names the major subsystem groupings that sit inside each S1 segment. Each entry below preserves the identifier for traceability while also stating the operational role in plain language.

### 2.1 Interaction Segment (S1-A)

- S2-A1 Navigation and workflow shell for the persistent application frame and workspace controls.
- S2-A2 Input entry and source upload views for analyst-provided narratives, ICD tables, and related source material.
- S2-A3 Gate review and decision views for HITL approvals, edits, rejections, and overrides.
- S2-A4 Artifact viewing and export views for canonical graph, STIX, Mermaid, report, and snapshot outputs.
- S2-A5 Prompt editor and history views for authorized prompt tuning and rollback.
- S2-A6 Runtime diagnostics and status views for liveness, errors, and execution telemetry.

### 2.2 Runtime Segment (S1-B)

- S2-B1 Run manager execution authority that owns authoritative lifecycle state.
- S2-B2 Stage sequencing and checkpointing that enforces ordered progression through the pipeline.
- S2-B3 Resume, cancel, and restart controls for governed interruption and controlled recovery.
- S2-B4 Runtime health and heartbeat controls for fail-closed liveness supervision.

### 2.3 Agent Processing Segment (S1-C)

- S2-C1 Agent 01 source normalization for ingest cleanup and source-to-canonical mapping.
- S2-C2 Agent 02 hierarchy context construction for subsystem, component, and functional enrichment.
- S2-C3 Agent 03 trust boundary validation for identifying crossings and interface-risk context.
- S2-C4 Agent 04 STRIDE scoring for per-element or per-interface exposure assessment.
- S2-C5 Agent 05 threat generation for concrete threat record construction.
- S2-C6 Agent 06 STIX packaging for standards-oriented threat-intelligence export content.
- S2-C7 Agent 07 mitigation generation for control recommendations tied to threat records.
- S2-C8 Agent 08 diagram generation for renderable Mermaid and related visual outputs.
- S2-C9 Agent 09 report writing for human-readable narrative packaging.

### 2.4 Governance Segment (S1-D)

- S2-D1 Schema validation middleware for contract, shape, and required-field enforcement.
- S2-D2 HITL gate decision services for approval, rejection, edit, and override capture.
- S2-D3 Audit event capture and retrieval for governance evidence and later review.
- S2-D4 Live-mode fail-closed controls for degraded-provider and runtime-integrity halts.

### 2.5 Artifact Segment (S1-E)

- S2-E1 Canonical graph export service for authoritative machine-readable state delivery.
- S2-E2 STIX export service for standards-conformant threat-intelligence packaging.
- S2-E3 Mermaid artifact service for diagram source generation and rendering support.
- S2-E4 Report and evidence export service for analyst-facing reports and release-governance bundles.

### 2.6 Persistence Segment (S1-F)

- S2-F1 Run state persistence for authoritative lifecycle, checkpoint, and error records.
- S2-F2 Prompt store persistence for prompt content, version history, and rollback lineage.
- S2-F3 Snapshot serialization and restore for portable run transfer and reconstitution.
- S2-F4 Version inventory and release evidence persistence for governed delivery records.

## 3. S3 Module Allocation (Representative)

The representative S3 allocations below connect the structural segments to concrete implementation surfaces so reviewers can see which code areas own each responsibility.

| S3 ID | Parent | Module/Path | Responsibility |
|---|---|---|---|
| S3-B1 | S2-B1 | `src/threat_modeler/backend/run_manager.py` | Authoritative execution state and run lifecycle. |
| S3-F2 | S2-F2 | `src/threat_modeler/backend/prompt_store.py` | Prompt persistence, versioning, and retrieval. |
| S3-A0 | S2-A1/S2-A6 | `src/threat_modeler/ui/` | Analyst interactions and runtime projections. |
| S3-SRV | S2-B2/S2-D4 | `src/threat_modeler/server/api.py` | Operational runtime service path. |
| S3-AGT | S2-C1..S2-C9 | `src/threat_modeler/agents/` | Agent stage implementations. |
| S3-SCH | S2-D1 | `docs/schemas/` and runtime validators | Contract and schema authority. |

## 4. Structural Boundaries and Interfaces

Primary structure-to-structure interfaces:

- Interaction Segment <-> Runtime Segment for analyst commands, runtime projections, and governed state requests.
- Runtime Segment <-> Agent Processing Segment for stage dispatch, bounded inputs, and validated outputs.
- Agent Processing Segment <-> Governance Segment for validation findings, gate triggers, and approval-sensitive transitions.
- Runtime/Governance Segments <-> Persistence Segment for checkpoints, prompt history, snapshots, and audit evidence.
- Agent/Governance Segments <-> Artifact Segment for packaging only authoritative, validated content into external deliverables.

Detailed interface definitions are in:

- `Multi_Agent_Interface_Control_Document.md`

## 5. Structural Integrity Constraints

- Runtime state authority must remain backend-owned.
- UI screens must consume projections, not own authoritative runtime state.
- Agent handoffs must preserve canonical IDs and stage boundary metadata.
- Validation services must gate downstream transitions on failure.
- Export services must preserve traceability back to canonical entities.

## 6. Structural Requirement Anchors

- PRJ-019 Asynchronous Backend State Authority and PRJ-029 Live Run Liveness Fail-Closed drive the backend-owned runtime and heartbeat-control structure.
- PRJ-026 Inter-Agent Handoff Integrity and INT-005 Stage Event Contract drive the runtime-to-agent and stage-boundary segmentation.
- PRJ-006 HITL Governance and INT-006 HITL Decision Contract drive the dedicated governance segment rather than distributing decision authority across unrelated modules.
- PRJ-017 Run Snapshot Portability, PRJ-018 Agent Prompt Configurability, PRJ-021 Component Semantic Version Authority, and PRJ-022 Component File Version Traceability drive the persistence and evidence-oriented segment split.
