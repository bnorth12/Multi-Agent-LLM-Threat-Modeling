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

- PRJ-005 End-to-End Pipeline Capability: integration boundaries must support complete stage-to-stage threat modeling flow with approved handoff behavior.
- PRJ-026 Inter-Agent Handoff Integrity: external and internal interface boundaries must preserve approved handoff records and associated metadata.
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

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- External_Interface_And_Integration_Design_Package satisfies INT-001 through INT-015 family (parser request contract, ICD/narrative source compliance, stage event contract, re-run contract, HITL decision contract, STIX/report contracts, model connection contract, etc.), PRJ-001/027 (input ingestion and ICD compliance), PRJ-011/022 (export completeness and provenance), PRJ-026 (inter-agent/external handoff), and supporting PRJ-016/021 (evidence and version authority) plus GUI/SCR surfaces that cross external boundaries
- Cross-boundary control rules, artifact delivery domain, and integration assumptions support C15-INT-001 (interface contract integrity), C16-PRJ-001 (delivery/runtime), C11-LLM (provider boundaries), C17-SCR, and C18-ADM governance

### Realizes

- This package realizes the external interface and integration segment of the architecture baseline plus the interface functions within M1 (Source Ingestion), M4 (Artifact Packaging/Export), and M5 (Governance)
- Realizes L2/L3 interface and boundary functions (F210 validation, F240 trust boundary, F280/F290/F300 packaging, F310+ governance at boundaries) and supports C15-INT capability slices plus external consumer domains for C14 verification evidence

### Provides / Requires

- Provides: documented external boundaries with admission/validation control points, trust-boundary reflection in runtime/canonical records, export consumers receiving only authoritative validated artifacts, mode-aware provider and artifact delivery contracts, standalone-usable release-candidate external interface documentation
- Requires: internal service contracts (runtime, agents, validation), canonical schema compliance at crossings, approved gate decisions before export, and explicit handling of external failure/slow/malformed responses
- Artifact delivery domain Provides completeness vs. degraded disclosure for JSON/STIX/diagrams/reports/snapshots; Requires consumers to treat packages as potentially partial

### Implemented By

- External provider integration and model connection: src/threat_modeler/llm/openai_compatible_adapter.py + server/api.py verification endpoint + config
- UI/external consumer screens and HMI data: src/threat_modeler/ui/screens/* (home, input_entry, results, export, stix/stride/mermaid viewers, token_usage, snapshot, prompt, etc.) and src/threat_modeler/server/hmi_data.py
- Ingestion/parsing boundaries and server-side integration: src/threat_modeler/parsing/*, src/threat_modeler/server/api.py
- Export and evidence handoff: export modules + run_manager packaging + the classes in this package's artifact delivery section
- 15_End_To_End / backfill citations: server/hmi_data.py cited in Partial_15_Wave for SCR/GUI/RHMI; multiple UI screens in Reachable_Module and S13-005 rows; provider boundaries in R01-003 and S13-005D (model connection verification)
- Cross-ref to Functional_Data_Flow_Design_Traceability_Package.md for data-flow responsibilities at external boundaries

### Depends On

- Architecture baseline, ICD (Multi_Agent_Interface_Control_Document.md), and functional decomposition for boundary definitions
- Runtime_And_Orchestration, Canonical_Graph_Lifecycle, Agent_Subsystem, Export_And_Evidence_Packaging, Model_Configuration, Prompt_Store, and System_Deployment designs (all internal producers/consumers at the boundaries this package governs)
- 15_End_To_End_Traceability_Attributes_Registry.md rows citing external/integration design surfaces (INT family, provider, HMI data, export delivery)
- Verification: interface admission/validation, provider dry-runs, export bundle checks, and FQT cases that cross external boundaries (FQT-002 provider, FQT-008 exports, FQT-010 documentation review) plus Tests/integration/test_validation_gates.py and e2e flows
- Release artifacts (Releases/Deployment_Guide, docs/User_Manual.md, user_manual/) for standalone external interface documentation consequences
