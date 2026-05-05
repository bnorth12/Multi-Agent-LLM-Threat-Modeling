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

**Sprint 2026-07 in progress** (GUI workstreams A–F: HMI features, provider selection, validation gates, exporters).

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
- **Streamlit HMI (Partial)** — 4 screens delivered:
  - SCR-001: Home / Run Dashboard (pipeline stage progress)
  - SCR-002: Role Selection (analyst role picker)
  - SCR-003: Configuration (partial; provider selection deferred to S07)
  - SCR-004: Input Entry (file upload, raw text, Start Run)
- **Evidence & Documentation**
  - 240 automated tests passing (unit + integration + E2E)
  - 4 screenshot evidence artifacts (S06)
  - User manual (HTML and Markdown)
  - HMI architecture blueprint (design authority for GUI)

### Sprint 2026-07 Workstreams (In Progress)

- **A (S07-01)** — Documentation & Traceability Cleanup (active)
- **B (S07-02)** — Model Provider Selection HMI (SCR-012/013/014)
- **C (S07-03)** — Input Entry Validation Gate & Offline Override
- **D (S07-04)** — Prompt Editor & Version History (SCR-010/011)
- **E (S07-05/06)** — Results & Export Screens (SCR-003/004, SCR-007/008/009)
- **F (S07-07)** — Test & CI Expansion
- **Closeout (S07-08)** — Required Online E2E Validation Gate

## Getting Started

```sh
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run all tests
.venv\Scripts\python.exe -m pytest Tests/ -q
```
