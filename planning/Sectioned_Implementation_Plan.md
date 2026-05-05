# Multi-Agent Threat Modeler
# Sectioned Implementation Plan

Date: 2026-05-02
Status: Active execution plan
Scope: Sprint 2026-05 through Sprint 2026-07

## 1. Plan Purpose

This document is the single execution plan for the active sprint window. It replaces prior mixed-status planning content and is intended to:

- align implementation to current repository reality
- assign accountable owners by workstream
- define measurable acceptance criteria per sprint
- define a realistic Definition of Done for feature completion
- standardize test input format around spreadsheet ICD data plus narrative architecture documents

## 2. Current Baseline (As of 2026-05-02)

### 2.1 What exists now

- Runtime scaffolding exists for orchestrator, state, validation, retrieval, and canonical models.
- Minimal unit tests are present and passing.
- Requirements package and traceability artifacts are present.

### 2.2 What is not complete

- Agent registry is not operational end-to-end.
- HITL workflow and audit trail are not implemented beyond stubs.
- Integration and e2e tests are mostly placeholders.
- CI quality gates that block merges on schema and contract failures are not configured.
- Documentation and plan status are not fully synchronized with code state.

### 2.3 Primary delivery risk

- The largest risk is requirements-to-code-to-test drift, not raw model quality.

## 3. Input and Fixture Standard (Updated)

The project will not treat YAML as the primary source format for test input. YAML may be used only as an optional derived transport artifact.

### 3.1 Authoritative test input artifacts

1. ICD spreadsheet input (authoritative tabular source)
- Format: xlsx and csv export
- Contents: flows, interfaces, protocol, source and destination, data classification, trust boundary hints
- Location: Tests/fixtures/inputs/icd/

2. Narrative architecture and mission context documents (authoritative text source)
- Format: md and docx
- Contents: system, subsystem, component, function descriptions, assumptions, operating constraints
- Location: Tests/fixtures/inputs/descriptions/

3. Optional derived serialization for automated test execution
- Format: json (preferred), yaml (allowed if needed for compatibility)
- Rule: derived artifacts must be reproducible from spreadsheet plus narrative source data
- Location: Tests/fixtures/inputs/derived/

### 3.2 Fixture quality gates

- Every fixture set must include a provenance note identifying source spreadsheet and source document versions.
- Every fixture set must include a requirement ID list for traceability.
- Every fixture set must include expected output assertions in Tests/fixtures/expected_outputs/.

## 4. Owners and Responsibilities

Owners are role-based and must be mapped to named individuals in sprint kickoff.

- Product Owner: scope decisions, priority, acceptance sign-off
- Technical Lead: architecture integrity, sequencing, code review standards
- Orchestrator Engineer: pipeline execution, routing, checkpoint behavior
- HITL and Audit Engineer: gate logic, role permissions, immutable audit records
- Data and Parsing Engineer: spreadsheet and narrative ingestion, normalization, fixture provenance
- Validation and Schema Engineer: typed contracts, schema boundary checks, failure policy
- Test Lead: test design, integration and e2e coverage, requirement mapping
- DevOps Engineer: CI gating, branch protections, test reporting
- Documentation Owner: README and planning sync, requirement and traceability updates

## 5. Sprint 2026-05 Execution Plan

Sprint objective:
Stabilize the runtime foundation and deliver a demonstrable governed pipeline path from authoritative inputs to validated intermediate artifacts.

### 5.1 Workstream A: Runtime baseline hardening
Owner: Technical Lead and Orchestrator Engineer

Deliverables:

- remove duplicate legacy blocks in core runtime modules
- keep one authoritative orchestrator and state model path
- ensure pipeline stage IDs and settings are consistent

Acceptance criteria:

- core modules have no duplicate class or function definitions for active runtime paths
- orchestrator runs a deterministic linear execution path across enabled stages
- code review confirms no dead compatibility seams remain in active execution path

### 5.2 Workstream B: Authoritative input ingestion (spreadsheet plus narrative)
Owner: Data and Parsing Engineer

Deliverables:

- ICD ingestion from xlsx and csv
- narrative ingestion from md and docx
- normalized intermediate representation for downstream agents
- fixture provenance metadata

Acceptance criteria:

- at least two ICD spreadsheet fixtures parse successfully
- at least two narrative description fixtures parse successfully
- normalization output contains required fields for system, subsystem, component, function, and flow entities
- test fixtures document source versions and requirement mappings

