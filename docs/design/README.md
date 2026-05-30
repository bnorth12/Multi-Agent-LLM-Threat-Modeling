# Design Documentation Index

## Purpose

This folder holds design-authority documents that sit below architecture baseline documents and above implementation detail.

In practice, architecture documents answer what the system must look like and what boundaries it must preserve, while the design documents in this folder answer how each governed subsystem will satisfy those boundaries.

Use this area for:

- system design documents
- software design specifications
- component-level design authorities
- future detailed design packages linked to architecture and requirements

## Subfolders

- `system/` for system-level design documents covering deployment, integration boundaries, and operating concepts.
- `software/` for software and component design specifications covering runtime behavior, data authority, agent behavior, persistence, exports, and provider configuration.

## Current Design Authorities

| Document | Design question it answers |
|---|---|
| `system/External_Interface_And_Integration_Design_Package.md` | How users, inputs, providers, and artifact consumers connect to the system boundary. |
| `system/Functional_Data_Flow_Design_Traceability_Package.md` | How system data flows are decomposed functionally and linked to architecture, design, implementation, and verification evidence. |
| `system/System_Deployment_And_Operating_Modes_Design.md` | How the system is deployed, packaged, and operated across supported modes. |
| `software/Agent_Subsystem_Design_Specification.md` | How each agent stage consumes, enriches, and emits governed content. |
| `software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md` | How canonical state is created, enriched, validated, and protected from unsafe mutation. |
| `software/Export_And_Evidence_Packaging_Design_Specification.md` | How controlled outputs and evidence bundles are assembled from authoritative sources. |
| `software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md` | How prompts, run state, checkpoints, and snapshots are persisted and restored. |
| `software/Runtime_And_Orchestration_Design_Specification.md` | How the control plane governs execution, validation, HITL pauses, and resume behavior. |
| `software/Model_Configuration_Design_Specification.md` | How provider selection, connection settings, and validation are exposed and stored. |

## Planned Follow-On Design Documents

### System Design

- Additional release-packaging or field-deployment design documents only if standalone delivery complexity grows beyond the current system design scope.

### Software Design

- HMI screen behavior detail specifications where the architecture blueprint needs implementation-constraining behavior rules for individual screens.
- Issue-scoped disposition packages for remediation work where the selected reconciliation path must be preserved as a reviewer-facing artifact before closeout.

## Traceability Rule

Every design document should reference:

- governing architecture document
- applicable requirement IDs from `Requirements/` together with requirement names where practical for readability
- verification approach and evidence source
- data-flow IDs when behavior depends on cross-boundary or multi-stage transformations
