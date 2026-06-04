# Functional Data Flow Design Traceability Package

## Purpose

Capture system data flows as functional design artifacts and connect them to capability, function, requirement, architecture, design, implementation, verification, and test evidence.

This package is the design-side authority for data-flow behavior and transformation responsibilities.

## Scope

- End-to-end flow paths across trust boundaries
- Input normalization and source provenance behavior
- State transition and artifact publication flows
- Verification hooks and test artifact linkage

## Functional Data Flow Catalog

| Flow ID | Flow Name | Trigger | Input Sources | Transformations | Output Artifacts | Trust Boundary Crossings | Failure / Gate Conditions | Governing Capability IDs | Governing Function IDs | Governing Requirement IDs |
|---|---|---|---|---|---|---|---|---|---|---|
| DF-G0-001 | Gate 0 Input Integrity Preflight | Run start before Stage 1 | Raw text, structured tables, uploaded files | Input parsing, integrity checks, source provenance checks | Input preflight snapshot and gate decision context | User input boundary to runtime state boundary | Missing source integrity data or incomplete provenance opens Gate 0 hold | C12-HITL-001 | GUI-032, HITL-009, RIC-001, RIC-005 | GUI-032, HITL-009 |
| DF-ORCH-001 | Orchestrator Stage Transition Flow | Stage completion events | Active framework state, gate decisions | Next-stage resolution, checkpoint updates, transition validation | Updated runtime state, stage status projection, downstream prompts | Runtime control boundary between orchestrator and agent stages | Invalid transition or unresolved gate prevents stage advance | C01-ORCH-001 | F-ORCH-STATE-TRANSITIONS | C01-ORCH-001, INT-005 |
| DF-LLM-TRACE-C11_LLM_004 | Live LLM Request Budget and Timeout Flow | Live provider request invocation | Runtime config defaults, provider request payload, retry policy | Timeout enforcement, bounded retries, provider response normalization | LLM call telemetry, runtime status projection, retry outcome logs | Runtime to provider boundary | Timeout exceeded, retry budget exhausted, or provider failure triggers controlled failure path | C11-LLM-001 | F-C11_LLM_004-TRACE-L2 | C11-LLM-004, LLM-004 |
| DF-ORCH-002 | LangGraph-Compatible Routing Equivalence | Run start with `langgraph-compatible` execution mode | Approved stage set, runtime execution mode policy, checkpoint context | Graph-native next-state routing with ordered transition contracts | Stage transition event stream and updated runtime state | Orchestrator mode boundary | Mode-routing mismatch or invalid transition aborts progression | C01-ORCH-002-CAP | F-C01_ORCH_002-L2 | C01-ORCH-002, PRJ-023 |
| DF-ORCH-003 | Stage Checkpoint Persistence Continuity | Approved stage transition completion | Transition event payload, run identifier, stage checkpoint data | Checkpoint serialization, persistence, and resume-time restore | Checkpoint-backed run continuity state | Runtime state persistence boundary | Checkpoint write/read failure enters controlled recovery state | C01-ORCH-003-CAP | F-C01_ORCH_003-L2 | C01-ORCH-003, INT-007 |
| DF-UI-003A | Paused-State Projection Flow | Gate-open pause event | Run manager pause state, gate metadata, stage completion counters | API projection shaping for paused-state representation | UI-consumable paused status with gate context | Backend API to UI projection boundary | Invalid pause projection creates governance drift signal | C13-UI-003A-CAP | F-GUI_003A-TRACE-L2 | GUI-003A, GUI-031 |
| DF-UI-012A | Stage Selection Persistence Flow | Configuration save action | Stage enablement selections and validation policy | Persist selection set and enforce non-empty enabled-stage rule | Stored stage configuration and run-start eligibility state | UI configuration boundary | Empty-selection validation failure blocks execution start | C13-UI-012A-CAP | F-GUI_012A-TRACE-L2 | GUI-012A |
| DF-UI-029 | Prompt-Response Correlation Flow | Prompt history selection and response rendering | Prompt record ID, response payload set | Response filtering by prompt ID and stale-response suppression | Correlated prompt-response projection | Prompt history and response retrieval boundary | Correlation mismatch suppresses stale payload and raises diagnostics flag | C13-UI-029-CAP | F-GUI_029-TRACE-L2 | GUI-029, PRJ-018 |
| DF-PRJ-024 | Visible Browser Upload Validation Flow | Browser validation scenario start | Approved fixture ICD and markdown narrative files | UI upload execution, fixture ingestion checks, evidence capture | Validation report and run input evidence artifacts | Browser automation boundary to UI input surface | Upload mismatch or fixture rejection records validation failure | C16-PRJ-024-CAP | F-PRJ_024-TRACE-L2 | PRJ-024, VS-009 |
| DF-ADM-001 | Administration Governance Control Verification Flow | Sprint governance pre-push and pre-merge checks | Feature branch checklist template, release process policy, administration requirement baseline | Governance token checks, policy conformance verification, control result publication | Administration control verification status and remediation signal | Governance policy boundary between planning controls and execution gates | Missing required governance controls opens remediation and blocks closure readiness | C18-ADM-001 | F-ADM-GOV-CONTROLS-L2 | ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006 |

