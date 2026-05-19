# Multi Agent Threat Modeler

Python-first LangGraph multi-agent threat modeling project for aerospace and ICS-style systems.

## Project Concept

This project defines and implements a multi-agent workflow that converts architecture descriptions and data flows into:

- Canonical threat-model graph
- STRIDE scoring and rationale
- Concrete threats with taxonomy mapping
- Mitigation recommendations
- STIX 2.1 export
- Mermaid diagrams
- Human-readable final report

The architecture is designed for human-in-the-loop governance and auditable, stage-based execution.

## Planned Technology Direction

- Primary implementation language: Python
- Orchestration: LangGraph
- Validation: JSON Schema plus Pydantic models
- Testing: Pytest
- Packaging and tooling: Python virtual environment and pip-based dependency management

## Dependency Strategy

Python dependencies are intentionally not finalized yet.

The project will add dependencies in phases after interface and component boundaries are confirmed.
Selection and lock criteria are documented in Python_Dependency_Strategy.md.

## Repository Layout

- docs: source architecture, schemas, prompts, and process references
- planning: phased implementation plans and planning artifacts
- Requirements: formal requirements package and component-level requirement sets
- Releases: release notes and release evidence bundles
- Tests: automated and scenario-based tests
- src: Python source code workspace for runtime, agents, and interfaces

## Current Status

**Sprint 2026-11 closeout execution active**.

Current sprint priority is to finalize alignment, governance, and evidence closure:

- Coverage gate for closeout scope is restored and validated (80% with sprint scope config).
- Final issue-evidence closure and traceability reconciliation are being completed.
- Top-level and sprint documentation are being normalized to a single closeout narrative.

Planned next-sprint architecture direction (deferred from 2026-11 scope):

- Remove Streamlit dependency from the deployed release UX path by introducing a separate production frontend integrated with the operational backend API.
- Keep Streamlit as a development/test harness until the replacement frontend reaches required parity and test coverage.

### Completed Deliverables

**Sprint 2026-05 & 2026-06 — Core Runtime and MVP GUI:**

- **Runtime Pipeline** — 9-agent LangGraph orchestrator with canonical graph validation and HITL gates 1–7
  - Orchestrator with validation halt behavior
  - Canonical model (typed dataclasses)
  - JSON Schema + Pydantic validation
  - Input parsing (CSV, XLSX, Markdown, TXT, YAML)
  - Config and model selection
- **HITL Governance** — 7 mandatory and conditional gates with audit trail, selective rerun, and rejection records
- **Artifact Export** — Canonical JSON, STIX 2.1, Mermaid diagrams, Markdown reports
- **Streamlit HMI** — Full screen set delivered (SCR-001 through SCR-014 plus Prompt Editor, Token Usage, Stage Results, Threat Review, Snapshot Manager, Results Export)
- **Evidence & Documentation**
  - 259 automated tests passing (unit + integration)
  - User manual (HTML and Markdown)
  - HMI architecture blueprint (design authority for GUI)

**Sprint 2026-09 — Backend Architecture Decoupling (Completed):**

- **`backend/run_manager.py`** — Pure-Python pipeline execution engine; no Streamlit dependency.
  Owns `_RUN_REGISTRY`, background threads, orchestrator lifecycle, and HITL gate handling.
  Persists run metadata to `~/.multi_agent_threat_modeler_runs.json` for reload recovery.
  Public API: `submit_run()`, `resume_run()`, `cancel_run()`, `wait_for_run()`, `get_run_status()`.
- **`backend/prompt_store.py`** — Thread-safe, file-backed agent prompt store.
  Persists prompt text, version history, and temperature settings to
  `~/.multi_agent_threat_modeler_prompts.json`.
- **`ui/execution.py`** (refactored) — Now a thin Streamlit adapter; all execution logic
  delegated to `backend/run_manager.py`.
- **`server/api.py`** — operational non-Streamlit HTTP server for run control and LangGraph execution-plan APIs.
- **`__main__.py`** — `python -m threat_modeler` CLI entry point for the operational API server.
- **55 new backend tests** added (total: 259 passing).
- Requirement PRJ-019 (Asynchronous Backend State Authority) fully implemented.

### Sprint 2026-11 Active Closeout Workstreams

