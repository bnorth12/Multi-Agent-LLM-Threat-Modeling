# Threat Modeler Code Directory

This directory is the Python implementation root for runtime code.

## Implemented Modules

`src/threat_modeler/`

| Module | Status | Purpose |
|---|---|---|
| `orchestrator.py` | Implemented | LangGraph-compatible stage execution, validation halt behavior |
| `validation.py` | Implemented | `CanonicalGraphValidator`, `ValidationResult`, `ValidationHaltError` |
| `config.py` | Implemented | `RuntimeSettings`, `ModelSelection`, `PipelineSettings` |
| `models/canonical.py` | Implemented | Typed dataclasses: System, Subsystem, Component, Function, Interface, threat graph |
| `models/__init__.py` | Implemented | Export module for canonical model types |
| `parsing/icd_parser.py` | Implemented | CSV and XLSX ICD parsing with entity_type dispatch; narrative document parser |
| `agents/__init__.py` | Scaffolded | `MockAgent` dataclass and `build_default_agents()` for orchestrator wiring |

## Planned Modules

- `agents/agent_01_input_normalizer.py` through `agent_09_human_report_writer.py` — full agent implementations
- `export/stix_exporter.py` — STIX 2.1 bundle output
- `export/diagram_generator.py` — Mermaid diagram generation
- `export/report_writer.py` — Markdown report generation
- `hmi/` — Streamlit-based analyst GUI (post-sprint; see docs/HMI_Architecture_Blueprint.md)
