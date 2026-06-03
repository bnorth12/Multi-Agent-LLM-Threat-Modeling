# Reachable Module Verification Backfill

## Purpose

Establish verification-artifact trace relationships for reachable implementation modules that had missing verification linkage despite known requirement IDs.

## Backfill Rows

| Code Module | Requirement ID(s) | Verification Artifact Anchor(s) |
|---|---|---|
| src/threat_modeler/ui/connection_validator.py | SCR-013, SCR-014 | Tests/integration/test_validation_gates.py; Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/runtime_io.py | SCR-007 | Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/screens/canonical_graph_viewer.py | GUI-019 | Tests/integration/test_canonical_graph_viewer.py |
| src/threat_modeler/ui/screens/markdown_viewer.py | GUI-025 | Tests/integration/test_markdown_viewer_editor.py |
| src/threat_modeler/ui/screens/mermaid_viewer.py | GUI-020 | Tests/integration/test_mermaid_viewer_screen.py |
| src/threat_modeler/ui/screens/prompt_editor.py | SCR-010, SCR-011 | Tests/integration/test_prompt_edit_to_execution.py; Tests/unit/test_prompt_requirements_baseline.py |
| src/threat_modeler/ui/screens/results_export.py | SCR-007 | Tests/integration/test_results_export_quick_preview.py |
| src/threat_modeler/ui/screens/role_select.py | SCR-002 | Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/screens/snapshot_manager.py | SCR-008 | Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/screens/stage_results.py | SCR-003 | Tests/integration/test_results_export_quick_preview.py; Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/screens/stix_viewer.py | GUI-018 | Tests/integration/test_stix_viewer_screen.py |
| src/threat_modeler/ui/screens/stride_viewer.py | GUI-021 | Tests/integration/test_stride_viewer_screen.py; Tests/integration/test_stride_export_artifact.py |
| src/threat_modeler/ui/screens/threat_review.py | SCR-004 | Tests/integration/test_hitl_gate_set_2.py; Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/session.py | GUI-025, SCR-013 | Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/version_governance.py | GUI-024 | Tests/integration/test_version_inventory_visibility.py |
| src/threat_modeler/backend/runtime_state.py | ORCH-003, INT-007 | Tests/integration/test_agent_pipeline_completeness.py; Tests/integration/test_validation_gates.py |
| src/threat_modeler/config.py | INT-001, INT-002, SCR-014 | Tests/integration/test_validation_gates.py; Tests/unit/test_operational_api_server.py |
| src/threat_modeler/orchestrator.py | C01-ORCH-004, C01-ORCH-005, ORCH-001 | Tests/unit/test_framework_orchestrator_langgraph.py; Tests/integration/test_agent_pipeline_completeness.py |
| src/threat_modeler/server/api.py | INT-001, INT-005 | Tests/unit/test_operational_api_server.py; Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/prompt_store.py | SCR-010, SCR-011 | Tests/unit/test_backend_prompt_store.py; Tests/integration/test_prompt_edit_to_execution.py |
| src/threat_modeler/ui/screens/home.py | SCR-001, GUI-003 | Tests/e2e/test_frontend_react_mui_full_workflow.py; Tests/test_hmi_backend_api.py |
| src/threat_modeler/ui/screens/input_entry.py | GUI-001A, SCR-003, SCR-004, SCR-011, SCR-014 | Tests/unit/test_input_ingestion.py; Tests/e2e/test_frontend_react_mui_full_workflow.py |
