# Threat Modeler Code Directory

This directory is the Python implementation root for runtime code.

## Implemented Modules

`src/threat_modeler/`

| Module | Status | Purpose |
|---|---|---|
| `orchestrator.py` | Implemented | LangGraph-native `StateGraph` stage execution, HITL/validation halt behavior |
| `validation.py` | Implemented | `CanonicalGraphValidator`, `ValidationResult`, `ValidationHaltError` |
| `config.py` | Implemented | `RuntimeSettings`, `ModelSelection`, `PipelineSettings` |
| `agents/` | Implemented | Agent 01-09 stage implementations plus shared base/deserialization support |
| `exports/` | Implemented | STIX, Mermaid, JSON, and markdown report exporters |
| `ui/` | Implemented | Streamlit-based analyst GUI and screen orchestration |
| `backend/` | Implemented | Run manager, prompt store, and execution backend services |
| `parsing/` | Implemented | Structured input parsing and normalization helpers |
| `models/` | Implemented | Canonical datamodel definitions and related types |

## Scope Note

This README tracks the current runtime implementation state for `src/`.
Status labels must remain consistent with release-candidate code-snapshot inventories.