## Traceability Bridge

Use this table to bind each flow to downstream realization artifacts.

| Flow ID | Architecture Reference | Design Reference | Implementation References | Verification References | Test Artifact Metadata Reference |
|---|---|---|---|---|---|
| DF-G0-001 | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py; src/threat_modeler/hitl/service.py; frontend/src/components/HITLGateManager.tsx | Tests/integration/test_avionics_expected_results.py; Tests/test_hmi_backend_api.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-ORCH-001 | docs/architecture/Multi_Agent_Logical_Decomposition.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py; Tests/integration/test_agent_pipeline_completeness.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-LLM-TRACE-C11_LLM_004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py; src/threat_modeler/config.py | Tests/e2e/test_live_llm_validation.py; Tests/unit/test_openai_compatible_adapter.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-ORCH-002 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-ORCH-003 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/backend/run_manager.py | Tests/integration/test_agent_pipeline_completeness.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-UI-003A | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | frontend/src/components/ExecutionProgress.tsx | Tests/test_hmi_backend_api.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-UI-012A | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | frontend/src/components/PipelineConfig.tsx | Tests/test_hmi_backend_api.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-UI-029 | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | frontend/src/components/LastPromptViewer.tsx | Tests/test_hmi_backend_api.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-PRJ-024 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | scripts/live_browser_e2e_smoke_react.py | Tests/e2e/test_browser_run_validation.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-ADM-001 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | scripts/verify_administration_controls.py | Tests/unit/test_administration_controls.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |

## Source-Derived L3/L4 Data Flow Decomposition

The decomposition below adds hierarchical flow detail mapped to reachable source modules and callable operations. L3 rows define flow families; L4 rows define lower-abstraction child flows that realize each parent.