### 5.3 Workstream C: Validation gates at stage boundaries
Owner: Validation and Schema Engineer

Deliverables:

- strict validation invocation at each stage handoff
- structured error codes and locations
- safe halt behavior when critical validation fails

Acceptance criteria:

- invalid stage output is blocked from downstream execution
- validator emits machine-readable issue records with location and code
- integration tests verify halt behavior for at least two failure modes

### 5.4 Workstream D: HITL gate MVP (Gate Set 1)
Owner: HITL and Audit Engineer

Deliverables:

- gate before context merge (input integrity Gate 0)
- gate after context merge (scope confirmation)
- gate after trust boundary validation (trust boundary approval)
- approve and reject actions with rationale capture
- HITL review UI at active gates with read and edit capability
- immutable audit event records for user actions

HITL GUI choice for Sprint 2026-05:

- workflow model: Option B Structured Review Workflow
- implementation profile: P2 Service-Based API Plus UI
- UI scope: review console with gate queue, artifact viewer, structured edit panel, diff preview, and decision submission

HITL GUI MVP action model for initial implementation:

- Review: analyst can inspect full gate artifact content before deciding
- Edit: analyst can update artifact content in structured edit form
- Save draft: analyst can persist edits without advancing the pipeline
- Accept as is: analyst accepts unmodified artifact and advances to the next stage
- Accept changes: analyst accepts edited artifact and advances to the next stage
- Reject: analyst rejects artifact and routes to configured halt or rerun handling

Acceptance criteria:

- pipeline pauses at Gate 0 and both required gates
- approve and reject decisions are persisted with actor, role, timestamp, rationale
- analyst can view gate artifacts and submit tracked edits before decision at both gates
- analyst can save draft edits without triggering stage advancement
- accept as is and accept changes both resume execution to the next configured stage
- selective rerun from first gate point works for at least one integration scenario

### 5.5 Workstream E: Testing and CI baseline
Owner: Test Lead and DevOps Engineer

Deliverables:

- expanded unit tests for orchestrator, validator, ingestion
- first integration test suite for stage flow and halt behavior
- CI workflow for unit and integration tests on pull requests

Acceptance criteria:

- minimum 15 total automated tests passing
- at least 4 integration tests implemented
- pull request CI fails on test failure
- pull request CI fails on schema or contract validation failure

### 5.6 Workstream F: Documentation synchronization
Owner: Documentation Owner

Deliverables:

- synchronize README, src README, and test documentation to actual implementation state
- update traceability references for new ingestion and HITL artifacts

Acceptance criteria:

- status language in primary docs reflects current implemented capability
- all newly added tests include requirement IDs in metadata, name, or nearby comment

## 6. Sprint 2026-06 Execution Plan

Sprint objective:
Complete first end-to-end governed run with artifacts, expand HITL controls, and establish release readiness baseline.

### 6.1 Workstream A: Agent pipeline completeness (MVP breadth)
Owner: Orchestrator Engineer and Technical Lead

Deliverables:

- operational registry for all planned stage IDs
- stage contract conformance checks for each agent boundary
- deterministic stage transition map for normal flow

Acceptance criteria:

- all configured stages execute in sequence for golden-path fixtures
- stage contracts are validated for each transition
- failure in one stage prevents unsafe downstream execution

### 6.2 Workstream B: HITL gate expansion (Gate Set 2)
Owner: HITL and Audit Engineer

Deliverables:

- STRIDE calibration gate
- threat plausibility gate
- mitigation adequacy gate
- conditional merge conflict resolution gate
- conditional export consistency gate
- edit and rerun actions with full diff tracking
- GUI support for per-gate view, edit, diff preview, and rerun controls

Acceptance criteria:

- all three additional gates are active in orchestrated run
- conditional gates trigger only when configured conditions are met
- edit action requires rationale and produces before and after audit records
- analyst can view and edit gate artifacts at each active gate before approve or reject
- rerun from selected gate resumes with preserved context

### 6.3 Workstream C: Retrieval evidence linkage
Owner: Data and Parsing Engineer and Validation and Schema Engineer

Deliverables:

- retrieval source linkage for threat and mitigation outputs
- confidence metadata in output model
- reproducible corpus ingestion scripts for controlled fixture corpus

Acceptance criteria:

- generated threats and mitigations include source identifiers when retrieval is enabled
- confidence metadata is present and schema-valid
- retrieval behavior is covered by unit and integration tests

