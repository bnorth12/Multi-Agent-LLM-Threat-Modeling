---
name: architecture-design-traceability-auditor
description: "Audit architecture/design traceability alignment from requirements through implementation and verification, including planned concept gaps versus as-built state."
---
# Architecture/Design Traceability Auditor Skill

## Purpose
Audit whether the architecture and design framework supports the requirement shape, implementation approach, and verification plan.

## Inputs
- Requirement files under Requirements/
- Architecture and design files under docs/architecture/ and docs/design/
- Sprint planning and issue-tracker artifacts under planning/
- Implementation and verification evidence under src/, frontend/src/, scripts/, and Tests/

## Procedure
1. Identify requirement IDs that have architecture/design references.
2. Separate concept-only planned items from as-built implementation.
3. Flag implementation that is not backed by architecture/design references.
4. Highlight gaps where the implementation shape does not match the documented design framework.
5. Return prioritized remediation notes for architecture and design iteration.

## Outputs
- Requirement IDs missing architecture/design traceability.
- Concept-vs-as-built gap list.
- Implementation-shape mismatch notes.
- Iteration recommendations for design updates.
