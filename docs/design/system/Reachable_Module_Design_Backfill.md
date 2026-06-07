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

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Reachable_Module_Design_Backfill satisfies design-side module-path trace closure for reachable implementation modules that had known requirement IDs but missing design anchors (SCR-001, GUI-001A, SCR-003/004/011/014, SCR-010, SCR-014)
- Contributes to full source-to-design surface coverage for C13-UI-001, C16-PRJ-001, and related governance slices (supports PRJ-005/026 architecture-design alignment)

### Realizes

- The listed UI screen modules are now anchored to Runtime_And_Orchestration_Design_Specification.md, Agent_Subsystem_Design_Specification.md, and Functional_Data_Flow_Design_Traceability_Package.md, realizing the corresponding UI and delivery functions (home dashboard, input entry, prompt editor, stage results, token usage/telemetry)
- Enables complete realization of the cited requirement IDs within C13-UI and C16-PRJ capabilities and their L2/L3 function allocations

### Provides / Requires

- Provides: explicit backfill rows (Code Module | Requirement ID(s) | Design Anchor) that close reachable-module gaps and can be consumed by the target design specs' Implemented By sections and by 15_End_To_End promotion
- Requires: the referenced design specs to reflect these modules in their Traceability Annexes; verification tests to remain executable

### Implemented By

- The five UI screen modules listed: src/threat_modeler/ui/screens/home.py, input_entry.py, prompt_editor.py, stage_results.py, token_usage.py
- Design anchors as listed (Runtime_And_Orchestration for home/stage_results; Agent_Subsystem for input/prompt; Functional_Data_Flow for token_usage)
- Cross-referenced in S13-005 remediation rows and Reachable_Module context for UI shell and telemetry behaviors

### Depends On

- Runtime_And_Orchestration_Design_Specification.md, Agent_Subsystem_Design_Specification.md, and Functional_Data_Flow_Design_Traceability_Package.md
- Capability and function hierarchies for the SCR/GUI requirement-to-capability mapping
- 15_End_To_End_Traceability_Attributes_Registry.md (S13-005* rows and related)
- UI shell and integration tests (Tests/unit/test_ui_app_shell.py, Tests/test_hmi_backend_api.py, Tests/integration/test_results_export_quick_preview.py, etc.)
- Architecture-design surface coverage and sprint traceability verifiers
