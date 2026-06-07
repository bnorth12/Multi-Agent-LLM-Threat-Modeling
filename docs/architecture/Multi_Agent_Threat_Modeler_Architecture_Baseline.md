# Multi-Agent Threat Modeler Architecture Baseline

## 1. Scope

This document defines the internal application architecture for the Multi-Agent Threat Modeler, including decomposition and interface boundaries for the software system itself.

The modeled system under analysis is represented in the canonical graph. This architecture defines the platform that builds, refines, validates, governs, and exports that canonical graph.

The repository should enforce the architectural concepts in this document now, not later: capability, requirement, function, interface function, architecture/design, implementation, and verification all participate in the development lifecycle for the Multi-Agent Threat Modeler application.

These concepts are primarily application-modeling concepts for the Multi-Agent Threat Modeler itself, but they may also surface in the application's data flows when source material, ICD structure, or later tool maturity makes them relevant.

Agents and skills are part of the implementation and governance mechanism for this repo, not a separate side channel. They are expected to help shape development, architecture, requirements, and verification, especially where traceability and boundary behavior are under review.

## 2. Mission Context

### 2.1 L0 Mission Function

- `M0` Threat Model Production Mission: Produce an auditable, governance-controlled canonical threat model from analyst-provided system sources.

### 2.2 L1 Mission Functions

- `M1` Source Ingestion and Normalization: ingest and normalize source data.
- `M2` Canonical Graph Lifecycle Management: build and refine canonical graph state.
- `M3` Threat Analysis and Synthesis: perform governed threat analysis and mitigation synthesis.
- `M4` Artifact Packaging and Export: package and export interoperable artifacts.
- `M5` Governance and Runtime Integrity: enforce HITL control, traceability, and run integrity.

## 3. Architecture Viewpoints

### 3.1 Structural View

Primary system segments:

- Analyst interaction segment (HMI, prompt editing, export actions)
- Runtime orchestration segment (run manager, stage execution control)
- Agent execution segment (agents 01 through 09)
- Validation and governance segment (schema checks, gate contracts, audit records)
- Artifact and integration segment (STIX, Mermaid, report, JSON exports)
- Persistence and evidence segment (run state, prompt store, snapshot and version evidence)

### 3.2 Logical View

Core logical domains:

- Run control domain
- Canonical graph lifecycle domain
- HITL decision domain
- Interface and payload contract domain
- Export and evidence domain

### 3.3 Functional View

Detailed decomposition is defined in:

- `Multi_Agent_Functional_Decomposition.md`

## 4. Canonical Graph Data-Centric Architecture

Most internal interfaces exchange one of the following:

- complete canonical graph state
- stage-local subset of canonical graph state
- validation metadata and decision annotations bound to canonical IDs

This creates a graph-centric information architecture where:

- every stage consumes canonical IDs and prior context
- every stage produces updates that must preserve canonical identity continuity
- all approvals, overrides, and exports are traceable back to canonical entities

## 5. Control and Feedback Loops

### 5.1 Primary Production Loop

Input -> normalize -> enrich -> validate -> score -> generate -> mitigate -> package -> report

### 5.2 Governance Loop

Stage output -> schema validation -> HITL gate decision -> resume or halt

### 5.3 Quality Feedback Loop

Validation or analyst rejection -> targeted stage rerun -> updated canonical state

### 5.4 Runtime Integrity Loop

Backend heartbeat and run state -> UI diagnostics -> operator action (resume, cancel, triage)

## 6. Interface Domains

Interface contracts are organized by domain:

- Internal service interfaces (runtime, agent orchestration, validation)
- External interfaces (provider APIs, file imports, artifact outputs)
- User interfaces (HMI screens, gate actions, prompt editor, export interactions)

Detailed ICD definitions are in:

- `Multi_Agent_Interface_Control_Document.md`

## 7. Requirements Alignment

Architecture alignment anchors:

- Project requirements from PRJ-001 Unified Input Ingestion through PRJ-030 Prompt Store Authority and Fail-Closed Loading, as applicable to each architecture slice.
- Interface requirements from INT-001 Parser Request Contract through INT-015 Model Connection Contract.
- GUI requirements from GUI-001 Input Entry Form through GUI-043, where the architecture touches analyst-facing behavior and release-visible interfaces.

Detailed function and interface mapping:

