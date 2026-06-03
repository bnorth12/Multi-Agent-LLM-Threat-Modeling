# Reachable Module Design Backfill

## Purpose

Establish design-side module-path trace relationships for reachable implementation modules with known requirement IDs and missing design linkage.

## Backfill Rows

| Code Module | Requirement ID(s) | Design Anchor |
|---|---|---|
| src/threat_modeler/ui/screens/home.py | SCR-001 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/screens/input_entry.py | GUI-001A, SCR-003, SCR-004, SCR-011, SCR-014 | docs/design/software/Agent_Subsystem_Design_Specification.md |
| src/threat_modeler/ui/screens/prompt_editor.py | SCR-010, SCR-011 | docs/design/software/Agent_Subsystem_Design_Specification.md |
| src/threat_modeler/ui/screens/stage_results.py | SCR-003 | docs/design/software/Runtime_And_Orchestration_Design_Specification.md |
| src/threat_modeler/ui/screens/token_usage.py | SCR-014 | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md |