| Flow Level | Flow ID | Parent Flow ID | Flow Name | Governing Capability IDs | Governing Function IDs | Implementation Anchors | Source-Derived Operations | Output / Control Effect |
|---|---|---|---|---|---|---|---|---|
| L3 | DF-L3-CLI-ENTRYPOINT | DF-ORCH-001 | CLI Entrypoint Dispatch Flow | C16-PRJ-001 | F-L3-CLI-ENTRYPOINT-BOOTSTRAP | src/threat_modeler/__main__.py |_parse_args; main | Runtime entry mode and execution handoff established |
| L4 | DF-L4-CLI-ARGUMENT-PARSE | DF-L3-CLI-ENTRYPOINT | CLI Argument Parse and Route | C16-PRJ-001 | F-L4-CLI-ARGPARSE-DISPATCH | src/threat_modeler/__main__.py |_parse_args; main | Parsed run arguments routed to selected runtime execution path |
| L3 | DF-L3-INTERFACE-DESERIALIZATION | DF-G0-001 | Interface Deserialization Flow | C15-INT-001 | F-L3-INT-DESERIALIZATION-SERVICES | src/threat_modeler/agents/deserialise.py |_dict_to_stride; \_dict_to_mitigation; \_dict_to_threat; \_dict_to_interface | Structured interface objects prepared for canonical graph ingest |
| L4 | DF-L4-INTERFACE-GRAPH-PARSE | DF-L3-INTERFACE-DESERIALIZATION | Canonical Graph Parse Flow | C15-INT-001 | F-L4-INT-GRAPH-PARSE-COERCION | src/threat_modeler/agents/deserialise.py |_coerce_int; parse_graph_json | Graph payload coercion and canonical representation generation |
| L3 | DF-L3-PROMPT-STORE-BACKEND | DF-ORCH-001 | Backend Prompt Store Lifecycle Flow | C01-ORCH-001 | F-L3-ORCH-PROMPT-STATE-STORE | src/threat_modeler/backend/prompt_store.py |PromptStore._load_from_disk; PromptStore._save_to_disk; PromptStore.get_history | Prompt history and persisted templates maintained for execution |
| L4 | DF-L4-PROMPT-STORE-MUTATIONS | DF-L3-PROMPT-STORE-BACKEND | Prompt Store Mutation Flow | C01-ORCH-001 | F-L4-ORCH-PROMPT-MUTATION-APIS | src/threat_modeler/backend/prompt_store.py |PromptStore._validate_agent; PromptStore.set_prompt; PromptStore.reset_to_default | Validated prompt updates and defaults applied to store state |
| L3 | DF-L3-RUNTIME-STATE-PERSISTENCE | DF-ORCH-003 | Runtime State Persistence Flow | C01-ORCH-001 | F-L3-ORCH-RUNTIME-STATE-PERSISTENCE | src/threat_modeler/backend/runtime_state.py |_persist_state_locked; \_restore_state_from_disk; snapshot | Runtime settings and validation state persisted/restored |
| L4 | DF-L4-RUNTIME-STATE-SERIALIZATION | DF-L3-RUNTIME-STATE-PERSISTENCE | Runtime State Serialization Flow | C01-ORCH-001 | F-L4-ORCH-RUNTIME-STATE-SERIALIZATION | src/threat_modeler/backend/runtime_state.py |_serialize_settings; \_deserialize_settings; get_validation_state | Serialized settings and queryable state projections published |
| L3 | DF-L3-HITL-MODEL-DECISION | DF-G0-001 | HITL Decision Model Flow | C12-HITL-001 | F-L3-HITL-DECISION-MODEL-SERVICES | src/threat_modeler/hitl/models.py |HitlGateRecord.open; HitlGateRecord.apply_decision; HitlAuditLog.record | Gate review decisions and audit log state advanced |
| L4 | DF-L4-HITL-MODEL-SERIALIZATION | DF-L3-HITL-MODEL-DECISION | HITL Decision Serialization Flow | C12-HITL-001 | F-L4-HITL-DECISION-SERIALIZATION | src/threat_modeler/hitl/models.py |HitlDecision.to_dict; HitlDecision.from_dict; HitlGateRecord.from_dict | Durable serialized HITL decision payloads emitted/ingested |
| L3 | DF-L3-LLM-ERROR-CONTRACT | DF-LLM-TRACE-C11_LLM_004 | LLM Error Contract Flow | C11-LLM-001 | F-L3-LLM-EXCEPTION-CONTRACT | src/threat_modeler/llm/llm_provider_error.py |LlmProviderError.__init__ | Provider failures normalized into governed error contract |
| L4 | DF-L4-LLM-ERROR-METADATA | DF-L3-LLM-ERROR-CONTRACT | LLM Error Metadata Normalization Flow | C11-LLM-001 | F-L4-LLM-ERROR-METADATA-NORMALIZATION | src/threat_modeler/llm/llm_provider_error.py |LlmProviderError.__init__ | Deterministic status/message metadata mapped for downstream handling |
| L3 | DF-L3-CANONICAL-MODEL-PROJECTION | DF-ORCH-001 | Canonical Model Projection Flow | C15-INT-001 | F-L3-INT-CANONICAL-GRAPH-MODEL | src/threat_modeler/models/canonical.py |CanonicalThreatModelGraph.data_flows; CanonicalThreatModelGraph.to_dict | Canonical graph projection published to downstream consumers |
| L4 | DF-L4-CANONICAL-PLACEHOLDER-SEED | DF-L3-CANONICAL-MODEL-PROJECTION | Canonical Placeholder Seed Flow | C15-INT-001 | F-L4-INT-CANONICAL-PLACEHOLDER-BUILD | src/threat_modeler/models/canonical.py |build_placeholder_graph | Baseline canonical graph seeded for continuity paths |
| L3 | DF-L3-API-RUNTIME-LIFECYCLE | DF-ORCH-001 | API Runtime Lifecycle Flow | C15-INT-001 | F-L3-INT-API-RUNTIME-LIFECYCLE | src/threat_modeler/server/api.py |ThreatModelerApiHandler.do_GET; ThreatModelerApiHandler.do_POST; \_authorize_request | Authenticated API request lifecycle controls run orchestration/state |
| L4 | DF-L4-API-CATALOG-SERIALIZATION | DF-L3-API-RUNTIME-LIFECYCLE | API Catalog Serialization Flow | C15-INT-001 | F-L4-INT-API-CATALOG-SERIALIZATION | src/threat_modeler/server/api.py |_load_run_catalog; \_save_run_catalog; \_serialize_framework_state | Run catalog and checkpoint payloads serialized for transport |
| L3 | DF-L3-HMI-DATA-PROJECTION | DF-UI-003A | HMI Data Projection Flow | C15-INT-001 | F-L3-INT-HMI-DATA-PROJECTION | src/threat_modeler/server/hmi_data.py |extract_threats_from_state; extract_stages_from_messages; extract_llm_metrics | Runtime state projected into UI threat/stage/metric payloads |
| L4 | DF-L4-HMI-THREAT-GATE-SERIALIZATION | DF-L3-HMI-DATA-PROJECTION | HMI Threat and Gate Serialization Flow | C15-INT-001 | F-L4-INT-HMI-SERIALIZE-THREAT-GATE | src/threat_modeler/server/hmi_data.py |serialize_threat; serialize_gate | Threat and gate records serialized for UI tables/views |
| L3 | DF-L3-FRAMEWORK-STATE-METRICS | DF-ORCH-001 | Framework State Metrics Flow | C01-ORCH-001 | F-L3-ORCH-FRAMEWORK-STATE-METRICS | src/threat_modeler/state.py |FrameworkState.record_message; FrameworkState.record_llm_usage; FrameworkState.llm_usage_totals | Message and usage metrics ledger updated for runtime observability |
| L4 | DF-L4-FRAMEWORK-PROMPT-LEDGER | DF-L3-FRAMEWORK-STATE-METRICS | Framework Prompt Ledger Flow | C01-ORCH-001 | F-L4-ORCH-FRAMEWORK-PROMPT-LEDGER | src/threat_modeler/state.py |FrameworkState.record_llm_prompt; FrameworkState.latest_llm_prompt; FrameworkState.llm_attempt_totals | Prompt and attempt telemetry projected for diagnostics |
| L3 | DF-L3-UI-DIAGNOSTICS-SURFACE | DF-UI-003A | UI Diagnostics Surface Flow | C13-UI-001 | F-L3-UI-DIAGNOSTICS-PANEL-SERVICES | src/threat_modeler/ui/debug.py |log_exception; validate_settings; show_debug_panel | Operator diagnostics panel state and validation signals rendered |
| L4 | DF-L4-UI-DIAGNOSTIC-EXEC-WRAP | DF-L3-UI-DIAGNOSTICS-SURFACE | UI Diagnostic Execution Wrapper Flow | C13-UI-001 | F-L4-UI-DIAGNOSTIC-EXEC-WRAPPER | src/threat_modeler/ui/debug.py |log_state_change; wrap_execution | Execution callbacks wrapped with debug/state-change telemetry |
| L3 | DF-L3-UI-PROMPT-STORE-FACADE | DF-UI-029 | UI Prompt Store Facade Flow | C13-UI-001 | F-L3-UI-PROMPT-STORE-FACADE | src/threat_modeler/ui/prompt_store.py |get_prompt; set_prompt; get_history; revert_to | Prompt persistence facade data supplied to UI editor surfaces |
| L4 | DF-L4-UI-PROMPT-TEMPERATURE-CONTROL | DF-L3-UI-PROMPT-STORE-FACADE | UI Prompt Temperature Control Flow | C13-UI-001 | F-L4-UI-PROMPT-STORE-TEMPERATURE | src/threat_modeler/ui/prompt_store.py |get_temperature; set_temperature; reset_to_default; is_modified | Temperature/default mutation controls propagated to runtime config |
| L3 | DF-L3-UI-HOME-DASHBOARD | DF-UI-003A | UI Home Dashboard Flow | C13-UI-001 | F-L3-UI-HOME-DASHBOARD-PROJECTION | src/threat_modeler/ui/screens/home.py |_render_live_dashboard; \_render_run_diagnostics_panel; render | Home dashboard runtime status and diagnostics published |
| L4 | DF-L4-UI-HOME-ERROR-STATUS | DF-L3-UI-HOME-DASHBOARD | UI Home Error and Status Flow | C13-UI-001 | F-L4-UI-HOME-ERROR-STATUS-DETAIL | src/threat_modeler/ui/screens/home.py |_extract_provider_http_status; \_render_execution_error_details | Provider status and error detail views rendered for operator action |
| L3 | DF-L3-UI-INPUT-INGESTION | DF-G0-001 | UI Input Ingestion Flow | C13-UI-001 | F-L3-UI-INPUT-INGESTION-SURFACE | src/threat_modeler/ui/screens/input_entry.py |_parse_uploaded_files; \_model_connection_banner; render | Uploaded user inputs transformed into run-ready payloads |
| L4 | DF-L4-UI-UPLOAD-PARSE | DF-L3-UI-INPUT-INGESTION | UI Upload Parse Flow | C13-UI-001 | F-L4-UI-INPUT-UPLOAD-PARSER | src/threat_modeler/ui/screens/input_entry.py |_parse_uploaded_files | Uploaded files parsed and normalized for run submission |
| L3 | DF-L3-UI-PROMPT-EDITOR | DF-UI-029 | UI Prompt Editor Flow | C13-UI-001 | F-L3-UI-PROMPT-EDITOR-INTERACTION | src/threat_modeler/ui/screens/prompt_editor.py |render; \_render_editor; \_render_history | Prompt authoring/editor history views composed for operator workflows |
| L4 | DF-L4-UI-PROMPT-DIFF | DF-L3-UI-PROMPT-EDITOR | UI Prompt Diff Flow | C13-UI-001 | F-L4-UI-PROMPT-DIFF-VISUALIZATION | src/threat_modeler/ui/screens/prompt_editor.py |_render_diff | Prompt revision deltas visualized for governed prompt change review |
| L3 | DF-L3-UI-STAGE-RESULTS | DF-UI-003A | UI Stage Results Projection Flow | C13-UI-001 | F-L3-UI-STAGE-RESULTS-PROJECTION | src/threat_modeler/ui/screens/stage_results.py |_stage_rows; \_message_rows; render | Stage and message result projections rendered for runtime timeline |
| L4 | DF-L4-UI-STAGE-MESSAGE-NORMALIZATION | DF-L3-UI-STAGE-RESULTS | UI Stage Message Normalization Flow | C13-UI-001 | F-L4-UI-STAGE-MESSAGE-NORMALIZATION | src/threat_modeler/ui/screens/stage_results.py |_message_rows | Stage message rows normalized for deterministic UI presentation |
| L3 | DF-L3-UI-SESSION-BOOTSTRAP | DF-UI-003A | UI Session Bootstrap Flow | C13-UI-001 | F-L3-UI-SESSION-BOOTSTRAP | src/threat_modeler/ui/session.py |init_session_state | Session defaults initialized for consistent UI control state |
| L4 | DF-L4-UI-SESSION-DEFAULTS | DF-L3-UI-SESSION-BOOTSTRAP | UI Session Default Initialization Flow | C13-UI-001 | F-L4-UI-SESSION-DEFAULT-INITIALIZATION | src/threat_modeler/ui/session.py |init_session_state | Session default key/value controls materialized for runtime use |
| L3 | DF-L3-UI-THEME-APPLICATION | DF-UI-003A | UI Theme Application Flow | C13-UI-001 | F-L3-UI-THEME-APPLICATION-SERVICES | src/threat_modeler/ui/theme.py |apply_theme | Theme configuration applied across UI component surfaces |
| L4 | DF-L4-UI-THEME-TOKEN-MAPPING | DF-L3-UI-THEME-APPLICATION | UI Theme Token Mapping Flow | C13-UI-001 | F-L4-UI-THEME-TOKEN-MAPPING | src/threat_modeler/ui/theme.py |apply_theme | Theme tokens mapped into concrete widget styles |
| L3 | DF-L3-CANONICAL-VALIDATION | DF-G0-001 | Canonical Validation Flow | C15-INT-001 | F-L3-INT-CANONICAL-VALIDATION-SERVICES | src/threat_modeler/validation.py |CanonicalGraphValidator.validate; ValidationResult.has_critical | Canonical payload validity and halt status asserted |
| L4 | DF-L4-CANONICAL-SCHEMA-RANGE-CHECK | DF-L3-CANONICAL-VALIDATION | Canonical Schema and Range Check Flow | C15-INT-001 | F-L4-INT-VALIDATION-SCHEMA-RANGE-CHECK | src/threat_modeler/validation.py |CanonicalGraphValidator._load_schema; CanonicalGraphValidator._is_int_in_range | Schema/range checks emitted for critical validation decisions |

