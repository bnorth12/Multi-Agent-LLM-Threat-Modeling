# Verification Strategy

Each requirement should be tagged with one or more verification methods:

- Test: Verified by automated or manual test case.
- Analysis: Verified by design or data analysis.
- Inspection: Verified by artifact review.
- Demonstration: Verified by operational run-through.

Verification planning rules:

VS-001: Requirement Owner SHALL assign at least one verification method to each requirement ID.

VS-002: Requirement Owner SHALL define objective pass criteria for each requirement ID.

VS-003: Test Team SHALL map automated tests to requirement IDs for all schema, orchestration, and interface contracts.

VS-004: Review Team SHALL perform inspection-based verification for HITL workflow and audit controls.

VS-005: Integration Team SHALL perform end-to-end demonstration of a complete run with approvals and exports.

VS-006: Sprint Team SHALL record demonstration evidence (annotated screenshots or screen recording) for every sprint that delivers runnable user-facing functionality. Evidence SHALL be attached to the sprint PR and referenced in the sprint test execution summary.

VS-007: Sprint demonstration SHALL cover, at minimum, the user-facing deliverables of that sprint: pipeline execution for pipeline sprints; HITL gate pause and resume for HITL sprints; screen walkthrough for HMI sprints; full end-to-end run from input to export for release sprints.

VS-008: For release-candidate sprints that intentionally exclude automation from release gating, Sprint Team SHALL execute and document a full manual release-candidate validation campaign that includes functional workflow checks and documentation walkthrough checks (user manual, product documentation set, and deployment guide).

VS-009: Sprint Team SHALL maintain at least one automated visible-browser validation scenario that exercises UI file upload behavior with approved sprint fixtures (including markdown narratives) and records command + fixture evidence in sprint test documentation.

VS-010: For runtime state transitions and HITL gate publication paths, Sprint Team SHALL execute a race-condition verification control that checks causal ordering invariants (for example, Gate 0 payload-ready-before-paused projection) using automated API tests and at least one timestamped polling probe, and SHALL record evidence in sprint governance artifacts.

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- VS-00x family derived from C14-VER-001 (Verification and Validation Governance) in Capability_Hierarchy_Baseline.md and the verification coverage control function F-VER-TRACEABILITY-L1
- Overall strategy supports CAP-L0-THREAT-MODELER mission verification and all L1 capabilities (especially C01-ORCH, C12-HITL, C13-UI, C14-VER, C16-PRJ, C18-ADM)

### Allocated To

- VS-001 through VS-010 allocated to C14-VER-001 and the verification/qualification artifacts (FQT plan, sprint test execution summaries, 15_End_To_End verification columns, independent review outputs)
- Sprint-specific verification (visible-browser, race-condition, release-candidate manual campaigns) allocated to C16-PRJ-001 and C18-ADM release-readiness controls

### Refines

- Detailed test plans (FQT, unit/integration/e2e suites) and per-sprint execution summaries refine the high-level VS-* strategy statements
- Component and sprint remediation verification obligations refine the base strategy

### Satisfied By

- VS-001 (unit/integration) satisfied by Tests/unit/, Tests/integration/, src/ test files, and the test anchors in 15_End_To_End_Traceability_Attributes_Registry.md
- VS-002/003 (FQT and sprint test execution summaries) satisfied by Tests/Formal_Qualification_Test_Plan.md + docs/verification/sprint_test_execution/Test_Execution_Summary_*.md + FQT/ archive evidence
- VS-004/005/006/007/008 (demonstration, screenshots, release-candidate validation) satisfied by FQT cases, e2e browser flows (live_browser_e2e_smoke_react.py), and release artifacts under Releases/ + docs/
- VS-009 (visible-browser CAV upload) satisfied by scripts/live_browser_e2e_smoke_react.py + FQT-002/003 input/upload cases + frontend input components
- VS-010 (race-condition / causal ordering for gates) satisfied by Tests/integration/test_validation_gates.py + timestamped polling + FQT gate cases
- All VS-* satisfied by the verification legs in 15_End_To_End (Test Level, Test Artifact ID, Evidence Timestamp) and by governance verifiers (verify_sprint_traceability.py, verify_architecture_design_surface_coverage.py, independent_repo_review.py)

### Verified By

- The artifacts listed above (FQT plan/execution, sprint summaries, browser automation, integration gate tests, independent reviews) are themselves the verification evidence for the VS-* requirements
- 15_End_To_End and Capability_Function_Architecture_Traceability_Matrix.md rows that cite verification artifacts close the "Verified By" direction for the requirements they cover
- C14-VER-001 governance (scripts/verify_*, governance_autoflow, sprint closeout certifiers) provides meta-verification that the strategy is being followed

### Depends On

- 01_Project_Requirements.md, 03_HITL_Requirements.md, 10_GUI_Requirements.md, 06_Project_Administration_Requirements.md, and all component reqs for the behaviors being verified
- All design specs (especially Runtime_And_Orchestration, Agent_Subsystem, Export_And_Evidence, External_Interface) for the "Satisfied By" implementations that must be verified
- 15_End_To_End_Traceability_Attributes_Registry.md as the single source for executable verification anchors
- FQT plan, sprint test execution summaries, and independent review outputs as the primary evidence consumers/producers
- 18_Traceability_Governance_Operating_Model.md (this strategy document operationalizes the "Verification" and "Evidence production / substantiation" relationships)
- C14-VER-001 / C18-ADM capabilities and their implementation anchors (scripts/verify_*, governance_autoflow, sprint-closeout-certifier) for ongoing enforcement

The VS-* strategy is refined by detailed executable artifacts (FQT plan cases, specific unit/integration/e2e test modules, sprint test execution summaries, and independent review outputs). These refinements live in the 15_End_To_End verification columns, the FQT document itself, and the design annexes (especially Runtime_And_Orchestration, Export_And_Evidence, etc.) that list the exact test anchors. No further top-level refinement list is needed here beyond the explicit mappings already provided in the Satisfied By / Verified By sections above.
