# Partial 15 Verification Backfill

## Purpose

Execute remediation waves by adding verification-artifact anchors for reachable modules that remain partial due to missing verification linkage.

## Backfill Rows

| Code Module | Requirement ID(s) | Verification Artifact Anchor(s) |
|---|---|---|
| src/threat_modeler/__main__.py | ORCH-001, INT-005 | Tests/test_hmi_backend_api.py; Tests/integration/test_agent_pipeline_completeness.py |
| src/threat_modeler/agents/deserialise.py | PRJ-005, INT-003 | Tests/integration/test_agent_pipeline_completeness.py |
| src/threat_modeler/backend/prompt_store.py | SCR-010, SCR-011 | Tests/integration/test_prompt_edit_to_execution.py; Tests/unit/test_prompt_requirements_baseline.py |
| src/threat_modeler/hitl/models.py | HITL-009, GUI-032 | Tests/integration/test_hitl_gate_set_1.py; Tests/integration/test_hitl_gate_set_2.py |
| src/threat_modeler/llm/llm_provider_error.py | C11-LLM-004, LLM-004 | Tests/unit/test_openai_compatible_adapter.py; Tests/e2e/test_live_llm_validation.py |
| src/threat_modeler/models/canonical.py | PRJ-005, INT-003 | Tests/integration/test_canonical_graph_viewer.py; Tests/integration/test_agent_pipeline_completeness.py |
| src/threat_modeler/server/hmi_data.py | SCR-004, GUI-032, RHMI-016 | Tests/test_hmi_backend_api.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
| src/threat_modeler/state.py | ORCH-001, INT-005, SCR-014, RHMI-016 | Tests/unit/test_framework_orchestrator_langgraph.py; Tests/unit/test_token_usage_runtime.py |
| src/threat_modeler/ui/debug.py | GUI-031, RHMI-005 | Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/theme.py | GUI-003, GUI-031 | Tests/e2e/test_frontend_react_mui_full_workflow.py |
| src/threat_modeler/validation.py | SCR-014, GUI-032 | Tests/integration/test_validation_gates.py |
