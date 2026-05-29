# Tests Directory

This directory contains the Python test suite, test configuration, and test dependencies for the Multi Agent Threat Modeler.

## Setup & Dependencies

### Installation

Test dependencies are separated from runtime dependencies:

```bash
# Install runtime + test dependencies
pip install -r Tests/requirements_e2e.txt
```

This command:

1. Installs runtime dependencies from `requirements.txt` (openai, langgraph, chromadb, stix2, python-dotenv)
1. Installs test-specific dependencies (pytest, playwright, streamlit for test harness)

### Environment Setup

Before running tests, configure the test environment:

```powershell
# PowerShell (Windows)
. .\scripts\set_test_env.ps1
```

This sets:

- `PYTHONIOENCODING=utf-8` (for proper Unicode logging)
- `RUN_VISIBLE_BROWSER_TESTS=1` (for headful E2E tests)
- Validates `GROK_API` availability for browser tests

---

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

Test totals evolve continuously. Treat command output as authoritative rather than this README.

Recommended commands:

```sh
# Total discovered tests
.venv\Scripts\python.exe -m pytest Tests/ --collect-only -q

# Current execution summary
.venv\Scripts\python.exe -m pytest Tests/ -q
```

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

Current automation model:

- Pull request gate: unit plus integration tests
- Main branch gate: full suite including e2e and coverage threshold
- Release gate: full suite plus artifact verification tests

### Lane Policy (Sprint 2026-11)

Lane A: CI-safe default lane

- Scope: unit, integration, and fixture-safe e2e only
- Excludes: tests marked `llm_live` and `llm_live_browser`
- Required on pull requests and main-branch merges

Lane B: controlled-live validation lane

- Scope: tests marked `llm_live` and `llm_live_browser`
- Trigger: scheduled or manually approved execution
- Requirements: live provider credentials, explicit environment controls, and evidence capture

Recommended commands:

```sh
# Lane A: CI-safe default
.venv\Scripts\python.exe -m pytest Tests/ -q -m "not llm_live and not llm_live_browser"

# Lane B1: live provider tests
.venv\Scripts\python.exe -m pytest Tests/e2e/test_live_llm_validation.py -v -m llm_live -s

# Lane B2: browser-live tests (opt-in)
set RUN_VISIBLE_BROWSER_TESTS=1
.venv\Scripts\python.exe -m pytest Tests/e2e/test_browser_cav_markdown_upload.py -v -m llm_live_browser -s

# Lane B2b: React + MUI frontend shell browser validation (Sprint 12)
set RUN_VISIBLE_BROWSER_TESTS=1
.venv\Scripts\python.exe -m pytest Tests/e2e/test_frontend_react_mui_shell.py -v -m "llm_live_browser and frontend_shell" -s

# Optional auth-UI assertion within shell lane (S12 auth readiness)
set RUN_VISIBLE_BROWSER_TESTS=1
set FRONTEND_AUTH_UI_TESTS=1
.venv\Scripts\python.exe -m pytest Tests/e2e/test_frontend_react_mui_shell.py -v -k unauthorized -m "llm_live_browser and frontend_shell" -s

# Lane B2c: React + MUI full workflow browser validation (Sprint 12 full conversion scope)
set RUN_VISIBLE_BROWSER_TESTS=1
set FRONTEND_FULL_BROWSER_TESTS=1
.venv\Scripts\python.exe -m pytest Tests/e2e/test_frontend_react_mui_full_workflow.py -v -m "llm_live_browser and frontend_full" -s

# Lane B3: standalone full E2E smoke (script-first, pytest-independent runtime)
set RUN_VISIBLE_BROWSER_TESTS=1
.venv\Scripts\python.exe scripts/live_browser_e2e_smoke.py

# Lane B3a: manual-followup browser lane (Edge)
set RUN_VISIBLE_BROWSER_TESTS=1
set THREAT_MODELER_BROWSER_CHANNEL=msedge
set THREAT_MODELER_SMOKE_KEEP_OPEN_UNTIL_INPUT=1
.venv\Scripts\python.exe scripts/live_browser_e2e_smoke.py

# Optional pytest wrapper that delegates to the standalone smoke script
set RUN_VISIBLE_BROWSER_TESTS=1
.venv\Scripts\python.exe -m pytest Tests/e2e/test_live_browser_smoke.py -v -s -m llm_live_browser
```

Release governance rule:

- Release candidate sign-off requires Lane A pass plus documented Lane B evidence (or approved waiver with rationale) in the sprint test execution summary.

Dependency boundary hardening:

```sh
# Verify release/runtime manifests do not include test-only dependencies
.venv\Scripts\python.exe scripts/verify_dependency_boundary.py
```

### Smoke Validation Guidance

- Mocked browser token checks are only interaction contracts; they do not prove live provider functionality.
- The authoritative smoke path is a visible browser run against the live provider that exercises the staged pipeline end to end.
- The authoritative smoke runtime entrypoint is `scripts/live_browser_e2e_smoke.py`; this keeps server start/execution independent of pytest internals.
- `Tests/e2e/test_live_browser_smoke.py` is a thin wrapper that only invokes the standalone script for test-lane integration.
- Browser policy: default automated lane uses Playwright Chromium; manual follow-up validation should use Edge by setting `THREAT_MODELER_BROWSER_CHANNEL=msedge`.
- Result-capture policy: keep the final visible browser open until evidence is captured by setting `THREAT_MODELER_SMOKE_KEEP_OPEN_UNTIL_INPUT=1` (or use timed hold with `THREAT_MODELER_SMOKE_HOLD_SECONDS`).
- For the current sprint, the smoke path should focus on the first three stages so gate 3 is reached only after gate 1 and gate 2 have executed in order.
- Use the live-browser smoke test in `Tests/e2e/test_live_browser_smoke.py` for that path.

## Documentation Rules for New Tests

- Every new feature branch should include test additions or explicit rationale for none.
- Every test file should include a short header comment describing scope.
- Every e2e scenario should map to requirement IDs and expected artifacts.
