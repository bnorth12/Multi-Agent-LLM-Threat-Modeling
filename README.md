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

- Docs: source architecture and prompt specifications
- Implemenation Plan: phased implementation plans and planning artifacts
- Requirements: formal requirements package and component-level requirement sets
- Releases: release notes and release evidence bundles
- Tests: automated and scenario-based tests
- Threat Modeler Code: Python source code for runtime, agents, and interfaces

## Current Status

The repository is currently documentation and requirements heavy. The next major phase is Python runtime implementation of the orchestrator, state model, agent interfaces, and test harness.

## Getting Started (Planned)

1. Create and activate a Python virtual environment.
1. Install project dependencies.
1. Run tests.
1. Execute a local sample threat-modeling run.

Implementation commands will be added once code scaffolding is committed.
