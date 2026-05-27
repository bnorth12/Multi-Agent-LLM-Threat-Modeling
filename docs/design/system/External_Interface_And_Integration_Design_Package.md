# External Interface and Integration Design Package

Date: 2026-05-25
Version: 0.1 (Draft)
Status: Active system design package

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`
- `../../architecture/HMI_Architecture_Blueprint.md`
- `System_Deployment_And_Operating_Modes_Design.md`

## Purpose

Define the system-level design for how the Multi-Agent Threat Modeler interacts with users, source inputs, provider services, and delivered artifact consumers across its external integration boundaries.

## Related Requirements

- PRJ-009 Deployment Mode Flexibility: integration boundaries must support offline, non-live, and policy-approved connected operating modes.
- PRJ-012 Role-Based Access Control: interface design must preserve role-gated actions and separation of duty.
- PRJ-021 Component Semantic Version Authority: external evidence consumers need version-aware delivery artifacts.
- INT-005 Stage Event Contract: runtime-facing interfaces must expose authoritative execution-state transitions.
- INT-006 HITL Decision Contract: user-facing governance interactions must submit structured decisions.
- INT-012 Provider Config Contract: provider-facing integrations must accept explicit provider and model configuration.
- INT-013 Authorization Contract: external user actions must pass authorization checks before state-changing operations are accepted.
- INT-015 Model Connection Contract: provider integration must validate endpoint, authentication, and model connection behavior explicitly.

## 1. Scope

This design covers:

- user-facing interface boundaries
- source-data ingestion and provider-service integration boundaries
- export delivery and evidence-consumer boundaries
- cross-boundary control and trust assumptions

This package does not replace the detailed architecture ICD. It organizes those interface domains into a system-integration view suitable for deployment, verification, and release planning.

## 2. Integration Domains

The system integrates across four primary external domains:

1. Analyst and reviewer interaction domain
1. Source input and ingestion domain
1. Model-provider and service integration domain
1. Artifact delivery and evidence-consumer domain

## 3. Analyst and Reviewer Interaction Domain

This domain covers browser-mediated interaction with the HMI and operator-facing control surfaces.

Key concerns:

- role-based access to run initiation, gate decisions, and configuration screens
- visibility of authoritative run status and degraded conditions
- controlled presentation of export and evidence artifacts

System design rule:

The HMI presents and requests actions, but backend runtime services remain authoritative for accepted state changes.

## 4. Source Input and Ingestion Domain

This domain covers narratives, ICD tables, structured files, and operator-supplied source material.

Key concerns:

- acceptance criteria for file and data formats
- validation before ingestion into canonical-state initialization
- preservation of provenance between source inputs and downstream artifacts

## 5. Model-Provider and Service Integration Domain

This domain covers live and non-live provider endpoints, local model runtimes, and OpenAI-compatible integration surfaces.

Key concerns:

- provider configuration and connection validation
- separation between supported deployment modes and optional development fixtures
- bounded failure handling when provider services are unavailable or misconfigured

System design rule:

Provider integration failures shall become explicit operational states, not hidden background degradations.

## 6. Artifact Delivery and Evidence-Consumer Domain

This domain covers the consumers of exported canonical JSON, STIX bundles, diagrams, reports, snapshots, and release evidence.

Key concerns:

- artifact completeness versus degraded bundle disclosure
- packaging consistency across modes
- standalone usability of release-candidate deliverables

## 7. Cross-Boundary Control Rules

1. Each external boundary shall have a documented validation or admission control point.
1. Trust-boundary crossings shall be reflected in the authoritative runtime and canonical-state records where relevant.
1. Export consumers shall receive artifacts derived only from authoritative validated state.
1. Integration design shall assume that external systems may fail, respond slowly, or provide malformed content.

## 8. Verification Expectations

Verification for this package should include:

- interface admission and validation tests
- provider integration dry runs across supported modes
- export delivery checks for complete and degraded bundles
- release-candidate review confirming the external interfaces are documented for standalone use
