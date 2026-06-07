# Agent Subsystem Design Specification

Date: 2026-05-25
Version: 0.1 (Draft)
Status: Active software design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Functional_Decomposition.md`
- `../../architecture/Multi_Agent_Structural_Decomposition.md`
- `../../architecture/Multi_Agent_Logical_Decomposition.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`

## Purpose

Define the software design authority for the agent subsystem so agent behavior, stage responsibilities, mutation boundaries, and prompt-controlled execution rules are specified separately from runtime control-plane behavior.

## Related Requirements

- PRJ-006 HITL Governance: agent outputs must remain reviewable and controllable at governed stage boundaries.
- PRJ-010 Evidence-Linked Outputs: generated agent content must retain traceable linkage to source evidence and analytical rationale.
- PRJ-011 Export Artifact Set: export-producing agents must emit content that can be packaged into the required artifact bundle.
- PRJ-013 Incremental Enrichment: each agent may enrich the canonical state only within its assigned responsibility boundary.
- PRJ-014 Selective Re-Run: agent stages must support approved rerun from a controlled restart point without corrupting upstream authority.
- PRJ-026 Inter-Agent Handoff Integrity: each stage must pass forward only the approved, correlated, and versioned handoff payload.
- INT-002 Agent Input Contract: every agent must consume a bounded and declared stage input envelope.
- INT-003 Agent Output Contract: every agent must emit independently validatable stage output.
- INT-010 STIX Export Contract: the STIX packager stage must produce standards-conformant export content.
- INT-011 Report Export Contract: the human report writer stage must produce controlled analyst-readable report outputs.

## 1. Scope

This design covers:

- agent responsibilities by processing stage
- agent input and output contract expectations
- canonical-graph read and write boundaries
- prompt authority and prompt-version consumption
- deterministic fallback expectations when agent output is incomplete or malformed

This design does not define run lifecycle control, HITL checkpoint ownership, or deployment topology. Those remain governed by `Runtime_And_Orchestration_Design_Specification.md` and system-design authorities.

## 2. Agent Subsystem Objectives

The agent subsystem exists to transform analyst inputs and intermediate canonical artifacts into progressively richer, governed threat-model products while preserving stage traceability and validation integrity.

In this document, the agent numbers are retained for traceability, but each role description is written as a named responsibility so reviewers can understand the stage purpose without memorizing the numeric order.

Primary objectives:

1. Produce stage-bounded outputs with explicit responsibility and ownership.
1. Mutate only the canonical-graph portions assigned to the current stage.
1. Preserve provenance between prompt version, source inputs, and emitted artifacts.
1. Support fallback behavior that degrades explicitly rather than silently corrupting downstream stages.

## 3. Stage-Aligned Agent Roles

### 3.1 Agent 01 Input Normalizer

Responsibilities:

- normalize narrative and structured inputs into canonical ingest-ready form
- identify missing required source fields
- preserve source-to-canonical provenance references

Write boundary:

- initial canonical entities and normalized source mappings only

### 3.2 Agent 02 Hierarchical Context Builder

Responsibilities:

- derive subsystem, component, and functional context
- enrich the canonical graph with structural and contextual links

Write boundary:

- hierarchy, context, and supporting relationship fields only

### 3.3 Agent 03 Trust Boundary Validator

Responsibilities:

- identify trust boundaries and cross-boundary interactions
- flag incomplete interface semantics relevant to threat analysis

Write boundary:

- trust-boundary records, interface annotations, and validation observations

### 3.4 Agent 04 STRIDE Scorer

Responsibilities:

- assess candidate STRIDE exposure across applicable system elements
- emit scored security observations for downstream threat generation

Write boundary:

- scored threat-condition metadata, not finalized threat statements

### 3.5 Agent 05 Concrete Threat Generator

Responsibilities:

- convert scored observations into concrete threat records
- bind threat records to affected components, interfaces, and functions

Write boundary:

- threat objects and traceable supporting rationale

### 3.6 Agent 06 STIX Packager

Responsibilities:

- package threat and mitigation content into STIX-compatible output structures
- preserve identifier consistency with canonical threat objects

Write boundary:

- STIX export artifacts and packaging metadata

### 3.7 Agent 07 Mitigation Generator

Responsibilities:

- generate mitigation recommendations tied to threat records
- maintain linkage between mitigation rationale and target threat objects

Write boundary:

- mitigation content attached to threat objects per schema convention

### 3.8 Agent 08 Diagram Generator

Responsibilities:

- derive renderable diagram views from the current authoritative graph state
- emit Mermaid or equivalent diagram representations without inventing unsupported topology

Write boundary:

- diagram artifacts and rendering metadata, not canonical structure authority

### 3.9 Agent 09 Human Report Writer

Responsibilities:

- produce human-readable report narratives from authoritative upstream artifacts
- summarize results without overriding authoritative graph content

Write boundary:

- report artifacts and packaging metadata only

## 4. Agent Contract Rules

1. Each agent shall consume only the inputs declared for its stage boundary.
1. Each agent shall emit outputs that can be validated independently before downstream handoff.
1. Agents shall not mutate unrelated canonical fields owned by prior or later stages.
1. Any inferred content added by an agent shall remain traceable to source material, upstream canonical state, or explicit analytical rationale.
1. Prompt variations may tune expression and analysis strategy, but they shall not change the stage contract without coordinated architecture and design updates.

## 5. Prompt and Configuration Authority

Prompt content is a controlled behavioral input to the agent subsystem.

Design rules:

1. Prompt versions consumed during a run shall be captured as evidence.
1. Prompt changes that alter stage responsibility, output schema expectations, or mutation boundaries require design review.
1. Agent selection and provider configuration remain external controls; the agent subsystem shall consume those controls without redefining them.

## 6. Fallback and Failure Expectations

If an agent returns incomplete, malformed, or non-conforming output, the subsystem shall favor explicit fallback or halt behavior.

Examples:

- preserve the last authoritative canonical state rather than injecting speculative fields
- emit validation findings that identify the offending stage and missing contract elements
- allow downstream artifact generation only from authoritative validated content

## 7. Implementation Surfaces

Expected implementation surfaces include:

- `src/threat_modeler/agents/`
- `src/threat_modeler/orchestrator.py`
- supporting validation and export modules that consume agent outputs
- prompt definitions under `docs/agents/`

## 8. Verification Expectations

Verification for this design should include:

- stage-specific contract tests for each agent
- regression tests for malformed or partial agent outputs
- prompt-version traceability evidence in run artifacts
- integration verification that downstream stages consume only validated upstream outputs

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Agent_Subsystem_Design_Specification satisfies PRJ-006 (HITL Governance at stage boundaries), PRJ-010 (Evidence-Linked Outputs), PRJ-011 (Export Artifact Set), PRJ-013 (Incremental Enrichment), PRJ-014 (Selective Re-Run), PRJ-026 (Inter-Agent Handoff Integrity), INT-002 (Agent Input Contract), INT-003 (Agent Output Contract), INT-010 (STIX Export Contract), INT-011 (Report Export Contract)
- Agent roles (01-09) satisfy the C02-A01 through C10-A09 component requirement families and the corresponding L2/L3 functions in Multi_Agent_Functional_Decomposition.md and Function_Hierarchy_Registry.md
- Prompt-controlled execution and fallback rules satisfy PRJ-020 live-mode integrity and related SCR governance controls

### Realizes

- Agent_Subsystem_Design_Specification realizes the agent execution segment of the architecture baseline and the M1-M4 mission subfunctions (ingestion, canonical lifecycle, threat analysis/synthesis, artifact packaging)
- Individual agent stages realize the L3 function allocations (F221=Agent 01, F231=Agent 02, ..., F301=Agent 09) and their parent L2 data-interaction functions (F210-F300 groups)
- The subsystem as a whole realizes C02 through C10 agent capability slices (C02-A01-*, C03-A02-*, ... C10-A09-*) and supports C01 orchestration handoff, C12 HITL review, C13 UI surfaces, and C16 delivery

### Provides / Requires

- Agent subsystem Provides: stage-bounded, independently validatable canonical mutations with provenance (prompt version + source linkage); Requires: bounded input envelope from prior stage or ingestion (INT-002), approved gate context for reviewable stages
- Specific agents: Agent 06 Provides STIX-conformant bundles (INT-010); Agent 09 Provides controlled analyst-readable reports (INT-011); all agents Require authoritative prior canonical state and must not mutate outside assigned responsibility
- Fallback/degraded paths Provide explicit validation findings and preserved last-authoritative state; Require downstream consumers to handle degraded records

### Implemented By

- Agent responsibilities and contracts: src/threat_modeler/agents/agent_01_input_normalizer.py through agent_09_human_report_writer.py
- Orchestrator/agent integration and handoff: src/threat_modeler/orchestrator.py
- Supporting validation, prompt authority, and export consumption: src/threat_modeler/validation.py, src/threat_modeler/models/canonical.py, export modules, prompt definitions in docs/agents/
- Specific 15_End_To_End citations: frontend/src/App.tsx and related for INT-011/INT-010/INT-002 paths (S12-025, S12-026, S12-028); src/threat_modeler/agents/ for core agent logic
- Backfill linkages (from Partial_15_Wave and Reachable_Module design backfills): src/threat_modeler/agents/deserialise.py, src/threat_modeler/models/canonical.py, src/threat_modeler/ui/prompt_store.py, src/threat_modeler/ui/theme.py, src/threat_modeler/ui/screens/input_entry.py, prompt_editor.py, etc.

### Depends On

- Governing architecture documents: Multi_Agent_Threat_Modeler_Architecture_Baseline.md, Multi_Agent_Functional_Decomposition.md, Multi_Agent_Structural_Decomposition.md, Multi_Agent_Logical_Decomposition.md, Multi_Agent_Interface_Control_Document.md
- Runtime control plane: Runtime_And_Orchestration_Design_Specification.md (orchestrator owns lifecycle, checkpoints, and HITL gate ownership; this spec owns only agent mutation rules)
- Canonical authority and schema: Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md and docs/schemas/canonical_graph.schema.json
- 15_End_To_End_Traceability_Attributes_Registry.md rows that cite this document as Design Artifact (multiple S12/S13 rows for INT-010/011, GUI export/report paths, agent input ingestion)
- Prompt store and state persistence for versioned prompt consumption (cross-ref Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md)
- Executable verification in Tests/ (stage contract tests, integration pipeline completeness, results export, etc.) and FQT plan cases that exercise the 9 stages + handoff integrity
