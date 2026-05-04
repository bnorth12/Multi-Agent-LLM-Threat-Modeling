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

Sprint 2026-05 runtime implementation is underway. The following modules are implemented and tested:

- **Orchestrator** (`src/threat_modeler/orchestrator.py`): LangGraph-compatible stage execution with validation halt behavior
- **Canonical model** (`src/threat_modeler/models/canonical.py`): typed dataclasses for System, Subsystem, Component, Function, Interface, and threat graph
- **Validation** (`src/threat_modeler/validation.py`): `CanonicalGraphValidator`, `ValidationResult`, `ValidationHaltError`
- **Input parsing** (`src/threat_modeler/parsing/icd_parser.py`): CSV and XLSX ICD parsing with Function and Interface entity dispatch; narrative document parser
- **Config** (`src/threat_modeler/config.py`): `RuntimeSettings`, `ModelSelection`, `PipelineSettings`
- **Test suite**: 55 tests passing (43 unit + 12 integration)

Active sprint work: S05-04 HITL gate implementation, S05-05 CI baseline, GUI/HMI implementation (post-sprint).

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
