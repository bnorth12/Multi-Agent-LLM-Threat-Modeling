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

- PRJ-006 orchestrated agent execution
- PRJ-013 contextual input enrichment
- PRJ-015 canonical-state integrity
- PRJ-021 evidence generation and delivery
- PRJ-023 runtime execution control
- PRJ-026 stage-to-stage contract integrity
- INT-005 runtime execution control
- INT-006 canonical export delivery

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
