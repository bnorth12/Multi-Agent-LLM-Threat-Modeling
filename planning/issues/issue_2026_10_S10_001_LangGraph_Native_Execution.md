# S10-001: LangGraph Native Execution Path

## Issue Summary

Replace compatibility-loop orchestration with a LangGraph-native execution graph while preserving validation and HITL behavior.

## Related Requirements

- PRJ-003
- PRJ-004
- PRJ-015
- PRJ-023

## Acceptance Criteria

- [x] Orchestrator executes planned stages through LangGraph `StateGraph`.
- [x] Existing validation halt behavior is preserved.
- [x] Existing mandatory/conditional HITL gates are preserved.
- [x] Resume-from-checkpoint path executes remaining stages with LangGraph.

## Status

Resolved

## Implementation Notes

- `src/threat_modeler/orchestrator.py` now executes stage sequences through LangGraph graph compilation/invocation.
- Legacy `StateGraph` API remains as a LangGraph-backed compatibility wrapper for tests.
- `src/threat_modeler/backend/run_manager.py` now executes via `run_planned_stages()` to honor configured mode.

## Verification

- Unit coverage updated in `Tests/unit/test_orchestrator.py`.
- Execution failover coverage updated in `Tests/unit/test_live_mode_failover_halt.py`.

## Closure Notes

Closed in Sprint 2026-10 implementation branch with LangGraph dependency added in `requirements.txt`.