- `Multi_Agent_Function_And_Interface_Requirements_Matrix.md`

The intent of this section is to remind the reader that the architecture baseline is not free-floating prose. Each segment, loop, and interface domain is expected to map back to named requirement authorities, not just numeric identifiers.

## 8. Change Control

When adding or refactoring architecture segments:

1. Update functional, structural, and logical decomposition docs.
1. Update ICD records for changed interfaces.
1. Update requirements matrix mappings.
1. Add or update requirement records under `Requirements/` if scope changes.
1. Add verification evidence in sprint traceability artifacts.

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Architecture baseline (mission + viewpoints + canonical data-centric + runtime integrity loops) satisfies PRJ-001 through PRJ-030 (project requirements for ingestion, canonical, pipeline, HITL, export, governance, liveness, prompt authority) and INT-001 through INT-015 (interface contracts)
- Structural, logical, and functional views satisfy the decomposition and allocation expectations in C01-ORCH-001, C12-HITL-001, C13-UI-001, C15-INT-001, C16-PRJ-001 and component families
- Canonical Graph Data-Centric Architecture satisfies PRJ-002 (canonical authority), INT-002 (parser contracts), INT-005 (stage events), PRJ-026 (handoff integrity)
- Runtime Integrity Loop and interface domains satisfy PRJ-019, PRJ-020, PRJ-023, PRJ-028, PRJ-029 (async state, live-mode, langgraph, gate/resume, liveness) plus SCR-014 and ADM controls for security/governance surfaces

### Realizes

- Multi-Agent Threat Modeler Architecture Baseline (this document) realizes CAP-L0-THREAT-MODELER and all L1 capabilities (C01-ORCH-001 through C18-ADM-001) via the defined segments, loops, and domains
- Analyst interaction segment + UI control surfaces realize C13-UI-001 and C12-HITL-001
- Runtime orchestration segment + run control domain realize C01-ORCH-001 and C16-PRJ-001
- Agent execution segment realizes C02-A01 through C10-A09 agent capability slices (M3/M4 analysis and packaging)
- Validation and governance segment + persistence/evidence realize C14-VER-001, C15-INT-001, C17-SCR-001, C18-ADM-001
- The architecture as a whole (with its three viewpoints and canonical data model) realizes the mission function M0-M5 decomposition

### Provides / Requires

- Architecture Provides: authoritative decomposition (structural/logical/functional), interface domain catalog, canonical data model, runtime integrity contracts
- Requires (from requirements layer): named PRJ/INT/GUI/HITL/ADM requirements as allocation sources; stable capability and function hierarchies
- Internal service interfaces Provide: stage handoff, state snapshot, validation result, gate decision payloads; Require: schema compliance and approved context at boundaries
- User interfaces Provide: observable state and actionable controls; Require: backend snapshot and artifact lineage for projection accuracy

### Implemented By

- Architecture concepts (orchestrator runtime control plane, agent execution segment, validation/governance) Implemented By: src/threat_modeler/orchestrator.py (FrameworkOrchestrator + LangGraphStateGraph wiring) ; src/threat_modeler/agents/*.py (all 9) ; src/threat_modeler/validation.py ; src/threat_modeler/hitl/service.py ; src/threat_modeler/backend/run_manager.py ; src/threat_modeler/state.py ; frontend/src/ (React components for HMI, gates, viewers)
- Canonical graph lifecycle Implemented By: src/threat_modeler/models/canonical.py and supporting parsers/normalizers
- Evidence/persistence Implemented By: export paths, snapshot logic in run_manager, prompt store, and FQT/test evidence capture under Tests/
- Specific runtime integrity and interface behaviors cross-referenced in 15_End_To_End_Traceability_Attributes_Registry.md implementation columns

### Depends On

- This architecture baseline Depends On: Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md for ID stability and parent/child linkage
- Depends On: Requirements/ (project, interface, HITL, GUI, admin reqs) for allocation sources and 15_End_To_End_Traceability_Attributes_Registry.md for full chain closure
- Depends On: docs/design/* specifications for refinement of the logical/functional allocations into concrete design
- Change control Depends On: governance_autoflow, verify_architecture_design_surface_coverage.py, and independent review outputs to detect drift
- All segments and domains Depend On: executable verification (Tests/unit, integration, e2e, FQT) that exercises the described interfaces, state transitions, and integrity loops