## Review Rule

Each active remediation slice must confirm that every governing flow row has non-empty links in all bridge columns before closeout.

## Sprint 2026-013 Coverage Anchors

- PRJ-005 is allocated through orchestration and data-flow paths in this package and its bridge rows.
- PRJ-026 is allocated through approved handoff and runtime state continuity data-flow paths in this package and its bridge rows.

### Closed Slice Evidence

- R01-003 (`C11-LLM-004`) now has a dedicated flow row and bridge entry to enforce end-to-end design traceability coverage.

## Reachable Module Design Backfill

These implementation modules are reachable in the running application and already carry requirement anchors. The rows below connect them back to the existing design families and show the verification artifacts that already exercise the same behavior.

| Code Module | Requirement ID(s) | Design / Flow Family | Verification Artifact Anchors | Notes |
|---|---|---|---|---|
| src/threat_modeler/ui/connection_validator.py | SCR-013, SCR-014 | UI control and runtime validation flow family | Tests/integration/test_validation_gates.py; Tests/test_hmi_backend_api.py | Validation and connection-governance boundary |
| src/threat_modeler/ui/runtime_io.py | SCR-007 | UI control and runtime validation flow family | Tests/test_hmi_backend_api.py; Tests/e2e/test_frontend_react_mui_full_workflow.py | Runtime I/O bridge into governed UI execution |
| src/threat_modeler/ui/screens/canonical_graph_viewer.py | GUI-019 | Artifact/viewer flow family | Tests/integration/test_canonical_graph_viewer.py | Canonical graph visualization and inspection |
| src/threat_modeler/ui/screens/config.py | SCR-003, SCR-012, SCR-013, SCR-014 | UI control and runtime validation flow family | Tests/test_hmi_backend_api.py; Tests/e2e/test_frontend_react_mui_full_workflow.py | Pipeline configuration and stage-selection behavior |
| src/threat_modeler/ui/screens/last_prompt.py | SCR-015 | UI control and runtime validation flow family | Tests/test_hmi_backend_api.py | Prompt diagnostics and last-response selection |
| src/threat_modeler/ui/screens/markdown_viewer.py | GUI-025 | Artifact/viewer flow family | Tests/integration/test_markdown_viewer_editor.py | Markdown artifact viewing |
| src/threat_modeler/ui/screens/mermaid_viewer.py | GUI-020 | Artifact/viewer flow family | Tests/integration/test_mermaid_viewer_screen.py | Mermaid diagram viewing |
| src/threat_modeler/ui/screens/results_export.py | SCR-007 | Artifact publication flow family | Tests/integration/test_results_export_quick_preview.py | Artifact export and preview |
| src/threat_modeler/ui/screens/role_select.py | SCR-002 | UI control and runtime validation flow family | Tests/test_hmi_backend_api.py; Tests/e2e/test_frontend_react_mui_full_workflow.py | Role selection and operator entry surface |
| src/threat_modeler/ui/screens/snapshot_manager.py | SCR-008 | UI control and runtime validation flow family | Tests/test_hmi_backend_api.py | Snapshot save and restore |
| src/threat_modeler/ui/screens/stix_viewer.py | GUI-018 | Artifact/viewer flow family | Tests/integration/test_stix_viewer_screen.py | STIX bundle inspection |
| src/threat_modeler/ui/screens/stride_viewer.py | GUI-021 | Artifact/viewer flow family | Tests/integration/test_stride_viewer_screen.py; Tests/integration/test_stride_export_artifact.py | STRIDE analysis and export coupling |
| src/threat_modeler/ui/screens/threat_review.py | SCR-004 | HITL review flow family | Tests/integration/test_hitl_gate_set_2.py; Tests/test_hmi_backend_api.py | Threat and mitigation review with governed decisions |
| src/threat_modeler/ui/screens/token_usage.py | SCR-014 | Runtime telemetry and governance flow family | Tests/unit/test_token_usage_runtime.py; Tests/integration/test_validation_gates.py | Token usage telemetry and gate-context reporting |
| src/threat_modeler/ui/version_governance.py | GUI-024 | Artifact/viewer flow family | Tests/integration/test_version_inventory_visibility.py | Version and governance presentation |

### Additional Reachable Module Outside Architecture / Design Trace (Beyond the 13)

| Code Module | Status |
|---|---|
| src/threat_modeler/ui/session.py | Reachable from runtime entrypoints and now anchored via source-derived L3/L4 function and data-flow decomposition entries |
