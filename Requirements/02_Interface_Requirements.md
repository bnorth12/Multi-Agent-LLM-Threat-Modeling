# Interface Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|INT-001|Parser Request Contract|Parser Interface SHALL accept normalized text payloads and table payloads in structured request format.|Standardized ingress reduces parser ambiguity.|Test|Verified by API contract tests with valid and invalid payload shapes.|
|INT-002|Agent Input Contract|Agent Input Interface SHALL receive canonical graph payload, run metadata, and stage context for each invocation.|Consistent stage input enables reusable agent adapters.|Test|Verified by schema tests at each agent entry point.|
|INT-003|Agent Output Contract|Agent Output Interface SHALL return canonical graph payload and stage result status in a schema-valid structure.|Uniform outputs simplify orchestration and validation.|Test|Verified by contract tests for success and failure returns.|
|INT-004|Validation Result Contract|Validation Interface SHALL return pass or fail result with machine-readable error codes and locations.|Structured errors enable deterministic remediation paths.|Test|Verified by negative tests asserting specific codes and field paths.|
|INT-005|Stage Event Contract|Orchestrator Interface SHALL expose stage transition events with stage name, timestamp, and correlation identifier.|Event traceability is required for audit and debugging.|Inspection|Verified by log/event review across a full run.|
|INT-006|HITL Decision Contract|HITL Decision Interface SHALL accept analyst decision objects containing action, rationale, actor, and role.|Formal decision payloads support governance.|Test|Verified by interface tests accepting required fields and rejecting incomplete decisions.|
|INT-007|Re-Run Contract|Re-Run Interface SHALL accept stage restart requests and resume execution from selected stage with preserved run context.|Controlled reruns reduce rework and support analyst iteration.|Demonstration|Verified by triggering staged rerun and confirming context continuity.|
|INT-008|Visualization Read Contract|Visualization Interface SHALL provide read access to graph nodes, flows, boundaries, threats, mitigations, and evidence references.|Analysts need complete contextual visibility for decisions.|Demonstration|Verified by UI/API walkthrough showing retrieval of all listed artifact domains.|
|INT-009|Visualization Edit Contract|Visualization Edit Interface SHALL submit proposed changes as typed patch operations rather than direct artifact overwrite.|Patch-based edits preserve auditability and conflict handling.|Test|Verified by edit operation tests confirming patch validation and no direct overwrite path.|
|INT-010|STIX Export Contract|STIX Export Interface SHALL output a standards-conformant STIX 2.1 bundle artifact with validation result metadata.|Export must be both interoperable and verifiable.|Test|Verified by STIX validator pass and metadata presence check.|
|INT-011|Report Export Contract|Report Export Interface SHALL output markdown report artifact and structured section index.|Structured indexing supports downstream publishing automation.|Test|Verified by export test asserting report file and section index schema.|
|INT-012|Provider Config Contract|Provider Configuration Interface SHALL accept provider name, model name, mode, and policy profile settings.|Runtime flexibility depends on explicit provider configuration.|Test|Verified by configuration parsing tests and runtime selection checks.|
|INT-013|Authorization Contract|Security Interface SHALL enforce role-based authorization checks before any edit, approve, or release action.|Security governance requires strict pre-action authorization.|Test|Verified by role matrix tests for allowed and denied operations.|
|INT-014|Audit Retrieval Contract|Audit Retrieval Interface SHALL return immutable change history for a selected run and artifact.|Immutable retrieval is required for compliance evidence.|Inspection|Verified by audit record review showing non-mutable chronological history.|
|INT-015|Model Connection Contract|Model Connection Interface SHALL accept provider name, endpoint URL, API key, authentication method, model name, and deployment-specific parameters, and SHALL return a connection validation result indicating success, connectivity error, or authentication failure.|Structured model configuration enables dynamic provider switching and integration with diverse LLM instances without code changes.|Test|Verified by connection tests with valid and invalid endpoints, confirming successful connection, clear error messages, model availability checks, and SCR-013 API-key input handling for providers that require authentication.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- INT-00x family primarily derived from C15-INT-001 (Integration and Interface Integrity) and supporting C01-ORCH / C13-UI / C16-PRJ capabilities in Capability_Hierarchy_Baseline.md
- INT-001/002/003/005/006/007/010/011/015 derived from or allocated under the interface and handoff portions of CAP-L0-THREAT-MODELER and M1/M2/M4/M5 mission functions
- INT-012/013/014/015 also support C11-LLM-001 (provider config), C17-SCR (authorization/audit), and C18-ADM (governance audit retrieval)

### Allocated To

