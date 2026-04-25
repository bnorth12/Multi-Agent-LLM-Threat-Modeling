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


### Section 1 Repository Hardening and Doc Normalization (COMPLETED)

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

- [x] Prompt files render cleanly
- [x] No duplicate numbered files
- [x] Canonical schema validates fixtures


### Section 2 Core Runtime Skeleton (COMPLETED)

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

- [x] End-to-end dry run with mocked outputs
- [x] Checkpoints persist and resume correctly


### Section 3 Agent Contracts and Validation Gates (COMPLETED)

Goals:

- Enforce strict contracts at each stage boundary
- Block malformed output propagation

Deliverables:

- Pydantic models
- JSON schema validation middleware
- failure policy for retry, escalate, or halt

Exit criteria:

- [x] Invalid outputs are blocked before downstream execution
- [x] Structured error records are generated


### Section 4 Knowledge Layer (NOT STARTED)

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


### Section 5 HITL Workflow and UX (NOT STARTED)

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


### Section 6 Visualization and Editing (NOT STARTED)

Goals:

- Deliver deterministic diagrams first
- Add safe editing without bypassing schema or audit controls

Recommended path:

1. Mermaid outputs with deterministic IDs and legend
1. Interactive viewer with flow-level detail panel
1. Advanced edits after ID stability and patch workflows are proven

Exit criteria:

- Analysts can inspect, edit, and rerun safely with complete traceability


### Section 7 Test and Evaluation Framework (IN PROGRESS)

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

- [x] Unit and contract tests for parser, orchestrator, and schema coupling implemented
- [x] CI/test pass rate is high
- [ ] CI blocks merges on schema and contract failure


### Section 8 Release and Operations (NOT STARTED)

Deliverables:

- reproducible environment setup
- runbooks for offline and hybrid modes
- versioned model provider matrix
- internal deployment packaging strategy

Exit criteria:

- one command local run
- deterministic artifact bundle per run


### Test Automation and Coverage (UPDATED)
- [x] Scaffolded and executed unit tests for orchestrator and state graph integration
- [x] Added stubs and infrastructure to enable automated tests for all new modules
- [x] All orchestrator and state graph code is now covered by automated tests
- [ ] Continue to develop and execute automated tests for all new code and modules as they are integrated
- [ ] CI to block merges on schema/contract test failure (to be implemented)


## 5. Immediate Next Sprint (UPDATED)

1. Normalize and deduplicate docs [x]
1. Finalize canonical schema and fixture set [x]
1. Implement LangGraph skeleton and mock agents [x]
1. Add HITL checkpoints for boundary, STRIDE, threat, and mitigation stages [ ]
1. Add diagram renderer and review workflow stub [ ]
1. Add contract tests for all agent interfaces [x]

## 6. Open Questions

1. Is first release strictly offline or policy-approved hybrid
1. Is STIX generation after threat stage or after mitigation stage
1. What are final role definitions for author, reviewer, and approver
1. What minimum audit evidence is required for governance sign-off


## 8. Sprint 2026-04 Checklist (IN PROGRESS)

### Requirements & Plan Audit
- [ ] Review all requirements and plans in docs and code
- [ ] List all gaps/inconsistencies as new issues

### Issue Creation
- [ ] Create GitHub issues for:
	- [ ] LangGraph state graph integration
	- [ ] HITL workflow MVP
	- [ ] Retrieval/knowledge layer MVP
	- [ ] Visualization/diagram output
	- [ ] Expanded contract/unit tests
	- [ ] Documentation sync
	- [ ] Any other gaps found in audit

### Sprint Branch & PR
- [ ] Create feature branch: feature/sprint-2026-04
- [ ] Implement sprint items, referencing issues in commits/PRs
- [ ] Open a PR for the sprint branch (title: Sprint 2026-04 Implementation)
- [ ] Ensure PR body lists all issues addressed and links to requirements/plan sections

### Status Checklist
- [ ] Add a checklist to this plan with:
	- [ ] Each requirement/plan item
	- [ ] Linked issue/PR numbers
	- [ ] Status (open/in progress/closed)

### Sprint Review & Closure
- [ ] Review checklist at sprint end
- [ ] Close completed issues
- [ ] Move incomplete items to next sprint
- [ ] Merge sprint PR and delete feature branch

The framework direction is strong. The primary risk is contract drift across specs, not model quality. Continued emphasis on schema governance and interface consistency will enable scalable implementation regardless of initial provider choice.
