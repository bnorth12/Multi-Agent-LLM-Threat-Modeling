# Partial 15 Requirements Backfill

## Purpose

Execute remediation waves by adding requirement-side anchors for reachable modules that remain partial due to missing requirement linkage.

## Backfill Rows

| Code Module | Requirement ID(s) | Requirement Anchor |
|---|---|---|
| src/threat_modeler/__main__.py | ORCH-001, INT-005 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/agents/deserialise.py | PRJ-005, INT-003 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/backend/runtime_state.py | RHMI-016, SCR-007, SCR-014 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/hitl/models.py | HITL-009, GUI-032 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/llm/llm_provider_error.py | C11-LLM-004, LLM-004 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/models/canonical.py | PRJ-005, INT-003 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/server/hmi_data.py | SCR-004, GUI-032, RHMI-016 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/state.py | ORCH-001, INT-005, SCR-014, RHMI-016 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/app.py | SCR-002, SCR-003, SCR-004, SCR-007, SCR-008, SCR-014 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/debug.py | GUI-031, RHMI-005 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/execution.py | RHMI-016, GUI-031, GUI-032, SCR-007, SCR-014 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/prompt_store.py | SCR-010, SCR-011 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/theme.py | GUI-003, GUI-031 | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/validation.py | SCR-014, GUI-032 | Requirements/04_Traceability_Matrix.md |
