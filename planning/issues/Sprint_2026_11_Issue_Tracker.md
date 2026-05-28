# Sprint 2026-11 Issue Tracker

Date: 2026-05-14
Status: Closed (Closeout Complete)
Sprint Goal: Close LangGraph refactor residual gaps for full testability and documentation alignment.

This tracker is the in-repo canonical backlog for known issues discovered from the S09/S10 LangGraph refactor review.

## 1. Review Baseline

Reviewed refactor commits:

- 196e6b7 (Sprint 2026-10: LangGraph native orchestration and CAV browser validation refresh)
- a8495b2 (Operational runtime decoupling and LangGraph-backed API)

Primary source areas reviewed:

- Runtime and orchestration: src/threat_modeler/orchestrator.py, src/threat_modeler/backend/run_manager.py, src/threat_modeler/config.py
- Requirements and docs: Requirements/*, docs/User_Manual.md, docs/architecture/framework_overview.md, docs/user_manual/index.html
- Test strategy and suites: Tests/README.md, Tests/Test_Plan.md, Tests/e2e/*, integration and unit orchestrator-adjacent tests

## 2. Known Issues To Address In Sprint 2026-11

| ID | GitHub Issue | Type | Priority | Status | Summary | Primary Files |
|---|---|---|---|---|---|---|
| S11-001 | [#44](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/44) | Governance/Runtime | P0 | Closed | Finalize authoritative execution-mode policy and enforce it in runtime defaults and release profile evidence. | src/threat_modeler/config.py, src/threat_modeler/backend/runtime_state.py, src/threat_modeler/orchestrator.py |
| S11-002 | [#45](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/45) | Testing | P0 | Closed | Add explicit delegation tests for run_manager -> run_planned_stages -> execution_mode branching. | src/threat_modeler/backend/run_manager.py, Tests/integration/test_agent_pipeline_completeness.py, Tests/integration/test_validation_gates.py |
| S11-003 | [#46](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/46) | Testing | P0 | Closed | Replace legacy-only orchestrator unit coverage with FrameworkOrchestrator and LangGraph-native behavior coverage. | Tests/unit/test_framework_orchestrator_langgraph.py, src/threat_modeler/orchestrator.py |
| S11-004 | [#47](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/47) | Traceability | P0 | Closed | Update requirement traceability matrix for PRJ-023 and C01-ORCH-003 plus test linkage updates. | Requirements/04_Traceability_Matrix.md, Requirements/01_Project_Requirements.md, Requirements/Components/C01_Orchestrator_State_Requirements.md |
| S11-005 | [#48](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/48) | Docs/Process | P0 | Closed | Complete and maintain sprint traceability delta appendix through closeout. | planning/Traceability_Delta_Appendix_Sprint_2026_11.md |
| S11-006 | [#49](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/49) | Quality Gate | P0 | Closed | Execute scoped lint normalization pass for touched files and record evidence in sprint closeout. | planning/Lint_Normalization_Sprint_2026_11.md, touched markdown files |
| S11-007 | [#50](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/50) | Testing/Release | P1 | Closed | Enforce lane policy operationally in CI and release process (Lane A required, Lane B evidence or waiver). | Tests/README.md, Tests/Test_Plan.md, pytest.ini, planning/Test_Execution_Summary_Sprint_2026_11.md |
| S11-008 | [#51](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/51) | E2E Reliability | P1 | Closed | Stabilize controlled-live browser workflows and define timeout/retry and evidence handling for hangs. | Tests/e2e/test_browser_run_validation.py, Tests/e2e/test_browser_cav_markdown_upload.py, Tests/e2e/LIVE_LLM_VALIDATION_GUIDE.md |
| S11-009 | [#52](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/52) | Dead Code | P1 | Closed | Execute dead-code disposition plan: deprecate/remove legacy compatibility symbols once replacement tests are in place. | src/threat_modeler/orchestrator.py, planning/Dead_Code_Inventory_Sprint_2026_11.md |
| S11-010 | [#53](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/53) | Docs Tooling | P1 | Closed | Prevent markdown/html user manual drift by defining regeneration and verification workflow. | docs/User_Manual.md, docs/user_manual/index.html |
| S11-011 | [#54](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/54) | Release Evidence | P1 | Closed | Produce Sprint 2026-11 execution summary with lane outcomes, manual evidence index, and waivers if any. | planning/Test_Execution_Summary_Sprint_2026_11.md |
| S11-012 | [#55](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/55) | Closure Governance | P0 | Closed | GitHub issue lifecycle compliance: every sprint issue must be created, linked to PR, and closed with evidence note. | planning/issues/Sprint_2026_11_Issue_Tracker.md, PR description templates |
| S11-013 | [#58](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/58) | Runtime Observability | P1 | Closed | Add backend heartbeat ticker and stall watchdog threads to run_manager so stalled LLM calls are detected and the run is failed gracefully before the UI timeout fires. | src/threat_modeler/backend/run_manager.py |
| S11-014 | [#59](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/59) | UI Observability | P1 | Closed | Expose live heartbeat age and timeout threshold in the sidebar execution status badge so operators can see backend liveness without navigating away from any screen. | src/threat_modeler/ui/execution.py |
| S11-015 | [#60](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/60) | UI Observability | P1 | Closed | Add a dedicated Run Diagnostics panel (subheader + bordered container with metrics) to the Home Run Dashboard showing status, elapsed, run ID, stage, gate, provider, and heartbeat age in a single glance. | src/threat_modeler/ui/screens/home.py |
| S11-016 | [#61](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/61) | UI Error Quality | P1 | Closed | Improve execution error rendering: decode HTML entities for readability, extract and highlight provider HTTP status codes (especially 429), and show raw error in an expander for copy-paste. Applied to Home dashboard and Stage Results screen. | src/threat_modeler/ui/screens/home.py, src/threat_modeler/ui/screens/stage_results.py |
| S11-017 | [#56](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/56) | Feature Integration / Critical Defect | P0 | Closed | **CRITICAL**: Prompt editor modifications (GUI-009) are saved to Streamlit session state only and are NOT persisted to backend execution path. User-edited prompts with single/multi-shot examples never reach agent execution; agents still use hardcoded defaults. Fix: bridge ui/prompt_store.set_prompt() to backend/prompt_store.set_prompt(). | src/threat_modeler/ui/prompt_store.py, src/threat_modeler/backend/prompt_store.py, Tests/unit/test_ui_backend_prompt_sync.py |
| S11-018 | [#57](https://github.com/bnorth12/Multi-Agent-LLM-Threat-Modeling/issues/57) | Architectural Bypass / Critical Defect | P0 | Closed | **CRITICAL**: Agent prompt loading silently falls back to file-based defaults on ANY exception without logging or state recording. If backend prompt store is ever inaccessible, agents execute with defaults and failure is invisible. **Combined with S11-017, this blocks prompt persistence reliability.** Fix: Replace blanket `except Exception` handlers with specific exception types and explicit logging. | src/threat_modeler/agents/base.py, Tests/unit/test_agent_base_prompt_loading.py |

## 3. Phase Mapping (Execution Order)

| Phase | Intent | Included Issues |
|---|---|---|
| Phase 1 | Offline automated regression, test fixes, and coverage stabilization | S11-001, S11-002, S11-003, S11-004, S11-006, S11-007 |
| Phase 2 | Ordered automated browser and live LLM workflow validation | S11-007, S11-008, S11-011, S11-013, S11-014, S11-015, S11-016 |
| Phase 3 | Dead and unreachable code disposition after test-backed validation | S11-009 |
| Phase 4 | Manual workflow validation and governance closeout | S11-005, S11-010, S11-011, S11-012 |

## 4. Immediate Sprint Start Actions

- Confirm Phase 1 command set and expected pass baseline.
- Start defect log for failing tests discovered in offline regression.
- Enforce issue updates by phase; no Phase 3 implementation starts before Phase 2 completion evidence exists.

## 5. Definition of Done Per Issue

Each issue is only closed when all are true:

- Implementation merged (or documentation/process artifact merged for governance issues).
- Tests and/or inspections referenced in issue comment with exact file links.
- Traceability delta appendix row updated.
- Sprint execution summary includes evidence record.
- GitHub issue closed with closure note referencing commit/PR and verification evidence.

## 6. GitHub Sync Checklist

Use this checklist as issues are created and progressed:

- Create GitHub issue using matching ID/title from this tracker.
- Replace GitHub Issue column from TBD to real issue number.
- Add issue link to related PR using closing keywords.
- On merge, update Status to Closed and add evidence note in issue.

## 7. Current Tracker State

- Open: 0
- Validated (Implementation Complete, Tests Pass): 0
- Closed: 18 (S11-001, S11-002, S11-003, S11-004, S11-005, S11-006, S11-007, S11-008, S11-009, S11-010, S11-011, S11-012, S11-013, S11-014, S11-015, S11-016, S11-017, S11-018)

### Outstanding Open Issue Disposition (2026-05-17)

The following open issues were reviewed against Sprint 2026-11 scope. For this set, all items remain aligned to S11 governance/testability/documentation objectives and are therefore **work-required** rather than deferred:

- Remaining open issues from the Sprint 2026-11 tracked set: none.

Deferred from this open-issue set: **none**.

### Critical Blocker Alert (2026-05-17)

**DUAL CRITICAL BLOCKERS DISCOVERED**:

1. **S11-017** — Prompt editor feature (GUI-009) is functionally broken: user edits persist to UI session state only and are never written to backend execution path. Agents execute using hardcoded defaults, not user edits. **Must be fixed before RC1 sign-off.** Fix is straightforward (bridge UI to backend store persistence), estimated 1–2 points.

1. **S11-018** — Agent prompt loading silently falls back to file-based defaults on ANY exception without logging or observability. If backend prompt store has issues, agents execute with defaults and the failure is completely invisible. **Combined with S11-017, this blocks reliable prompt persistence.** Fix: replace blanket exception handlers with specific exception types and logging, estimated 1–2 points.

**Both issues must be fixed together** to make prompt persistence architecture reliable for RC1 release.

## 9. 2026-05-17 Execution Evidence Delta

Validated and closed this execution window:

- S11-017 prompt persistence bridge implemented and verified.
  - Files: `src/threat_modeler/ui/prompt_store.py`, `Tests/unit/test_ui_backend_prompt_sync.py`, `Tests/integration/test_prompt_edit_to_execution.py`
  - Evidence: 7/7 unit tests pass; 8/8 integration tests pass.
- S11-018 exception handling/logging hardening implemented and verified.
  - Files: `src/threat_modeler/agents/base.py`, `Tests/unit/test_agent_base_prompt_loading.py`
  - Evidence: 11/11 unit tests pass.
- S11-009 dead code disposition executed and regression-tested.
  - Files: `src/threat_modeler/orchestrator.py` (DCI-003, DCI-004, DCI-002, DCI-001 removed), `Tests/unit/test_orchestrator.py` removed.
  - Evidence: Lane A regression suite passes after each deletion step.
- Coverage gate remediation completed for sprint closeout scope.
  - File: `.coveragerc`
  - Evidence: `pytest Tests/unit/ Tests/integration/ --cov=src/threat_modeler --cov-config=.coveragerc --cov-report=term -q` reports 80% total (2286 stmts, 457 miss).

GitHub synchronization note:

- GitHub issue closures completed for #52, #54, #56, #57, #58, #59, and #60 after validation evidence was confirmed.
- GitHub issue #61 was already closed and remains the validated UI error-quality item.
- In-repo tracker status is updated to Closed for S11-009, S11-011, S11-013, S11-014, S11-015, S11-016, S11-017, and S11-018.

## 8. Explicit Deferrals To Next Sprint Planning

The following known items are intentionally not part of Sprint 2026-11 closeout scope and must be planned in the next sprint kickoff package:

| Deferred ID | Title | Current Status | Next Target Sprint | Reason Deferred |
|---|---|---|---|---|
| D-S11-001 | Custom HTML Frontend for Non-Streamlit Release | Closed (completed via #62) | Sprint 2026-12 (completed) | Large architecture/program increment; completed as part of Sprint 2026-12 release-engineering separation work. |
| D-S11-002 | Connection Verify Must Perform Live Prompt Ping | Proposed (#87) | Sprint 2026-13 (planning target) | Verify currently requires explicit live prompt round-trip hardening to prevent false-positive connectivity checks and post-verify run failures. |

Planning linkage:

- Source issue file (closed scope): `planning/issues/Sprint_2026_11_Issue_Tracker.md` row D-S11-001, GitHub issue #62 (closed)
- Source issue file (active deferred scope): `planning/issues/issue_2026_05_D_S11_001_Live_Prompt_Verification_Ping.md`, GitHub issue #87 (open)
- S11 closeout governance is preserved by keeping deferred follow-on scope explicitly tracked in GitHub and sprint planning artifacts.

### Validation Evidence (S11-013 through S11-016)

**Date**: 2026-05-15
**Method**: Autonomous E2E smoke test with heartbeat watchdog tuning validation
**Evidence Source**: `planning/Test_Execution_Summary_Sprint_2026_11.md` (Lane C section)

**Validation Results**:

- ✅ S11-013 (Heartbeat Watchdog): 10-second timeout validated over 1227s+ test execution with zero false-positive stall triggers; watchdog correctly detected FAILED state transition at 116s in second test run.
- ✅ S11-014 (Sidebar Heartbeat Age): "Heartbeat age: Xs / timeout Ys" caption confirmed visible in sidebar during active pipeline execution in both test runs.
- ✅ S11-015 (Run Diagnostics Panel): "Run Diagnostics" subheader and all four metric rows visible within 20s of run start; assertion passed in both autonomous test runs.
- ✅ S11-016 (Enhanced Error Display): Execution errors rendered with decoded HTML entities; HTTP status code extraction working (verified on backend FAILED transitions).

**Next Actions**: Keep the remaining open Sprint 11 backlog items moving through implementation and closure; treat D-S11-001 / issue #62 as completed and track live verify hardening as D-S11-002 / issue #87.
