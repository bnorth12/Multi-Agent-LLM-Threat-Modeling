# Test Plan

## 1. Objective

Define a complete and scalable Python test strategy for unit, integration, and end-to-end validation of the multi-agent threat modeling workflow.

## 2. Scope

In scope:

- canonical graph schema and state handling
- orchestration transitions and checkpointing
- agent contract validation
- HITL gate behavior and audit side effects
- output artifact generation contracts

Out of scope for early phases:

- model quality benchmarking across external providers
- UI-specific visual regression testing

## 3. Test Levels

### Unit

- Parser mapping functions
- Schema validators
- Utility functions
- Individual agent output shape checks

### Integration

- Multiple agent stages in sequence
- Failure and recovery paths
- HITL pause and resume events

### End-to-End

- Full pipeline on curated fixtures
- Incremental merge scenario
- Selective rerun from downstream stage

## 4. Exit Criteria by Level

- Unit: all tests pass, no critical contract violations
- Integration: all stage transitions verified, no unhandled state errors
- End-to-End: required output artifacts generated and validated
- Demonstration: sprint demonstration completed and recorded per VS-005; evidence attached to sprint PR

## 5. Sprint Demonstration Requirements

Every sprint that delivers runnable user-facing functionality SHALL include a sprint demonstration as part of the Definition of Done. The demonstration verifies that delivered features work end-to-end in a realistic scenario, not just in isolated unit or integration tests.

### Demonstration Scope

The demonstration SHALL cover, at minimum, the functionality delivered in that sprint:
- For pipeline sprints: a full or partial pipeline run on a fixture input, showing stage outputs.
- For HITL sprints: at least one HITL gate pause, decision (accept or reject), and pipeline resume.
- For HMI sprints: walkthrough of all delivered screens in the Streamlit application.
- For release sprints: full end-to-end run from input to export artifact, including all mandatory HITL gates.

### Demonstration Evidence

Evidence SHALL be attached to the sprint PR and referenced in the sprint test execution summary. Accepted evidence formats:
- Annotated screenshots stored in `docs/screenshots/` (minimum requirement).
- Screen recording (optional but preferred for HITL and HMI sprints).
- Terminal output log showing pytest run + manual demo steps.

### Demonstration Record Format

Each sprint test execution summary SHALL include a Demonstration section with:
- Date and performer
- Environment (local Streamlit, offline model profile, etc.)
- Scenario description
- Outcome: pass / pass with notes / fail
- Evidence link (screenshot index or recording)
- Any open defects discovered during demo

## 5. Defect Severity Guidelines

- Critical: schema bypass, unsafe release path, broken checkpointing
- Major: incorrect stage routing, missing mandatory artifacts
- Minor: formatting defects, non-blocking metadata mismatches

## 6. Traceability

Every integration and e2e test case should include requirement IDs in test metadata or test name.
