# Sprint 2026-10 Issue Tracker

This tracker is the in-repo canonical status view for the LangGraph refactor sprint.

## 1. Sprint Scope

- Refresh LangGraph migration planning baseline.
- Implement LangGraph-native orchestration.
- Update requirements and documentation.
- Expand automated test coverage, including visible-browser CAV markdown upload workflow.

## 2. Checklist

| ID | GitHub Issue | Workstream | Status | Notes |
|----|--------------|-----------|--------|-------|
| S10-001 | TBD | LangGraph native execution path | **Closed** | Implemented in `src/threat_modeler/orchestrator.py`; run manager now calls `run_planned_stages()` |
| S10-002 | TBD | Requirements + documentation refresh | **Closed** | Requirements, verification, traceability, planning plan refreshed for LangGraph sprint |
| S10-003 | TBD | Visible browser CAV markdown upload automation | **Closed** | Added `Tests/e2e/test_browser_cav_markdown_upload.py` and CAV markdown fixture |
| S10-004 | TBD | Sprint closure notes + PR closeout mapping | **Closed** | Issue closure notes added in per-issue files and PR closeout section |

## 3. Defect/Change Log

| ID | Type | Status | Verification |
|----|------|--------|--------------|
| D-S10-001 | Compatibility seam replaced by LangGraph execution graph | Resolved | Unit/integration test execution with LangGraph dependency installed |
| D-S10-002 | Execution manager patch point mismatch in failover test | Resolved | `Tests/unit/test_live_mode_failover_halt.py` updated to patch `backend.run_manager.FrameworkOrchestrator` |
| D-S10-003 | Missing visible-browser CAV upload automation path | Resolved | `Tests/e2e/test_browser_cav_markdown_upload.py` added (opt-in run) |

## 4. Closure Notes

- Sprint work completed on branch: `copilot/langgraph-implementation-refresh-docs`.
- Issue files include implementation and verification notes.
- GitHub issue IDs remain `TBD` in this environment; add IDs and auto-close keywords in PR once IDs are created.
