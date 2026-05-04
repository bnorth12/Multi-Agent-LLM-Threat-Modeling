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

## Manual Execution

From project root with the virtual environment active:

```sh
# Run all tests
.venv\Scripts\python.exe -m pytest Tests/ -q

# Run only unit tests
.venv\Scripts\python.exe -m pytest Tests/unit -q

# Run only integration tests
.venv\Scripts\python.exe -m pytest Tests/integration -q

# Run with verbose output
.venv\Scripts\python.exe -m pytest Tests/ -v
```

## Current Test Counts

| Suite | File | Tests | Status |
|---|---|---|---|
| Unit | Tests/unit/test_input_ingestion.py | 43 | Passing |
| Integration | Tests/integration/test_validation_gates.py | 12 | Passing |
| **Total** | | **55** | **All passing** |

## Requirement Linkage

| Test File | Requirements Covered |
|---|---|
| test_input_ingestion.py | PRJ-001, PRJ-002, INT-001, INT-002 (ingestion contracts) |
| test_validation_gates.py | PRJ-003, PRJ-015, INT-005 (validation halt behavior) |

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
