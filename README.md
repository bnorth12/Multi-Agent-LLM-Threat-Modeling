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

**Sprint 2026-09 in progress** (Backend architecture decoupling; UI viewer expansion; LangGraph migration preparation).

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

### Sprint 2026-09 Open Workstreams

- **S09-1** — UI Artifact Viewer Expansion (STIX, Canonical Graph, Mermaid, STRIDE viewers)
- **S09-2** — STRIDE Export Capability
- **S09-3** — Results Export Quick Preview Defect
- **S09-4** — LangGraph `StateGraph` swap-in via `run_manager.submit_run()` seam

## Getting Started

```sh
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Launch the operational API server (preferred)
python -m threat_modeler

# Or launch on a custom port
python -m threat_modeler --port 9000

# Streamlit is for automated browser validation only (non-operational)
pip install -r Tests/requirements_e2e.txt
streamlit run src/threat_modeler/ui/app.py

# Run all unit tests
python -m pytest Tests/unit/ -q
```
