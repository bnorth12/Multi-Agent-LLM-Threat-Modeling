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
