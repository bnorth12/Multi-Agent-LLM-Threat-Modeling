# Threat Modeler Code Directory

This directory is the Python implementation root for runtime code.

## Implemented Modules

`src/threat_modeler/`

| Module | Status | Purpose |
|---|---|---|
| `orchestrator.py` | Implemented | Pipeline orchestration with HITL and validation-halting behavior |
| `validation.py` | Implemented | Canonical graph validation and halt signaling |
| `config.py` | Implemented | Runtime/provider/pipeline configuration models |
| `agents/` | Implemented | Agent 01-09 stage implementations plus shared base/deserialization support |
| `exports/` | Implemented | STIX, Mermaid, JSON, and markdown report exporters |
| `ui/` | Implemented | Streamlit-based analyst GUI and screen orchestration |
| `backend/` | Implemented | Run manager, prompt store, and execution backend services |
| `parsing/` | Implemented | Structured input parsing and normalization helpers |
| `models/` | Implemented | Canonical datamodel definitions and related types |

## Scope Note

This README describes the modules included in the v1.0.0 release-candidate
code snapshot. It does not track future planning backlog items.
