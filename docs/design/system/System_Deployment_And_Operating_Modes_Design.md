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