- **S11 Governance/Traceability** — execution-mode alignment, traceability delta completion, issue closure evidence.
- **S11 Testing/Release Evidence** — Lane A/Lane B evidence completion, manual validation indexing, closeout summary quality.
- **S11 Documentation Hygiene** — README, manuals, architecture, and sprint documents updated to current runtime behavior and release policy.

## Getting Started

### Quick Start: Runtime Only

```sh
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install runtime dependencies
pip install -r requirements.txt

# Launch the operational API server
python -m threat_modeler

# Or launch on a custom port
python -m threat_modeler --port 9000
```

### Development & Testing

```sh
# Install runtime + test dependencies (includes pytest, playwright, streamlit)
pip install -r Tests/requirements_e2e.txt

# Configure test environment (UTF-8 logs + browser test flags)
.\scripts\set_test_env.ps1

# Run unit tests
python -m pytest Tests/unit/ -q

# Run scripted tests with structured logging under test_reports/YYYY-MM-DD/
python scripts/run_and_log.py scripts/verify_sprint_traceability.py --sprint 2026_11

# Browser E2E smoke (requires GROK_API or GROK_API_KEY)
python scripts/run_and_log.py scripts/live_browser_e2e_smoke.py

# Streamlit HMI (test harness only, not operational)
streamlit run src/threat_modeler/ui/app.py
```

### Git Hooks

Install the repo-managed Git hooks (recommended):

```powershell
.\scripts\install_git_hooks.ps1
```

This configures `core.hooksPath` to `.githooks` for this repository. The included `pre-push` hook runs:
- `python -m pytest Tests/unit/ -q`
- `python scripts/verify_sprint_traceability.py --sprint $TRACEABILITY_SPRINT` (default: `2026_11`)

Behavior:
- Unit tests are blocking.
- Traceability verification is warning-only by default to avoid unnecessary push blockers.
- Set `TRACEABILITY_ENFORCE=1` to make traceability failures blocking.

Use this setup to catch local quality and traceability regressions before opening or updating PRs.

### Dependency Strategy

**Runtime Dependencies** (`requirements.txt`):
- `openai` — LLM integration
- `langgraph` — Agent orchestration
- `chromadb` — Vector store for retrieval
- `stix2` — STIX 2.1 export format
- `python-dotenv` — Environment variable loading

**Test Dependencies** (`Tests/requirements_e2e.txt`):
- Includes all runtime dependencies (via `-r ../requirements.txt`)
- `pytest`, `pytest-cov` — Unit and integration testing
- `playwright`, `pytest-playwright` — Browser automation for E2E
- `streamlit` — Development HMI test harness only
- Additional test utilities (json-report, timeout, etc.)

This separation keeps the production release minimal while providing comprehensive testing infrastructure for development.

## Test Execution

All test commands and infrastructure are documented in [Tests/README.md](Tests/README.md).

### Quick Reference

```bash
# Environment setup (one-time, recommended before test runs)
.\scripts\set_test_env.ps1

# Unit tests (fast, local)
python -m pytest Tests/unit/ -q

# Sprint traceability verification (logs to test_reports/)
python scripts/run_and_log.py scripts/verify_sprint_traceability.py --sprint 2026_11

# E2E browser tests (requires GROK_API environment variable)
python scripts/run_and_log.py scripts/live_browser_e2e_smoke.py
```

### Test Organization

- **Unit tests** → `Tests/unit/` — Fast validation of core functions
- **Integration tests** → `Tests/integration/` — Multi-module orchestration tests
- **E2E tests** → `Tests/e2e/` — Full pipeline from input to artifact export
- **Test fixtures** → `Tests/fixtures/` — Sample inputs and expected outputs
- **Test reports** → `Tests/test_reports/YYYY-MM-DD/[test_type]/` — Logs organized by date and type

### Test Infrastructure

- **`scripts/run_and_log.py`** — Universal test runner with UTF-8 logging and environment validation
- **`scripts/set_test_env.ps1`** — Environment setup (PYTHONIOENCODING, browser flags, GROK_API check)
- **`Tests/requirements_e2e.txt`** — Consolidated test dependencies
- **`Tests/conftest.py`** — Pytest configuration and fixtures
- **`Tests/pytest.ini`** — Pytest test discovery and behavior settings
