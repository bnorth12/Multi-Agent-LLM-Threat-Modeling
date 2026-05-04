# Issue: Sprint 2026-06 HITL Gate Set 2

## Sprint
2026-06

## Owner Role
HITL and Audit Engineer

## Description
Expand HITL controls with additional gates and edit plus rerun support.

## Scope
- STRIDE calibration gate.
- Threat plausibility gate.
- Mitigation adequacy gate.
- Conditional Merge Conflict Resolution gate after context merge conflicts.
- Conditional Export Consistency gate before publication when consistency checks fail or exceed warning thresholds.
- Edit with rationale and before and after diff audit.
- Selective rerun from chosen gate.
- UI supports per-gate artifact view and edit workflows for all active gates.
- UI supports save draft, accept as is, and accept changes actions at all active gates.

## Acceptance Criteria
- All three gates are active in orchestrated runs.
- Conditional merge conflict gate triggers only when configured conflict conditions are met.
- Conditional export consistency gate triggers only when configured consistency conditions are met.
- Edit action produces auditable before and after records.
- At each active gate, analyst can view and edit content prior to approve or reject.
- Save draft does not advance stage execution.
- Accept as is and accept changes both advance to the next configured stage.
- Rerun resumes with preserved run context.

## Requirement Links
- PRJ-006
- PRJ-007
- HITL-003
- HITL-004
- HITL-005
- HITL-010
- HITL-011

## Status
- [ ] Not started
- [ ] In progress
- [ ] Completed
