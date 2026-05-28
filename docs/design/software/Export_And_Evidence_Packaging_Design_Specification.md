# Export and Evidence Packaging Design Specification

Date: 2026-05-25
Version: 0.1 (Draft)
Status: Active software design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`
- `../../architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md`
- `../system/System_Deployment_And_Operating_Modes_Design.md`

## Purpose

Define the software design authority for turning authoritative runtime and canonical-graph state into exportable artifacts, auditable evidence packages, and release-ready deliverables.

## Related Requirements

- PRJ-011 Export Completeness: packaging must generate the expected artifact set from authoritative sources.
- PRJ-021 Component Semantic Version Authority: release-ready artifact bundles must identify the versioned components that produced them.
- PRJ-022 Component File Version Traceability: evidence packages must retain file-level provenance where required.
- INT-006 HITL Decision Contract: governed decisions that affect release artifacts must remain traceable in the evidence set.
- INT-007 Re-Run Contract: export packaging must stay consistent when artifacts are regenerated from an approved restart point.
- INT-010 STIX Bundle Contract: STIX-oriented consumers require a structured threat-intelligence export path.
- INT-011 Human Report Contract: analyst-readable reports must remain part of the controlled output package.

## 1. Scope

This design covers:

- export artifact assembly
- evidence capture and provenance retention
- packaging boundaries for standalone release candidates
- failure handling when individual artifacts cannot be produced

This design does not redefine the canonical-state lifecycle or deployment-mode policy. Those remain governed by the canonical-graph lifecycle design and system deployment design.

## 2. Packaging Objectives

The packaging subsystem shall:

1. Generate user-facing and machine-readable artifacts from authoritative validated sources.
1. Preserve traceability between run context, prompt/version state, and emitted outputs.
1. Support release-candidate delivery where documentation and artifacts must stand alone.
1. Surface degraded packaging outcomes explicitly when one or more artifacts cannot be produced.

## 3. Artifact Classes

The design recognizes five artifact classes:

### 3.1 Canonical State Artifacts

- canonical JSON export
- checkpoint-compatible state snapshots

### 3.2 Threat Intelligence Artifacts

- STIX bundle outputs
- threat and mitigation structured exports where applicable

### 3.3 Analyst Consumption Artifacts

- Mermaid diagrams
- markdown or human-readable reports

### 3.4 Evidence Artifacts

- prompt version records
- token and model/version traces where available
- validation findings and degraded-state records

### 3.5 Release Packaging Artifacts

- deployment guidance references
- user-manual references
- release-candidate evidence manifests

## 4. Packaging Rules

1. All exported artifacts shall derive from authoritative runtime and canonical state.
1. Artifact metadata shall preserve run identity and applicable version or provenance markers.
1. Packaging shall separate authoritative data artifacts from derived presentation artifacts.
1. Missing optional artifacts shall not silently invalidate successfully produced authoritative artifacts.
1. Any degraded artifact set shall include an explicit record of what could not be produced and why.

## 5. Evidence Model

Each evidence package should preserve enough context to reconstruct what was produced, under which controls, and from which authoritative state.

The intent is that an auditor, reviewer, or future maintainer can inspect one evidence package and understand not just what files were emitted, but why those files are trustworthy, which execution path produced them, and whether the package represents a complete or degraded delivery set.

Recommended evidence fields include:

- run identifier
- execution mode
- prompt version set
- provider selection summary
- validation status by stage
- artifact manifest and production status
- timestamps and toolchain version markers when available

## 6. Failure and Degraded Packaging Behavior

If one export artifact fails:

1. preserve successful authoritative artifacts
1. record the failed artifact and causal condition
1. prevent packaging logic from implying a complete successful bundle when the bundle is incomplete

Examples:

- diagram generation fails but canonical JSON remains valid and exportable
- STIX packaging falls back to canonical threat export when structured transformation is not possible
- report generation is omitted while retaining evidence that upstream state remained authoritative

## 7. Release-Candidate Consequences

For standalone release-candidate preparation, packaging shall support a deliverable set that can be understood without fixture automation.

This implies coordination with:

- `Releases/` deployment artifacts
- `docs/User_Manual.md`
- `docs/user_manual/index.html`

## 8. Implementation Surfaces

Expected implementation surfaces include:

- export modules under `src/threat_modeler/`
- runtime packaging and snapshot services
- report, diagram, and STIX generation components
- release and evidence assembly scripts where applicable

## 9. Verification Expectations

Verification for this design should include:

- artifact-presence checks per run mode
- manifest verification for complete and degraded bundles
- traceability checks from exported artifacts back to authoritative runtime state
- release-candidate dry runs confirming the delivery package stands alone

