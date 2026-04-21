# Python Dependency Strategy

Status: Pre-implementation planning

## Why Dependencies Are Not Locked Yet

The architecture and requirement contracts are still being normalized. Locking dependencies before the runtime interfaces stabilize would create avoidable churn.

## Dependency Selection Principles

1. Add a dependency only when a requirement or interface explicitly needs it.
1. Prefer stable, widely adopted Python packages with active maintenance.
1. Prefer dependencies with permissive licensing and clear offline usage support.
1. Minimize transitive dependency count for security and maintainability.
1. Keep core runtime dependencies separate from optional feature dependencies.

## Planned Dependency Buckets

Core runtime candidate areas:

- Orchestration and workflow state
- Data validation and schema handling
- Structured logging and observability

Agent capability candidate areas:

- LLM provider adapters
- Retrieval and embeddings
- STIX serialization and validation
- Diagram and report generation

Developer tooling candidate areas:

- Testing and coverage
- Linting and formatting
- Type checking

## Introduction Process

1. Open issue describing requirement-driven need.
1. Document alternatives considered.
1. Record expected usage scope and risk.
1. Add dependency in focused feature branch.
1. Add tests proving required behavior.
1. Update this file and any relevant README files.

## Initial Bootstrapping Guidance

When code scaffolding starts, begin with the smallest viable baseline:

- Python runtime
- test runner
- schema or model validation layer

All additional dependencies should be introduced incrementally based on implemented features.
