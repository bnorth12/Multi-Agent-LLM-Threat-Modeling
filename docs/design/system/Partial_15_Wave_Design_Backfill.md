# Partial 15 Design Backfill

## Purpose

Execute remediation waves by adding design-side anchors for reachable modules that remain partial due to missing design linkage.

## Backfill Rows

| Code Module | Requirement ID(s) | Design Anchor |
|---|---|---|
| src/threat_modeler/__main__.py | ORCH-001, INT-005 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/agents/deserialise.py | PRJ-005, INT-003 | docs/design/software/Agent_Subsystem_Design_Specification.md |
| src/threat_modeler/backend/runtime_state.py | RHMI-016, SCR-007, SCR-014 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/hitl/models.py | HITL-009, GUI-032 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/llm/llm_provider_error.py | C11-LLM-004, LLM-004 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/models/canonical.py | PRJ-005, INT-003 | docs/design/software/Agent_Subsystem_Design_Specification.md |
| src/threat_modeler/server/hmi_data.py | SCR-004, GUI-032, RHMI-016 | docs/design/system/External_Interface_And_Integration_Design_Package.md |
| src/threat_modeler/state.py | ORCH-001, INT-005, SCR-014, RHMI-016 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/app.py | SCR-002, SCR-003, SCR-004, SCR-007, SCR-008, SCR-014 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/debug.py | GUI-031, RHMI-005 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/execution.py | RHMI-016, GUI-031, GUI-032, SCR-007, SCR-014 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/prompt_store.py | SCR-010, SCR-011 | docs/design/software/Agent_Subsystem_Design_Specification.md |
| src/threat_modeler/ui/theme.py | GUI-003, GUI-031 | docs/design/software/Agent_Subsystem_Design_Specification.md |
