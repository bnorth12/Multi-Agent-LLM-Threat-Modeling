---
name: architecture-design-disposition-planner
description: "Prepare architecture/design disposition workpacks so remediation execution makes an explicit design-vs-implementation decision with traceability and approval."
---
# Architecture/Design Disposition Planner Skill

## Purpose
Create a deterministic disposition package before implementation closeout so remediation work does not bypass architecture/design decision logic.

## Inputs
- Remediation sprint plan under planning/
- Evidence target list in the selected remediation plan
- Requirement IDs in scope
- Existing architecture/design, implementation, and verification references

## Procedure
1. Parse the selected remediation sprint plan and extract requirement IDs plus evidence targets.
2. Build an authoring workpack that separates architecture/design targets, implementation targets, and verification targets.
3. Flag missing legs in the traceability chain.
4. Require one disposition decision path and a rationale/approval record.

## Outputs
- `local_reviews/latest/architecture_design_authoring_workpack_latest.md`
- `local_reviews/latest/architecture_design_authoring_workpack_latest.json`
- Explicit disposition decision template with approval and rerun-verification fields.
