# Threat Modeler Code Directory

This directory is the Python implementation root for runtime code.

Current package scaffold:

- `threat_modeler/`
- `threat_modeler/agents/`
- `threat_modeler/models/`
- `threat_modeler/parsing/`
- `threat_modeler/hitl/`
- `threat_modeler/exports/`

Initial framework modules now include:

- runtime configuration and pipeline settings
- framework state container
- linear orchestrator scaffold for known stages
- placeholder validation seam
- stub agent classes for Agent 1 through Agent 9
- parsing, HITL, and export placeholders

Implementation rule:

- represent current architectural knowledge explicitly
- defer incomplete behavior with targeted `TODO` markers rather than hiding future work
