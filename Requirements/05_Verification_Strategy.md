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
