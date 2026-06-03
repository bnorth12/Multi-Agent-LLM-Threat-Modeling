# Function-Level Verification Matrix

## Purpose

Provide persistent verification traceability for source-derived L3 and L4 function IDs in architecture, with explicit test artifact anchors for each function row.

## Scope

- Authority source for function IDs: docs/architecture/Function_Hierarchy_Registry.md
- Covered function levels: L3 and L4 source-derived decomposition rows
- Verification authority source: test artifacts under Tests/

## Matrix

| Function ID | Function Level | Implementation Anchor | Verification Test Anchor(s) |
|---|---|---|---|
| F-L3-CLI-ENTRYPOINT-BOOTSTRAP | L3 | src/threat_modeler/__main__.py | Tests/unit/test_main_operational_server_entrypoint.py; Tests/unit/test_operational_api_server.py |
| F-L4-CLI-ARGPARSE-DISPATCH | L4 | src/threat_modeler/__main__.py | Tests/unit/test_main_operational_server_entrypoint.py; Tests/unit/test_operational_api_server.py |
| F-L3-INT-DESERIALIZATION-SERVICES | L3 | src/threat_modeler/agents/deserialise.py | Tests/integration/test_agent_pipeline_completeness.py; Tests/integration/test_validation_gates.py |
| F-L4-INT-GRAPH-PARSE-COERCION | L4 | src/threat_modeler/agents/deserialise.py | Tests/integration/test_agent_pipeline_completeness.py; Tests/integration/test_validation_gates.py |
| F-L3-ORCH-PROMPT-STATE-STORE | L3 | src/threat_modeler/backend/prompt_store.py | Tests/unit/test_backend_prompt_store.py; Tests/unit/test_ui_backend_prompt_sync.py |
| F-L4-ORCH-PROMPT-MUTATION-APIS | L4 | src/threat_modeler/backend/prompt_store.py | Tests/unit/test_backend_prompt_store.py; Tests/unit/test_ui_backend_prompt_sync.py |
| F-L3-ORCH-RUNTIME-STATE-PERSISTENCE | L3 | src/threat_modeler/backend/runtime_state.py | Tests/integration/test_agent_pipeline_completeness.py; Tests/integration/test_validation_gates.py |
| F-L4-ORCH-RUNTIME-STATE-SERIALIZATION | L4 | src/threat_modeler/backend/runtime_state.py | Tests/integration/test_agent_pipeline_completeness.py; Tests/integration/test_validation_gates.py |
| F-L3-HITL-DECISION-MODEL-SERVICES | L3 | src/threat_modeler/hitl/models.py | Tests/integration/test_hitl_gate_set_2.py; Tests/test_hmi_backend_api.py |
| F-L4-HITL-DECISION-SERIALIZATION | L4 | src/threat_modeler/hitl/models.py | Tests/integration/test_hitl_gate_set_2.py; Tests/test_hmi_backend_api.py |
| F-L3-LLM-EXCEPTION-CONTRACT | L3 | src/threat_modeler/llm/llm_provider_error.py | Tests/unit/test_openai_compatible_adapter.py; Tests/e2e/test_live_llm_validation.py |
| F-L4-LLM-ERROR-METADATA-NORMALIZATION | L4 | src/threat_modeler/llm/llm_provider_error.py | Tests/unit/test_openai_compatible_adapter.py; Tests/e2e/test_live_llm_validation.py |
| F-L3-INT-CANONICAL-GRAPH-MODEL | L3 | src/threat_modeler/models/canonical.py | Tests/unit/test_canonical_graph_schema_validation.py; Tests/integration/test_canonical_graph_viewer.py |
| F-L4-INT-CANONICAL-PLACEHOLDER-BUILD | L4 | src/threat_modeler/models/canonical.py | Tests/unit/test_canonical_graph_schema_validation.py; Tests/integration/test_canonical_graph_viewer.py |
| F-L3-INT-API-RUNTIME-LIFECYCLE | L3 | src/threat_modeler/server/api.py | Tests/unit/test_operational_api_server.py; Tests/test_hmi_backend_api.py |
| F-L4-INT-API-CATALOG-SERIALIZATION | L4 | src/threat_modeler/server/api.py | Tests/unit/test_operational_api_server.py; Tests/test_hmi_backend_api.py |
| F-L3-INT-HMI-DATA-PROJECTION | L3 | src/threat_modeler/server/hmi_data.py | Tests/test_hmi_backend_api.py; Tests/integration/test_results_export_quick_preview.py |
| F-L4-INT-HMI-SERIALIZE-THREAT-GATE | L4 | src/threat_modeler/server/hmi_data.py | Tests/test_hmi_backend_api.py; Tests/integration/test_results_export_quick_preview.py |
| F-L3-ORCH-FRAMEWORK-STATE-METRICS | L3 | src/threat_modeler/state.py | Tests/unit/test_token_usage_runtime.py; Tests/unit/test_run_manager.py |
| F-L4-ORCH-FRAMEWORK-PROMPT-LEDGER | L4 | src/threat_modeler/state.py | Tests/unit/test_token_usage_runtime.py; Tests/unit/test_run_manager.py |
| F-L3-UI-DIAGNOSTICS-PANEL-SERVICES | L3 | src/threat_modeler/ui/debug.py | Tests/unit/test_ui_app_shell.py; Tests/test_hmi_backend_api.py |
| F-L4-UI-DIAGNOSTIC-EXEC-WRAPPER | L4 | src/threat_modeler/ui/debug.py | Tests/unit/test_ui_app_shell.py; Tests/test_hmi_backend_api.py |
| F-L3-UI-PROMPT-STORE-FACADE | L3 | src/threat_modeler/ui/prompt_store.py | Tests/unit/test_prompt_requirements_baseline.py; Tests/unit/test_ui_backend_prompt_sync.py |
| F-L4-UI-PROMPT-STORE-TEMPERATURE | L4 | src/threat_modeler/ui/prompt_store.py | Tests/unit/test_prompt_requirements_baseline.py; Tests/unit/test_ui_backend_prompt_sync.py |
| F-L3-UI-HOME-DASHBOARD-PROJECTION | L3 | src/threat_modeler/ui/screens/home.py | Tests/e2e/test_frontend_react_mui_full_workflow.py; Tests/test_hmi_backend_api.py |
| F-L4-UI-HOME-ERROR-STATUS-DETAIL | L4 | src/threat_modeler/ui/screens/home.py | Tests/e2e/test_frontend_react_mui_full_workflow.py; Tests/test_hmi_backend_api.py |
| F-L3-UI-INPUT-INGESTION-SURFACE | L3 | src/threat_modeler/ui/screens/input_entry.py | Tests/unit/test_input_ingestion.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
| F-L4-UI-INPUT-UPLOAD-PARSER | L4 | src/threat_modeler/ui/screens/input_entry.py | Tests/unit/test_input_ingestion.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
| F-L3-UI-PROMPT-EDITOR-INTERACTION | L3 | src/threat_modeler/ui/screens/prompt_editor.py | Tests/integration/test_prompt_edit_to_execution.py; Tests/unit/test_prompt_requirements_baseline.py |
| F-L4-UI-PROMPT-DIFF-VISUALIZATION | L4 | src/threat_modeler/ui/screens/prompt_editor.py | Tests/integration/test_prompt_edit_to_execution.py; Tests/unit/test_prompt_requirements_baseline.py |
| F-L3-UI-STAGE-RESULTS-PROJECTION | L3 | src/threat_modeler/ui/screens/stage_results.py | Tests/integration/test_results_export_quick_preview.py; Tests/test_hmi_backend_api.py |
| F-L4-UI-STAGE-MESSAGE-NORMALIZATION | L4 | src/threat_modeler/ui/screens/stage_results.py | Tests/integration/test_results_export_quick_preview.py; Tests/test_hmi_backend_api.py |
| F-L3-UI-SESSION-BOOTSTRAP | L3 | src/threat_modeler/ui/session.py | Tests/unit/test_ui_app_shell.py; Tests/test_hmi_backend_api.py |
| F-L4-UI-SESSION-DEFAULT-INITIALIZATION | L4 | src/threat_modeler/ui/session.py | Tests/unit/test_ui_app_shell.py; Tests/test_hmi_backend_api.py |
| F-L3-UI-THEME-APPLICATION-SERVICES | L3 | src/threat_modeler/ui/theme.py | Tests/unit/test_ui_app_shell.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
| F-L4-UI-THEME-TOKEN-MAPPING | L4 | src/threat_modeler/ui/theme.py | Tests/unit/test_ui_app_shell.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
| F-L3-INT-CANONICAL-VALIDATION-SERVICES | L3 | src/threat_modeler/validation.py | Tests/unit/test_canonical_graph_schema_validation.py; Tests/integration/test_validation_gates.py |
| F-L4-INT-VALIDATION-SCHEMA-RANGE-CHECK | L4 | src/threat_modeler/validation.py | Tests/unit/test_canonical_graph_schema_validation.py; Tests/integration/test_validation_gates.py |

## Governance Rule

All L3 and L4 function IDs in docs/architecture/Function_Hierarchy_Registry.md must have at least one matching row in this matrix with non-empty Tests anchors.
