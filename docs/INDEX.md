# Docs Index

## User Documentation

- [user_manual/index.html](user_manual/index.html) (**End-user manual — primary** — fully styled HTML with sidebar navigation, per-screen GUI descriptions, screenshot placeholders, HITL gate guide, and glossary; open in any browser)
- [User_Manual.md](User_Manual.md) (Markdown source for the user manual — superseded by the HTML version above; retained for diff history and plain-text access)
- [screenshots/README.md](screenshots/README.md) (Screenshot evidence index — SCR-xxx to GUI requirement ID mapping for sprint AC evidence)
- [user_manual/screenshots/](user_manual/screenshots/) (Working directory for user manual GUI screenshots — place captured PNGs here matching filenames referenced in index.html figures)

## Architecture

- [architecture/framework_overview.md](architecture/framework_overview.md)
- [architecture/architecture_diagram.mermaid](architecture/architecture_diagram.mermaid)

## Design Specifications

- [HMI_Architecture_Blueprint.md](HMI_Architecture_Blueprint.md) (**Design authority** for all analyst-facing GUI screens; covers GUI-001 through GUI-014, navigation model, shared components, role gating, and state management)
- [Model_Configuration_Design_Specification.md](Model_Configuration_Design_Specification.md) (Model provider selection and connection configuration for GUI — see also HMI blueprint §9.4)

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

## Data Model Note

Mitigations are defined at the threat object level in the canonical schema.
