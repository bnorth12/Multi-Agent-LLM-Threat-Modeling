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
