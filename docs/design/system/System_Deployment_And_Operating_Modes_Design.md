# System Deployment and Operating Modes Design

Date: 2026-05-24
Version: 0.1 (Draft)
Status: Active system design specification

## Governing Architecture

- `../../architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md`
- `../../architecture/Multi_Agent_Interface_Control_Document.md`
- `../../architecture/HMI_Architecture_Blueprint.md`

## Purpose

Define the system-level design that turns the architecture baseline into a releasable deployment and operating concept.

This document covers:

- deployment topology and trust boundaries
- supported operating modes and mode transitions
- external dependency boundaries
- release-candidate packaging expectations for standalone operation

## Related Requirements

- PRJ-009 Deployment Mode Flexibility: the system design must explicitly support offline-only and policy-approved connected operating modes.
- PRJ-021 Component Semantic Version Authority: deployment and release packaging must preserve component-version evidence.
- INT-005 Stage Event Contract: operating-mode transitions and active execution state must remain observable.
- INT-006 HITL Decision Contract: governed user decisions remain part of the deployed system control model, not a development-only convenience.
- INT-013 Authorization Contract: deployment packaging must preserve role-enforced access at user-facing control points.

## 1. Deployment Topology

The system is deployed as four cooperating deployment domains:

1. Analyst interaction domain hosting the user-facing HMI and local browser session.
1. Runtime orchestration domain hosting the run manager, gate controller, validation services, and prompt store APIs.
1. Model-service integration domain hosting provider adapters and outbound connections to local or remote model endpoints.
1. Artifact and evidence domain hosting generated exports, snapshots, reports, and release evidence.

The deployment shall preserve backend runtime state as the operational authority. User-interface state may cache view data, but it shall not become the source of truth for stage completion, gate status, or export readiness.

## 2. Supported Operating Modes

### 2.1 Development and Fixture Mode

Purpose:

- local development
- deterministic testing
- architecture and UX verification without live model dependencies

Characteristics:

- local or fixture providers enabled
- test fixtures and scripted automation permitted
- reduced credential handling burden

### 2.2 Connected Non-Live Validation Mode

Purpose:

- integration validation against configured providers and services
- operational shakeout before release candidate packaging

Characteristics:

- provider configuration enforced
- connection validation required before run start where applicable
- exported evidence retained for verification records

### 2.3 Release Candidate Standalone Mode

Purpose:

- package the product for evaluator or user deployment without reliance on text-fixture automation

Characteristics:

- deployment and user guidance must stand alone
- manual startup, configuration, validation, and shutdown procedures documented
- packaging must include all required runtime services, schemas, prompts, and user-facing guidance
- release notes and deployment guide become controlled delivery artifacts under `Releases/`

## 3. External Dependency Boundaries

The design recognizes three classes of external dependency:

1. Input dependencies such as ICD tables, narratives, and analyst-supplied source documents.
1. Model-provider dependencies such as OpenAI-compatible endpoints, local model runtimes, or cloud-hosted services.
1. Delivery dependencies such as browser runtime, local filesystem access, and optional evidence archiving locations.

Each dependency class shall have a documented validation entry point before the dependent mission flow is started.

## 4. Operating-Mode Control Rules

1. Mode selection shall be explicit in configuration and visible to the operator.
1. Release-candidate packaging shall default to the documented supported mode set only.
1. Standalone releases shall not assume the presence of development fixtures, test harnesses, or automation-only support paths.
1. Provider validation status shall gate run start when the selected provider requires a live connection.
1. Evidence packaging shall record the mode used for each delivered run artifact set.

## 5. Release-Candidate Documentation Consequences

When the project enters release-candidate preparation, the following user-facing artifacts shall be updated together:

1. `Releases/Deployment_Guide_<version>.md`
1. `docs/User_Manual.md`
1. `docs/user_manual/index.html`

The deployment guide is the release-controlled authority for installation, environment preparation, startup, shutdown, upgrade, rollback, and standalone troubleshooting.

## 6. Verification Expectations

Verification evidence for this design should include:

- deployment dry-run checklist results
- operating-mode validation records
- release-candidate packaging review
- user-manual and deployment-guide cross-check against the delivered build

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- System_Deployment_And_Operating_Modes_Design satisfies operating mode selection, release-candidate packaging defaults, standalone release constraints (no dev fixtures/test harnesses), provider validation gating for live connections, and evidence packaging recording the mode used for each delivered artifact set
- Supports C16-PRJ-001 (product delivery and runtime reliability), C17-SCR-001 (security/compliance runtime controls), C14-VER-001 (verification evidence and qualification trace), C18-ADM (release-readiness review), and PRJ-011/021/022 export/evidence/version requirements under governed release conditions

### Realizes

- This design realizes the release-candidate and operating-mode aspects of M5 (Governance and Runtime Integrity) and C16-PRJ / C17-SCR / C14-VER / C18-ADM capabilities in the hierarchy
- Provides the deployment and packaging rules that the Export_And_Evidence_Packaging_Design_Specification.md and External_Interface_And_Integration_Design_Package.md depend on for standalone deliverables

### Provides / Requires

- Provides: explicit mode selection in configuration (visible to operator), release-candidate packaging limited to documented supported modes, standalone release assumptions (no dev/test automation paths), provider validation as gate for live runs, evidence packaging that records the mode per artifact set
- Requires: coordination with Releases/Deployment_Guide, docs/User_Manual.md, and docs/user_manual/ for release-candidate documentation; authoritative state and export content from the runtime/canonical/export designs; governance cadence and release-readiness controls (C18-ADM)
- Standalone releases Provide self-describing deliverables; Require the deployment guide to be the release-controlled authority for install/startup/upgrade/rollback/troubleshooting

### Implemented By

- Mode and packaging rules are realized in runtime packaging paths (run_manager export/snapshot), config for provider/mode selection, and release assembly processes
- Cross-referenced by Export_And_Evidence_Packaging_Design_Specification.md (standalone deliverables), External_Interface_And_Integration_Design_Package.md (external consumer domain for release-candidates), and System_Deployment_And_Operating_Modes_Design.md itself for the consequences section
- 15_End_To_End and capability citations for C16-PRJ and C17-SCR rows that depend on deployment/runtime reliability and compliance evidence (e.g. SCR-014, PRJ delivery slices)
- Verification and release artifacts: deployment dry-runs, operating-mode records, Releases/Deployment_Guide_<version>.md, docs/User_Manual.md, user_manual/index.html, FQT release-candidate cases, and C18-ADM release-readiness checks (scripts/verify_administration_controls.py, governance_autoflow)

### Depends On

- Architecture baseline and all software/system design specs for the content that must be packaged under the governed modes
- 15_End_To_End_Traceability_Attributes_Registry.md (delivery, evidence, and compliance legs)
- Capability_Hierarchy_Baseline.md (C16-PRJ-001, C17-SCR-001, C14-VER-001, C18-ADM-001)
- Release process (07_Release_Process.md) and administration requirements (06_Project_Administration_Requirements.md)
- Executable governance/release checks and FQT evidence that the delivered artifacts match the documented modes and standalone expectations
