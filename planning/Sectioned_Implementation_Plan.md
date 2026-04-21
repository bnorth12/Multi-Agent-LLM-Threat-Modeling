# Multi-Agent Threat Modeler Sectioned Implementation Plan

Date: 2026-04-20
Status: Initial working plan

## 1. Executive Direction

The repository has a strong conceptual baseline but is still implementation-light. The immediate objective is to move from fragmented specs to a single versioned source of truth, then implement a runnable Python LangGraph pipeline with strict validation and HITL checkpoints.

## 2. Major Decisions to Lock First

1. Deployment mode

- Option A: offline and air-gapped only
- Option B: hybrid mode with approved external providers

1. Model abstraction

- Implement provider-agnostic model routing
- Make model and provider selectable by configuration

1. Source-of-truth hierarchy

- Canonical schema file
- Agent prompt files
- LangGraph state schema
- No duplicate numbered variants

1. Governance baseline

- JSON schema validation at every agent boundary
- Prompt versioning and fixture-based contract checks

## 3. Current Inconsistencies and Gaps

### A. File quality and version drift

1. Duplicate files existed for same agent and have been cleaned.

1. Multiple files previously contained pasted wrapper artifacts from other folder structures.

1. Several prompt or spec files were truncated and required normalization.

### B. Schema and pipeline alignment issues

1. Mitigation placement conflict existed between flow-level and threat-level modeling.

1. Agent dependency depiction varied across documents.

1. Canonical schema was described but not initially enforced with formal JSON Schema.

### C. Architectural and operational ambiguity

1. Model strategy had mixed language between offline-only and configurable provider options.

1. Runtime implementation scaffold was not yet established.

1. HITL stage behavior and user permissions were underdefined.

## 4. Recommended Build Sections

### Section 1 Repository Hardening and Doc Normalization

Goals:

- Remove duplicate and truncated docs
- Rebuild clean source-of-truth artifacts
- Lock naming and folder standards

Deliverables:

- docs specs canonical schema
- docs specs state schema
- one prompt file per agent
- architecture decision records for model strategy and mitigation placement

Exit criteria:

- Prompt files render cleanly
- No duplicate numbered files
- Canonical schema validates fixtures

### Section 2 Core Runtime Skeleton

Goals:

- Build runnable LangGraph pipeline with typed state
- Add deterministic routing and checkpoint persistence

Deliverables:

- core state model
- graph definition
- routing module
- agent stubs and contracts
- parser module

Exit criteria:

- End-to-end dry run with mocked outputs
- Checkpoints persist and resume correctly

### Section 3 Agent Contracts and Validation Gates

Goals:

- Enforce strict contracts at each stage boundary
- Block malformed output propagation

Deliverables:

- Pydantic models
- JSON schema validation middleware
- failure policy for retry, escalate, or halt

Exit criteria:

- Invalid outputs are blocked before downstream execution
- Structured error records are generated

### Section 4 Knowledge Layer

Goals:

- Implement retrieval with source traceability
- Keep retrieval policy configurable by deployment mode

Deliverables:

- corpus ingestion pipelines
- retriever abstraction and provider toggles
- citation metadata in threat and mitigation outputs

Exit criteria:

- Reproducible ingestion runs
- Retrieval includes source IDs and confidence metadata

### Section 5 HITL Workflow and UX

Goals:

- Define approval, edit, and override behavior
- Define role permissions and audit requirements

Required gates:

1. Scope confirmation after context merge
1. Trust boundary approval after validation
1. STRIDE calibration after scoring
1. Threat plausibility review after generation
1. Mitigation adequacy review after mapping
1. Final sign-off before release

Allowed actions:

- Edit nodes, flows, boundaries, and risk values with rationale
- Approve or reject threats and controls
- Trigger selective rerun from chosen stage

Restricted actions:

- Silent mutation of approved artifacts
- Untracked edits to historical run evidence

Exit criteria:

- HITL policy and role matrix completed
- Prototype supports approve, edit, rerun, and full audit trail

### Section 6 Visualization and Editing

Goals:

- Deliver deterministic diagrams first
- Add safe editing without bypassing schema or audit controls

Recommended path:

1. Mermaid outputs with deterministic IDs and legend
1. Interactive viewer with flow-level detail panel
1. Advanced edits after ID stability and patch workflows are proven

Exit criteria:

- Analysts can inspect, edit, and rerun safely with complete traceability

### Section 7 Test and Evaluation Framework

Test layers:

1. Unit tests
1. Contract tests
1. Scenario tests
1. Regression tests
1. Safety tests

Metrics:

- schema pass rate
- citation coverage
- threat quality on curated fixtures
- HITL override rate
- time to report

Exit criteria:

- CI blocks merges on schema and contract failure

### Section 8 Release and Operations

Deliverables:

- reproducible environment setup
- runbooks for offline and hybrid modes
- versioned model provider matrix
- internal deployment packaging strategy

Exit criteria:

- one command local run
- deterministic artifact bundle per run

## 5. Immediate Next Sprint

1. Normalize and deduplicate docs
1. Finalize canonical schema and fixture set
1. Implement LangGraph skeleton and mock agents
1. Add HITL checkpoints for boundary, STRIDE, threat, and mitigation stages
1. Add diagram renderer and review workflow stub
1. Add contract tests for all agent interfaces

## 6. Open Questions

1. Is first release strictly offline or policy-approved hybrid
1. Is STIX generation after threat stage or after mitigation stage
1. What are final role definitions for author, reviewer, and approver
1. What minimum audit evidence is required for governance sign-off

## 7. Summary Opinion

The framework direction is strong. The primary risk is contract drift across specs, not model quality. Continued emphasis on schema governance and interface consistency will enable scalable implementation regardless of initial provider choice.
