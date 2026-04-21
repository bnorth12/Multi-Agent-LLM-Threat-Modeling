# Tests Directory

This directory contains the Python test suite for the Multi Agent Threat Modeler.

## Test Suite Layout

- unit: fast tests for pure functions, schema models, and validation logic
- integration: multi-module tests for orchestrator plus agent interactions
- e2e: full pipeline tests from input fixtures to final artifacts
- fixtures: reusable source material and expected outputs

## Coverage Targets

1. Unit tests

- Parser normalization behavior
- Canonical schema validation behavior
- State transition helpers and routing logic
- Agent contract validation

1. Integration tests

- Agent stage chaining with checkpoint persistence
- HITL pause and resume behavior
- Validation failure handling and safe halt behavior

1. End-to-end tests

- Golden-path run with representative aerospace sample inputs
- Incremental update run that merges existing baseline
- Selective rerun from an intermediate stage

## Test Source Material

Place source fixtures in:

- fixtures/inputs

Place expected outputs in:

- fixtures/expected_outputs

Examples of fixture categories:

- small system with 2 to 5 data flows
- trust-boundary-heavy scenario
- high-risk STRIDE scenario
- malformed input cases for negative testing

## Manual Execution (Planned Python Commands)

When runtime code and dependencies are available, execute manually from project root:

1. Run all tests

- pytest

1. Run only unit tests

- pytest Tests/unit

1. Run integration tests

- pytest Tests/integration

1. Run end-to-end tests

- pytest Tests/e2e

1. Run with coverage

- pytest --cov

## Automated Execution

Planned automation model:

- Pull request gate: unit plus integration tests
- Main branch gate: full suite including e2e and coverage threshold
- Release gate: full suite plus artifact verification tests

## Documentation Rules for New Tests

- Every new feature branch should include test additions or explicit rationale for none.
- Every test file should include a short header comment describing scope.
- Every e2e scenario should map to requirement IDs and expected artifacts.
