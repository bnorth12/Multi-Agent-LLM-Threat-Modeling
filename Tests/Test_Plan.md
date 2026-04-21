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

## 5. Defect Severity Guidelines

- Critical: schema bypass, unsafe release path, broken checkpointing
- Major: incorrect stage routing, missing mandatory artifacts
- Minor: formatting defects, non-blocking metadata mismatches

## 6. Traceability

Every integration and e2e test case should include requirement IDs in test metadata or test name.
