# Docs Index

## Architecture

- [framework_overview.md](framework_overview.md)
- [architecture_diagram.mermaid](architecture_diagram.mermaid)

## Schemas

- [canonical_graph.schema.json](canonical_graph.schema.json) (authoritative)
- [canonical_json_schema.txt](canonical_json_schema.txt) (example payload)
- [langgraph_state_schema.txt](langgraph_state_schema.txt)

## Agent Prompts

- [agent_01_input_normalizer.txt](agent_01_input_normalizer.txt)
- [agent_02_hierarchical_context_builder.txt](agent_02_hierarchical_context_builder.txt)
- [agent_03_trust_boundary_validator.txt](agent_03_trust_boundary_validator.txt)
- [agent_04_stride_scorer.txt](agent_04_stride_scorer.txt)
- [agent_05_concrete_threat_generator.txt](agent_05_concrete_threat_generator.txt)
- [agent_06_stix_packager.txt](agent_06_stix_packager.txt)
- [agent_07_mitigation_generator.txt](agent_07_mitigation_generator.txt)
- [agent_08_diagram_generator.txt](agent_08_diagram_generator.txt)
- [agent_09_human_report_writer.txt](agent_09_human_report_writer.txt)

## Retrieval and Supporting References

- [Vector DB Design.txt](Vector%20DB%20Design.txt)
- [Few-Shot for Agent 5.txt](Few-Shot%20for%20Agent%205.txt)
- [project_instructions.txt](project_instructions.txt)

## Planning and Requirements Cross-References

- [../Implemenation Plan/Sectioned_Implementation_Plan.md](../Implemenation%20Plan/Sectioned_Implementation_Plan.md)
- [../Implemenation Plan/Requirements_Baseline_v0.1.md](../Implemenation%20Plan/Requirements_Baseline_v0.1.md)
- [../Requirements/README.md](../Requirements/README.md)
- [../Requirements/03_HITL_Requirements.md](../Requirements/03_HITL_Requirements.md)
- [../Requirements/09_HITL_Framework_Options.md](../Requirements/09_HITL_Framework_Options.md)

## Data Model Note

Mitigations are defined at the threat object level in the canonical schema.
