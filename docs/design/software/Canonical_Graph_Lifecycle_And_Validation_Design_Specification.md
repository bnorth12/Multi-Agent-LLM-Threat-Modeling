# Canonical Graph Lifecycle and Validation Design Specification

Date: 2026-05-25
Version: 0.1 (Draft)
Status: Active software design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Functional_Decomposition.md`
- `../../architecture/Multi_Agent_Logical_Decomposition.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`
- `../../schemas/canonical_graph.schema.json`

## Purpose

Define the software design authority for how the canonical graph is created, enriched, validated, handed off between stages, and preserved as the authoritative state model for the application.

## Related Requirements

- PRJ-006 HITL Governance: canonical-state progression must support governed pause, review, and continuation points.
- PRJ-013 Incremental Enrichment: the canonical graph must support safe enrichment without destructive overwrite.
- PRJ-015 Fail-Safe Halting: validation logic must stop unsafe downstream propagation.
- PRJ-021 Component Semantic Version Authority: canonical-state evidence must remain version-aware for release governance.
- PRJ-023 LangGraph Native Orchestration: canonical-state handoff rules must remain valid across the orchestrated runtime path.
- PRJ-026 Inter-Agent Handoff Integrity: each stage must pass forward only controlled and traceable canonical-state updates.
- INT-005 Stage Event Contract: state transitions must remain observable and auditable.
- INT-006 HITL Decision Contract: reviewed canonical-state changes must reflect structured human decisions when governance gates apply.

## 1. Scope

This design covers:

- canonical-graph creation and initialization rules
- stage-by-stage mutation boundaries
- validation gates and contract enforcement
- degraded-mode and fallback rules when stage output is malformed
- preservation of authoritative state for downstream exports and evidence

This design does not define deployment topology or detailed agent prompt behavior. Those remain covered by system design and agent-subsystem software design authorities.

## 2. Canonical Graph Design Role

The canonical graph is the single authoritative representation of the analyzed system and its threat-model state.

In practice, this means readers should think of the canonical graph as the one version of the truth that every major subsystem must either update under controlled rules or consume as read-only authority. Reports, diagrams, STIX bundles, UI views, and evidence packages may each present the data differently, but none of them are allowed to become a competing source of truth.

It shall serve as:

- the authoritative handoff artifact between processing stages
- the source of truth for export generation
- the state reference for HITL review decisions
- the provenance anchor for evidence packaging and auditability

## 3. Lifecycle States

The canonical graph progresses through the following design states:

1. Initialized from source inputs and normalized ingest artifacts.
1. Enriched with structural, functional, and contextual relationships.
1. Annotated with trust-boundary and validation observations.
1. Expanded with threat, mitigation, and export-support metadata.
1. Frozen as an authoritative export source for downstream packaging.

At each state, only the stage owning that transition may mutate the assigned fields for that lifecycle segment.

## 4. Mutation Authority Rules

1. Each processing stage shall declare the canonical sections it may create or modify.
1. A stage shall not overwrite unrelated fields owned by earlier validated stages without an explicit correction path.
1. Derived artifacts such as reports, diagrams, and STIX bundles shall read from the authoritative graph rather than redefine it.
1. User-interface displays may project or summarize canonical state, but they shall not become the canonical authority.

## 5. Validation Architecture

Validation shall occur at three levels:

### 5.1 Schema Validation

Ensure the graph conforms to the canonical schema and required structural rules.

### 5.2 Stage Contract Validation

Ensure each stage produced the mandatory fields, identifiers, and references required for downstream handoff.

### 5.3 Semantic Guard Validation

Ensure that critical relationships remain coherent, such as:

- threats linked to valid components, interfaces, or functions
- mitigations attached to valid threat objects
- identifiers stable across stage transitions and export generation

## 6. Handoff Rules

Before a downstream stage may consume the graph:

1. The upstream stage output shall be validated.
1. The runtime shall record whether the graph is authoritative, degraded-but-usable, or halted.
1. Any fallback behavior shall preserve the last validated canonical state rather than partially committing malformed data.

## 7. Fallback and Recovery Design

When a stage returns non-conforming output, the system shall prefer explicit degraded-state handling over silent mutation.

Examples:

- reject malformed stage mutations and preserve the prior validated graph
- emit validation findings tied to the stage and contract breach
- allow export only from the last authoritative graph state and clearly record degraded conditions

## 8. Implementation Surfaces

Expected implementation surfaces include:

- `src/threat_modeler/models/`
- `src/threat_modeler/validation.py`
- `src/threat_modeler/orchestrator.py`
- runtime and export modules that consume authoritative canonical state

## 9. Verification Expectations

Verification for this design should include:

- schema validation regression coverage
- stage contract tests for required canonical fields
- fallback-path tests that preserve prior authoritative state
- evidence confirming exported artifacts derive from validated canonical content

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Canonical_Graph_Lifecycle_And_Validation_Design_Specification satisfies PRJ-006 (HITL Governance via pause/review/continuation points on canonical state), PRJ-013 (Incremental Enrichment without destructive overwrite), PRJ-015 (Fail-Safe Halting on validation failure), PRJ-021 (Component Semantic Version Authority in state evidence), PRJ-023 (LangGraph Native Orchestration compatibility for handoff rules), PRJ-026 (Inter-Agent Handoff Integrity with controlled/traceable updates), INT-005 (Stage Event Contract for observable/auditable transitions), INT-006 (HITL Decision Contract for reviewed canonical changes)
- Canonical creation, mutation boundaries, validation gates, and degraded/fallback rules satisfy core elements of C01-ORCH-001 (orchestration), C15-INT-001 (interface/canonical contracts), and multiple C13-UI / C16-PRJ delivery slices that consume authoritative state

### Realizes

- This design realizes the canonical graph lifecycle domain of the architecture baseline and the M2 (Canonical Graph Lifecycle Management) mission subfunction plus supporting portions of M1, M3, M4, and M5
- Realizes L2 functions around canonical initialization, context enrichment, validation services, and handoff (F220, F230, F240 groups and their L3/L4 children) per Functional Decomposition and Function_Hierarchy_Registry.md
- Supports realization of C01-ORCH, C15-INT, and governance capabilities that depend on stable authoritative canonical state (multiple S13 and S12 rows in 15_End_To_End cite this doc for telemetry, state projection, and handoff paths)

### Provides / Requires

- Provides: single authoritative canonical representation, stage-by-stage mutation boundaries with contract enforcement, validation findings tied to stage/contract breach, preserved prior validated graph on non-conformance, version-aware state for release governance
- Requires: controlled input from ingestion or prior stage, approved human decisions at governance gates (INT-006), schema definitions (docs/schemas/canonical_graph.schema.json), and handoff rules that remain valid under LangGraph orchestration (PRJ-023)
- Degraded-mode handling Provides explicit record of validation failure + last authoritative state; Requires downstream consumers (export, UI, evidence) to respect degraded markers

### Implemented By

- Canonical model and core lifecycle: src/threat_modeler/models/canonical.py
- Validation gates and contract enforcement: src/threat_modeler/validation.py (CanonicalGraphValidator and related)
- Orchestrator integration for state handoff, enrichment, and degraded handling: src/threat_modeler/orchestrator.py
- Runtime consumption and projection: src/threat_modeler/backend/run_manager.py and related runtime_state modules
- 15_End_To_End citations: docs/design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md is listed as Design Artifact for S12-020 (INT-005 telemetry), S13-001 (INT-005 orchestration alignment), and multiple S13-005* UI/state projection rows (e.g. TokenUsageView, ExecutionProgress, ArtifactsViewer, run_manager async projection)
- Backfill support: src/threat_modeler/agents/deserialise.py, src/threat_modeler/models/canonical.py (Partial_15_Wave_Design_Backfill)

### Depends On

- Governing architecture: Multi_Agent_Threat_Modeler_Architecture_Baseline.md, Multi_Agent_Functional_Decomposition.md, Multi_Agent_Logical_Decomposition.md, Multi_Agent_Interface_Control_Document.md, and the canonical schema
- Runtime and orchestration ownership: Runtime_And_Orchestration_Design_Specification.md (this spec owns canonical rules; runtime owns lifecycle control, checkpoints, and gate ownership)
- Agent subsystem for stage-specific mutations that must stay within assigned canonical boundaries (cross-ref Agent_Subsystem_Design_Specification.md)
- 15_End_To_End_Traceability_Attributes_Registry.md rows citing this document (multiple orchestration, telemetry, UI state projection, and remediation slices)
- Export/evidence packaging and UI consumers that must only derive from validated canonical content (Export_And_Evidence_Packaging_Design_Specification.md, various frontend components)
- Executable tests exercising schema compliance, stage contracts, fallback preservation, and integration pipeline completeness (Tests/integration/test_validation_gates.py, Tests/integration/test_agent_pipeline_completeness.py, etc.) plus FQT cases that traverse full canonical lifecycle under governance
