# Docs Index

## User Documentation

- [user_manual/index.html](user_manual/index.html) (**End-user manual — primary** — fully styled HTML with sidebar navigation, per-screen GUI descriptions, HITL gate guide, and glossary; open in any browser)
- [User_Manual.md](User_Manual.md) (Markdown source for the user manual — superseded by the HTML version above; retained for diff history and plain-text access)
- [screenshots/README.md](screenshots/README.md) (Historical screenshot evidence index — preserved sprint-era captures and mapping)
- [user_manual/screenshots/](user_manual/screenshots/) (Current user-manual screenshot source set; place release-facing PNGs here matching filenames referenced in index.html figures)

## Architecture

- [architecture/framework_overview.md](architecture/framework_overview.md)
- [architecture/architecture_diagram.mermaid](architecture/architecture_diagram.mermaid)
- [architecture/Multi_Agent_Architecture_Decomposition_Package.md](architecture/Multi_Agent_Architecture_Decomposition_Package.md)
- [architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md](architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md)
- [architecture/Capability_Hierarchy_Baseline.md](architecture/Capability_Hierarchy_Baseline.md)
- [architecture/Function_Hierarchy_Registry.md](architecture/Function_Hierarchy_Registry.md)
- [architecture/Multi_Agent_Functional_Decomposition.md](architecture/Multi_Agent_Functional_Decomposition.md)
- [architecture/Multi_Agent_Structural_Decomposition.md](architecture/Multi_Agent_Structural_Decomposition.md)
- [architecture/Multi_Agent_Logical_Decomposition.md](architecture/Multi_Agent_Logical_Decomposition.md)
- [architecture/Multi_Agent_Interface_Control_Document.md](architecture/Multi_Agent_Interface_Control_Document.md)
- [architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md](architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md)
- [architecture/HMI_Architecture_Blueprint.md](architecture/HMI_Architecture_Blueprint.md) (architecture authority for analyst-facing GUI structure, navigation, role gating, and shared interaction patterns)

## Backend Module Reference

- `src/threat_modeler/backend/run_manager.py` — Streamlit-free pipeline execution engine.
  JSON state file: `~/.multi_agent_threat_modeler_runs.json`.
- `src/threat_modeler/backend/prompt_store.py` — Thread-safe agent prompt store.
  JSON state file: `~/.multi_agent_threat_modeler_prompts.json`.
- `src/threat_modeler/server/api.py` — Operational non-Streamlit HTTP server.
- `src/threat_modeler/__main__.py` — CLI entry point (`python -m threat_modeler`) for the operational API server.
- `src/threat_modeler/ui/app.py` — Streamlit test harness used for browser automation/e2e validation.

## Design Specifications

- [design/README.md](design/README.md) (design-document index and architecture-to-design traceability rules)
- [design/system/External_Interface_And_Integration_Design_Package.md](design/system/External_Interface_And_Integration_Design_Package.md) (system design package for user, system, provider, and artifact interfaces plus integration boundaries)
- [design/system/System_Deployment_And_Operating_Modes_Design.md](design/system/System_Deployment_And_Operating_Modes_Design.md) (system design for deployment topology, operating modes, and release packaging boundaries)
- [design/software/Agent_Subsystem_Design_Specification.md](design/software/Agent_Subsystem_Design_Specification.md) (software design for agent roles, stage responsibilities, prompt/configuration inputs, and canonical-graph mutation constraints)
- [design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md](design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md) (software design for canonical-graph state transitions, validation gates, fallback rules, and authoritative mutation control)
- [design/software/Export_And_Evidence_Packaging_Design_Specification.md](design/software/Export_And_Evidence_Packaging_Design_Specification.md) (software design for export assembly, evidence capture, release-ready packaging, and provenance preservation)
- [design/software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md](design/software/Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md) (software design for persisted run state, prompt version storage, checkpoint continuity, and recovery boundaries)
- [design/software/Runtime_And_Orchestration_Design_Specification.md](design/software/Runtime_And_Orchestration_Design_Specification.md) (software design for runtime state authority, orchestration control, HITL pause/resume, and evidence flow)
- [design/software/Model_Configuration_Design_Specification.md](design/software/Model_Configuration_Design_Specification.md) (software design for model provider selection and connection validation; governed by the HMI architecture blueprint for screen behavior)

## Schemas

- [schemas/canonical_graph.schema.json](schemas/canonical_graph.schema.json) (authoritative)
- [schemas/hitl_trigger_rules.schema.json](schemas/hitl_trigger_rules.schema.json) (HITL trigger thresholds)
- [schemas/canonical_json_schema.txt](schemas/canonical_json_schema.txt) (example payload)
- [schemas/langgraph_state_schema.txt](schemas/langgraph_state_schema.txt)

## Agent Prompts

- [agents/agent_01_input_normalizer.txt](agents/agent_01_input_normalizer.txt)
- [agents/agent_02_hierarchical_context_builder.txt](agents/agent_02_hierarchical_context_builder.txt)
- [agents/agent_03_trust_boundary_validator.txt](agents/agent_03_trust_boundary_validator.txt)
- [agents/agent_04_stride_scorer.txt](agents/agent_04_stride_scorer.txt)
- [agents/agent_05_concrete_threat_generator.txt](agents/agent_05_concrete_threat_generator.txt)
- [agents/agent_06_stix_packager.txt](agents/agent_06_stix_packager.txt)
- [agents/agent_07_mitigation_generator.txt](agents/agent_07_mitigation_generator.txt)
- [agents/agent_08_diagram_generator.txt](agents/agent_08_diagram_generator.txt)
- [agents/agent_09_human_report_writer.txt](agents/agent_09_human_report_writer.txt)

## Retrieval and Supporting References

- [references/Vector DB Design.txt](references/Vector%20DB%20Design.txt)
- [references/Few-Shot for Agent 5.txt](references/Few-Shot%20for%20Agent%205.txt)
- [process/project_instructions.txt](process/project_instructions.txt)

## Planning and Requirements Cross-References

- [../planning/Sectioned_Implementation_Plan.md](../planning/Sectioned_Implementation_Plan.md)
- [../planning/Requirements_Baseline_v0.1.md](../planning/Requirements_Baseline_v0.1.md)
- [../Requirements/README.md](../Requirements/README.md)
- [../Requirements/03_HITL_Requirements.md](../Requirements/03_HITL_Requirements.md)
- [../Requirements/09_HITL_Framework_Options.md](../Requirements/09_HITL_Framework_Options.md)
- [../Requirements/13_Runtime_State_And_Input_Contract_Requirements.md](../Requirements/13_Runtime_State_And_Input_Contract_Requirements.md)
- [../planning/issues/issue_2026_99_D_S13_022_Run_State_And_Gate_Contract_Corrections.md](../planning/issues/issue_2026_99_D_S13_022_Run_State_And_Gate_Contract_Corrections.md)
- [process/Runtime_State_And_Gate_Contract_Resolution_2026_05.md](process/Runtime_State_And_Gate_Contract_Resolution_2026_05.md)

## Data Model Note

Mitigations are defined at the threat object level in the canonical schema.
