# Docs Index

## Architecture

- [architecture/framework_overview.md](architecture/framework_overview.md)
- [architecture/architecture_diagram.mermaid](architecture/architecture_diagram.mermaid)

## Schemas

- [schemas/canonical_graph.schema.json](schemas/canonical_graph.schema.json) (authoritative)
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