### 6.4 Workstream D: Artifact generation and e2e validation
Owner: Test Lead and Orchestrator Engineer

Deliverables:

- canonical JSON export
- STIX bundle export
- Mermaid diagram export
- markdown report export
- end-to-end golden path and one negative-path scenario tests

Acceptance criteria:

- one complete run emits all four artifact classes
- e2e tests validate artifact presence and minimum structural correctness
- negative-path e2e demonstrates safe halt and auditable failure record

### 6.5 Workstream E: Release and operational readiness
Owner: DevOps Engineer and Documentation Owner

Deliverables:

- reproducible local setup instructions
- runbook for offline mode and hybrid mode policy profile
- release checklist and evidence packaging convention

Acceptance criteria:

- a new developer can run setup and baseline tests from documented steps
- release checklist is complete and linked to evidence artifacts

## 7. Sprint 2026-07 Execution Plan

**Sprint Tracking Artifacts:**
- **Local Tracker:** planning/issues/Sprint_2026_07_Issue_Tracker.md (in-repo canonical status)
- **GitHub Issues:** #26–#33 (bnorth12/Multi-Agent-LLM-Threat-Modeling)

Sprint objective:
Close requirement and documentation alignment gaps while delivering the remaining
high-priority HMI configuration and review capabilities defined in the HMI
Architecture Blueprint.

### 7.1 Workstream A: Documentation and traceability cleanup
Owner: Documentation Owner and Technical Lead

Deliverables:

- reconcile screen ID naming across blueprint, user manual, tracker, and screenshot index
- update README project status and current test counts
- update traceability matrix to separate delivered behavior from deferred behavior
- update implementation plan and sprint tracker references for S07 issue set

Acceptance criteria:

- no conflicting SCR ID mappings remain across active docs
- README status language reflects current sprint closeout state
- traceability matrix clearly marks deferred GUI requirements
- S07 tracker and issue files are linked from the implementation plan

### 7.2 Workstream B: Model provider and connection HMI (SCR-012/013/014)
Owner: HMI Architect and Orchestrator Engineer

Deliverables:

- SCR-012 Model Provider Selection with provider dropdowns
- include Custom or Intranet provider option for self-hosted enterprise endpoints
- SCR-013 Model Connection Details for endpoint, model name, auth settings, and non-secret config
- SCR-014 Connection Validation with explicit pass/fail state handling

Acceptance criteria:

- providers include at minimum:
	- Local or Fixture (unconfigured, offline test mode)
	- OpenAI
	- Anthropic
	- xAI or Grok
	- Azure OpenAI
	- Ollama
	- Custom or Intranet (OpenAI-compatible self-hosted endpoint)
- connection details screen supports API key and endpoint URL for Custom or Intranet provider
- for commercial providers with known defaults, base URL is shown and locked by default; for Azure, Ollama, and Custom or Intranet it is editable
- connection validation status is persisted to `session_state["model_connection_valid"]`
- validation failures produce actionable error messaging without app crash

### 7.3 Workstream C: Input gate enforcement and controlled offline mode
Owner: HMI Architect and Test Lead

Deliverables:

- enforce `model_connection_valid == True` gate on Input Entry run initiation per blueprint
- explicit offline test override mode for fixture-only verification scenarios
- banner and helper text that clearly distinguishes offline test mode from validated online mode

Acceptance criteria:

- Start Run button remains disabled when neither model validation nor approved offline override is active
- offline override is intentionally selectable and visibly indicated to analyst
- automated tests cover run gating for validated online, offline override, and blocked states

### 7.4 Workstream D: Prompt configuration HMI (SCR-010/011)
Owner: HMI Architect and Prompt Engineering Owner

Deliverables:

- agent prompt editor screen per agent (SCR-010)
- prompt version history and rollback controls (SCR-011)
- per-agent temperature configuration in prompt/config workflow

Acceptance criteria:

- authorized role can edit, save, and revert prompts without source edits
- each save creates version history entry with actor and timestamp metadata
- per-agent temperature settings are persisted and used in subsequent runs

### 7.5 Workstream E: Remaining analyst workflow screens
Owner: HMI Architect and HITL Engineer

Deliverables:

- Stage Results Viewer (SCR-003)
- Threat and Mitigation Review (SCR-004)
- Results Export, Snapshot Export, and Snapshot Restore (SCR-007/008/009)

