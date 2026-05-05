# Issue: Sprint 2026-06 HITL Gate Set 2

## Sprint
2026-06

## GitHub Issue
GH #19

## Owner Role
HITL and Audit Engineer

## Description
Implement the backend HITL gate engine for Gates 3–7 (STRIDE calibration, threat plausibility,
mitigation adequacy, conditional merge conflict resolution, conditional export consistency), including
audit record production, draft save, accept/reject behavior, and selective rerun. UI screens for these
gates are delivered in S06-07 (Streamlit App Shell) after this backend is in place.

## Scope

### Mandatory Post-Stage Gates
- Gate 3: STRIDE Calibration — triggers after `agent_04` completes.
- Gate 4: Threat Plausibility — triggers after `agent_05` completes.
- Gate 5: Mitigation Adequacy — triggers after `agent_07` completes.

### Conditional Gates
- Gate 6: Merge Conflict Resolution — triggers when context merge detects conflict with approved
  baseline; controlled by `hitl_trigger_rules.json` conflict thresholds.
- Gate 7: Export Consistency — triggers before publication when canonical JSON, STIX, diagram, or
  report consistency checks fail or exceed warning thresholds.

### Backend Engine
- Extend `GateEngine` to register gates 3–7 following the same `gate_0/1/2` pattern.
- Extend `_MANDATORY_POST_STAGE_GATES` in `orchestrator.py` to include `agent_04`, `agent_05`,
  `agent_07` mappings.
- Conditional gate trigger logic reads `hitl_trigger_rules.json` thresholds.
- All gate actions (accept-as-is, accept-changes, save-draft, reject) produce audit entries via
  `HitlAuditLog.record()`.
- Edit action computes before/after diff via `_compute_diff`.
- `submit_decision()` advances or halts pipeline per gate status.

### Selective Rerun
- `resume_from_checkpoint()` accepts a gate_id to re-enter pipeline from the associated stage.
- Prior approved stages are not recomputed on selective rerun.

## Acceptance Criteria
- Gates 3, 4, and 5 open automatically after their associated stages in orchestrated runs.
- Conditional gate 6 triggers only when conflict conditions in `hitl_trigger_rules.json` are met; does
  not trigger on clean merge.
- Conditional gate 7 triggers only when export consistency checks fail or exceed thresholds; does not
  trigger on consistent output.
- Accept-as-is and accept-changes both advance to the next configured stage.
- Save-draft does not advance stage execution.
- Reject halts pipeline and sets `hitl_rejected_at_gate` on state.
- Every gate decision (all five gate IDs) produces an auditable record with actor, timestamp,
  rationale, and before/after diff.
- Selective rerun from a gate resumes execution without recomputing prior approved stages.
- All behaviors are covered by integration tests using fixture-mode agents (no LLM required).

## Requirement Links
- PRJ-006
- PRJ-007
- HITL-003
- HITL-004
- HITL-005
- HITL-010
- HITL-011

## Dependencies
- S06-01 (Agent Pipeline Completeness) — gates 3/4/5 depend on stages 04/05/07 being registered.

## Implementation Notes
- Gate UI screens (view, edit, approve, reject per gate) are in scope for S06-07, not this issue.
- Follow Gate Set 1 patterns in `src/threat_modeler/hitl/` exactly; extend rather than refactor.

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- Gates 3 (STRIDE Calibration), 4 (Threat Plausibility), 5 (Mitigation Adequacy) registered and wired to agent_04, agent_05, agent_07 respectively.
- Conditional Gate 6 (Merge Conflict) and Gate 7 (Export Consistency) implemented with threshold-based trigger logic from `hitl_trigger_rules.json`.
- All five gate actions (accept-as-is, accept-changes, save-draft, reject, selective-rerun) produce audit entries.
- `resume_from_checkpoint()` resumes without recomputing prior approved stages.
- Integration test suite `Tests/integration/test_hitl_gate_set_2.py` covers all ACs in fixture mode.
- CI test run: 240 passed, 1 deselected (llm_live), 0 failures.
