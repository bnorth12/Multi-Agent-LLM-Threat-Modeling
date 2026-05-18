# Traceability Delta Appendix Sprint 2026-11

Date: 2026-05-14
Status: Complete (updated through sprint closeout)
Purpose: Map each changed requirement and documentation line to corresponding runtime and test files for sprint-close governance evidence.

## 1. Delta Mapping Table

| Source file | Source line | Change summary | Runtime file mapping | Test file mapping | Verification evidence status |
|---|---:|---|---|---|---|
| Requirements/01_Project_Requirements.md | 27 | PRJ-023 updated to require governed release profiles run with execution_mode=langgraph-compatible | src/threat_modeler/orchestrator.py:327, src/threat_modeler/orchestrator.py:342, src/threat_modeler/backend/run_manager.py:223, src/threat_modeler/config.py:78 | Tests/integration/test_agent_pipeline_completeness.py:293, Tests/integration/test_agent_pipeline_completeness.py:302, Tests/integration/test_avionics_expected_results.py:51, Tests/integration/test_avionics_expected_results.py:64, Tests/integration/test_validation_gates.py:45 | Complete (Lane A and ordered validation evidence captured in sprint execution summary, 2026-05-17) |
| Requirements/01_Project_Requirements.md | 33 | PRJ-029 added for live run liveness fail-closed behavior | src/threat_modeler/backend/run_manager.py:107, src/threat_modeler/backend/run_manager.py:271, src/threat_modeler/ui/execution.py:95 | Tests/e2e/test_browser_run_validation.py:181, scripts/live_browser_e2e_smoke.py:596 | Complete (Lane C watchdog and FAILED-state evidence captured, 2026-05-17) |
| Requirements/01_Project_Requirements.md | 34 | PRJ-030 added for backend prompt-store authority and fail-closed prompt loading | src/threat_modeler/ui/prompt_store.py:40, src/threat_modeler/backend/prompt_store.py:12, src/threat_modeler/agents/base.py:185 | Tests/unit/test_ui_backend_prompt_sync.py:17, Tests/unit/test_agent_base_prompt_loading.py:16, Tests/integration/test_prompt_edit_to_execution.py:15 | Complete (S11-017/S11-018 verification evidence captured, 2026-05-17) |
| Requirements/04_Traceability_Matrix.md | 32 | PRJ-023 mapping reconciled to include C01-ORCH-003 governance authority | src/threat_modeler/config.py:39, src/threat_modeler/backend/runtime_state.py:35, src/threat_modeler/server/api.py:80 | Tests/unit/test_execution_mode_governance.py:1, Tests/integration/test_agent_pipeline_completeness.py:314 | Complete (S11-004 reconciliation evidence and issue closure captured, 2026-05-17) |
| Requirements/04_Traceability_Matrix.md | 72 | Legacy orchestrator linkage replaced with active FrameworkOrchestrator LangGraph unit coverage mapping | src/threat_modeler/orchestrator.py:326, src/threat_modeler/orchestrator.py:551 | Tests/unit/test_framework_orchestrator_langgraph.py:1 | Complete (S11-003 test evidence captured, 2026-05-17) |
| Requirements/04_Traceability_Matrix.md | 73 | Execution-mode governance linkage added to dedicated unit suite | src/threat_modeler/config.py:39, src/threat_modeler/backend/runtime_state.py:35, src/threat_modeler/server/api.py:80 | Tests/unit/test_execution_mode_governance.py:1 | Complete (S11-001 governance evidence captured, 2026-05-17) |
| Requirements/10_GUI_Requirements.md | 56 | GUI-026 added for run liveness telemetry and timeout visibility | src/threat_modeler/ui/execution.py:95, src/threat_modeler/ui/screens/home.py:141 | Tests/e2e/test_browser_run_validation.py:181, scripts/live_browser_e2e_smoke.py:596 | Complete (S11-014 evidence captured in sprint summary, 2026-05-17) |
| Requirements/10_GUI_Requirements.md | 57 | GUI-027 added for consolidated Run Diagnostics panel | src/threat_modeler/ui/screens/home.py:188 | scripts/live_browser_e2e_smoke.py:657 | Complete (S11-015 evidence captured in sprint summary, 2026-05-17) |
| Requirements/10_GUI_Requirements.md | 58 | GUI-028 added for improved execution error rendering and provider status extraction | src/threat_modeler/ui/screens/home.py:243, src/threat_modeler/ui/screens/stage_results.py:134 | scripts/live_browser_e2e_smoke.py:664 | Complete (S11-016 evidence captured in sprint summary, 2026-05-17) |
| Requirements/10_GUI_Requirements.md | 59 | GUI-029 added for last-prompt response correlation semantics | src/threat_modeler/ui/screens/last_prompt.py:1 | Tests/unit/test_last_prompt_runtime.py:1 | Complete (GUI correlation behavior validated in unit coverage, 2026-05-17) |
| Requirements/Components/C01_Orchestrator_State_Requirements.md | 7 | C01-ORCH-003 added for execution mode governance (linear compatibility, langgraph-compatible governed release mode) | src/threat_modeler/config.py:78, src/threat_modeler/backend/runtime_state.py:64, src/threat_modeler/orchestrator.py:326, src/threat_modeler/orchestrator.py:327, src/threat_modeler/server/api.py:80 | Tests/integration/test_agent_pipeline_completeness.py:293, Tests/integration/test_avionics_expected_results.py:51, Tests/unit/test_live_mode_failover_halt.py:51 | Complete (Lane A and ordered validation evidence captured in sprint execution summary, 2026-05-17) |
| Requirements/Components/C11_LLM_Requirements.md | 8 | C11-LLM-004 added for live timeout/retry default budget (900s, 2 attempts) | src/threat_modeler/config.py:25, src/threat_modeler/llm/openai_compatible_adapter.py:1 | Tests/e2e/test_live_llm_validation.py:78, Tests/unit/test_openai_compatible_adapter.py:1 | Complete (live profile and adapter behavior evidence captured, 2026-05-17) |
| Requirements/HITL-012-014_Conditional_Gate_State_Reporting.md | 43 | Stale orchestrator path corrected to current orchestrator module | src/threat_modeler/orchestrator.py:277, src/threat_modeler/orchestrator.py:342 | Tests/integration/test_hitl_gate_set_2.py:274 | Complete (Lane A regression and gate validation evidence captured in sprint execution summary, 2026-05-17) |
| docs/User_Manual.md | 288 | execution_mode default documented as langgraph-compatible with linear marked compatibility-only | src/threat_modeler/config.py:39, src/threat_modeler/backend/runtime_state.py:35 | Tests/unit/test_execution_mode_governance.py:1, Tests/integration/test_agent_pipeline_completeness.py:314 | Complete (documentation/runtime alignment verified in sprint closeout evidence, 2026-05-17) |
| docs/User_Manual.md | 300 | Execution Mode Policy section added (linear compatibility mode, langgraph-compatible release mode) | src/threat_modeler/orchestrator.py:326, src/threat_modeler/orchestrator.py:327, src/threat_modeler/orchestrator.py:342 | Tests/integration/test_validation_gates.py:45, Tests/integration/test_agent_pipeline_completeness.py:302 | Complete (documentation/runtime alignment verified in sprint closeout evidence, 2026-05-17) |
| docs/User_Manual.md | 304 | RC verification instruction added to require execution_mode=langgraph-compatible evidence capture | src/threat_modeler/backend/run_manager.py:223, src/threat_modeler/server/api.py:80 | Tests/e2e/test_live_llm_validation.py:209, Tests/e2e/test_browser_cav_markdown_upload.py:22 | Complete (Lane B/Lane C evidence captured in sprint execution summary, 2026-05-17) |
| docs/architecture/framework_overview.md | 88 | Execution Mode Semantics section added | src/threat_modeler/orchestrator.py:326, src/threat_modeler/orchestrator.py:342, src/threat_modeler/config.py:78 | Tests/integration/test_agent_pipeline_completeness.py:293, Tests/integration/test_validation_gates.py:45 | Complete (architecture/runtime/test alignment verified in sprint closeout evidence, 2026-05-17) |
| docs/architecture/framework_overview.md | 96 | Explicit governed profile requirement for execution_mode=langgraph-compatible | src/threat_modeler/backend/run_manager.py:223, src/threat_modeler/orchestrator.py:327 | Tests/unit/test_live_mode_failover_halt.py:51, Tests/integration/test_avionics_expected_results.py:51 | Complete (architecture/runtime/test alignment verified in sprint closeout evidence, 2026-05-17) |
| docs/user_manual/index.html | 993 | HTML manual default updated to langgraph-compatible with linear compatibility-only guidance | src/threat_modeler/config.py:39, src/threat_modeler/backend/runtime_state.py:35 | Tests/unit/test_execution_mode_governance.py:1, Tests/e2e/test_live_llm_validation.py:209 | Complete (manual parity checks and sprint execution evidence captured, 2026-05-17) |

## 2. Update Procedure During Sprint

When a requirement or documentation line changes:

1. Add a new row to the table.
1. Include exact source line and concise change summary.
1. Map to at least one runtime file and one test file.
1. Update verification status when evidence is captured.

## 3. Sprint-Close Completion Criteria

- Every requirement/doc line changed during sprint appears in this appendix.
- Every row maps to at least one runtime file and one test file.
- Evidence status updated from pending to complete or waived with rationale.
- Appendix is referenced in planning/Test_Execution_Summary_Sprint_2026_11.md.