Acceptance criteria:

- analyst can inspect stage outputs and threat artifacts through GUI without direct file access
- analyst can export canonical JSON, STIX, Mermaid, and report artifacts via GUI
- snapshot export and restore flow rehydrates run context in a new session

### 7.6 Workstream F: Test and CI closeout gates
Owner: Test Lead and DevOps Engineer

Deliverables:

- expanded unit/integration/e2e coverage for all S07-delivered GUI workflows
- CI rules that keep `llm_live` out of default PR test path but runnable as explicit gate
- sprint closeout checklist entry for required online validation evidence

Acceptance criteria:

- non-live suite remains green in CI
- at least one online end-to-end `llm_live` test run is required and evidenced to close the sprint
- sprint test execution summary records date, performer, scenario, outcome, and evidence link for the online run

## 8. Definition of Done (Realistic)

A feature or workstream is Done only when all conditions below are true.

1. Implementation completeness
- code merged for scoped behavior
- no active TODO placeholders in merged scope for required behavior

2. Contract and validation safety
- boundary validation implemented for new or changed interfaces
- unsafe downstream propagation is blocked on critical failures

3. Automated testing
- unit tests added or updated for changed logic
- integration tests added for changed stage transitions or gate behavior
- e2e tests added when workflow-level behavior changes

4. Traceability
- requirement IDs linked in tests or implementation notes
- traceability matrix updated if new requirement mappings were introduced

5. Documentation
- user and developer docs reflect actual behavior
- fixture format and provenance instructions updated when input contracts change

6. CI and quality
- pull request checks pass
- no unresolved critical defects in sprint scope

7. Review and acceptance
- code review completed by designated owner role
- Product Owner acceptance criteria are met and recorded

## 9. Exit Criteria by Sprint

### Sprint 2026-05 exit criteria

- spreadsheet plus narrative fixture pipeline is operational
- HITL Gate Set 1 is operational with audit trail
- integration test layer is established and running in CI
- planning and README documentation are synchronized

### Sprint 2026-06 exit criteria

- complete orchestrated pipeline runs across all planned stages for golden path
- HITL Gate Set 2 is operational
- e2e validation covers artifact generation and failure safety
- release readiness baseline package is complete

### Sprint 2026-07 exit criteria

- documentation and traceability cleanup items are complete and merged
- model provider selection and connection validation screens are operational
- Input Entry run gating enforces validated model connection with explicit offline test override
- prompt editor and version history are operational with per-agent temperature configuration
- at least one online end-to-end `llm_live` test run is executed and documented as sprint closeout evidence

## 10. Sprint Ceremonies and Governance

- Sprint kickoff: assign named individuals to each owner role and confirm scope
- Mid-sprint review: evaluate acceptance criteria progress by workstream
- Sprint closeout: evaluate Definition of Done per completed item
- Carryover policy: incomplete scope must include explicit blocker, owner, and next sprint target
- Branch policy: use one feature branch per sprint and track all sprint issues on that single branch

## 11. Immediate Next Actions (Sprint 2026-07 Kickoff)

1. Create branch feature/sprint_2026_07 and issue set by workstream.
2. Assign named owners to role placeholders in this plan.
3. Implement S07 cleanup workstream first to remove planning and traceability drift.
4. Implement SCR-012 through SCR-014 model configuration sequence with Custom/Intranet provider support.
5. Implement Input Entry model validation gate and offline override behavior.
6. Execute and document one required online `llm_live` e2e run before sprint closure.

## 12. Issue Tracking in Repo

All sprint execution issues for this plan are created and tracked in planning/issues.

- Tracker: planning/issues/Sprint_2026_05_06_Issue_Tracker.md
- Sprint 2026-05 issues: S05-01 through S05-06
- Sprint 2026-06 issues: S06-01 through S06-07
- Tracker: planning/issues/Sprint_2026_07_Issue_Tracker.md
- Sprint 2026-07 issues: S07-01 through S07-08

Issue status updates must be performed in both the individual issue file and the central tracker in the same commit.

## 13. Sprint Branch Strategy

To reduce branch overhead and keep traceability simple, each sprint uses exactly one feature branch.

- Sprint 2026-05 branch: feature/sprint_2026_05
- Sprint 2026-06 branch: feature/sprint_2026_06
- Sprint 2026-07 branch: feature/sprint_2026_07

All workstream issues for a sprint are implemented and tracked on that sprint branch until merge.