- INT-001/002/003/004/005 allocated to C15-INT-001 / F-INT-TRACEABILITY-L1 and L3/L4 canonical validation + stage event services (Function_Hierarchy_Registry.md)
- INT-005/006/007 allocated to C01-ORCH-001 and C12-HITL-001 (stage events, HITL decision, re-run contracts) realized in Runtime_And_Orchestration_Design_Specification.md + orchestrator + hitl/service.py
- INT-008/009 allocated to C13-UI-001 visualization surfaces (visualization read/edit contracts)
- INT-010/011 allocated to C07/C08/C09/C10 packaging agents and Export_And_Evidence_Packaging_Design_Specification.md
- INT-012/015 allocated to C11-LLM-001 and Model_Configuration_Design_Specification.md + openai_compatible_adapter + config + PipelineConfig
- INT-013/014 allocated to C17-SCR-001 and administration/security controls (C18-ADM)
- Most INT-* allocated to External_Interface_And_Integration_Design_Package.md and Multi_Agent_Interface_Control_Document.md for boundary definitions

### Refines

- Component-level interface details in C01_Orchestrator_State_Requirements.md, C02_Agent_01_..., C11_LLM_Requirements.md, C12_HITL_*, etc. refine the project interface contracts
- Sprint remediation slices (S12/S13) add concrete handoff, projection, and connection behaviors that refine the base INT-* statements

### Satisfied By

- INT-001/002/003/004 satisfied by src/threat_modeler/parsing/*, agents (input normalizer, context builder, trust boundary, etc.), validation.py (CanonicalGraphValidator), and Agent_Subsystem_Design_Specification.md + Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md
- INT-005/006/007 satisfied by src/threat_modeler/orchestrator.py (FrameworkOrchestrator, stage events, handoff), backend/run_manager.py, hitl/service.py (HitlService, decision recording, resume), and Runtime_And_Orchestration_Design_Specification.md
- INT-008/009 satisfied by frontend visualization components (stix_viewer, stride_viewer, mermaid_viewer, artifacts/threat review viewers) + backend data services (server/hmi_data.py, ui/screens/*)
- INT-010/011 satisfied by agent_06_stix_packager.py, agent_08_diagram_generator.py, agent_09_human_report_writer.py + Export_And_Evidence_Packaging_Design_Specification.md + test export paths
- INT-012/015 satisfied by Model_Configuration_Design_Specification.md, src/threat_modeler/config.py, llm/openai_compatible_adapter.py, frontend/src/components/PipelineConfig.tsx, server/api.py (model connection verification)
- INT-013/014 satisfied by authorization and audit paths in runtime + governance (C17-SCR / C18-ADM controls)
- 15_End_To_End rows (R01-003, S12-033, S12-034, S13-005*, many INT-005/010/011/015 legs) list the exact design + source + verification for each

### Verified By

- Contract/schema tests in Tests/unit and integration (test_input_ingestion.py, test_validation_gates.py, test_agent_pipeline_completeness.py, test_results_export_quick_preview.py, test_stride_export_artifact.py, test_stix_viewer_screen.py, etc.)
- Live provider/connection tests (Tests/e2e/test_live_llm_validation.py, Tests/test_hmi_backend_api.py)
- UI/API walkthroughs and FQT cases that exercise the full set of INT contracts (FQT-002 provider, FQT-003 input, FQT-007/008 results/export, FQT-010 documentation review)
- Governance verifiers and 15_End_To_End Test Artifact IDs / Verification Artifacts

### Depends On

- Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md for C15-INT-001 and related allocations
- 01_Project_Requirements.md (many PRJ-* depend on or elaborate the INT contracts)
- Agent_Subsystem, Canonical_Graph_Lifecycle, Runtime_And_Orchestration, Export_And_Evidence, Model_Configuration, External_Interface_And_Integration_Design_Package.md, and Multi_Agent_Interface_Control_Document.md for realization
- 15_End_To_End_Traceability_Attributes_Registry.md (the durable record of INT legs)
- Verification Strategy (05_) for contract vs. demonstration vs. inspection methods
- C11_LLM_Requirements.md, C12_HITL_*, GUI requirements, and Components/ for detailed elaboration
- 18_Traceability_Governance_Operating_Model.md for the relationship taxonomy itself (this document is a primary example of the "Interface provision and consumption" and "Requirement allocation" rules)

Many INT-* are further refined by component-level contracts in the Cxx_ files (e.g., C01-ORCH-005 for handoff, C02-A01-00x for input normalization, C11-LLM-004 for timeout budgets) and by sprint-specific UI/integration slices (S12-0xx, S13-005x). These refinements are tracked in the 15_End_To_End_Traceability_Attributes_Registry.md rows and the corresponding design annexes (External_Interface_And_Integration_Design_Package.md, Agent_Subsystem_Design_Specification.md, etc.) rather than duplicated at this level.
