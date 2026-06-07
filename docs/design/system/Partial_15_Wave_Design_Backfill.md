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

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- Partial_15_Wave_Design_Backfill satisfies design-anchor closure for modules that had requirement IDs and source implementation but incomplete design linkage (ORCH-001, INT-005, PRJ-005, INT-003, RHMI-016, SCR-007/014, C11-LLM-004/LLM-004, HITL-009, GUI-032, SCR-004, SCR-002/003/007/008, SCR-010/011, GUI-003/031, etc.)
- Directly supports architecture-design surface coverage gates (PRJ-005, PRJ-026) and promotion from historical appendix into 15_End_To_End core registry

### Realizes

- The backfill rows realize the missing design legs for the listed modules, linking them to Runtime_And_Orchestration_Design_Specification.md, Agent_Subsystem_Design_Specification.md, and External_Interface_And_Integration_Design_Package.md
- Enables full realization of the cited capabilities (C01-ORCH, C11-LLM, C12-HITL, C13-UI, C15-INT, C16-PRJ, C17-SCR) and their functions for the modules that were previously only partially traced

### Provides / Requires

- Provides: concrete table of Code Module → Requirement ID(s) → Design Anchor that can be used to populate Implemented By / Satisfies entries in the target design specs' annexes
- Requires: the named design anchors to maintain corresponding traceability annex content; the 15_End_To_End registry to promote the now-closed rows

### Implemented By

- All modules enumerated in the Backfill Rows table (src/threat_modeler/__main__.py, agents/deserialise.py, backend/runtime_state.py, hitl/models.py, llm/llm_provider_error.py, models/canonical.py, server/hmi_data.py, state.py, ui/app.py, ui/debug.py, ui/execution.py, ui/prompt_store.py, ui/theme.py)
- Design anchors as listed per row (primarily the two software design specs + one system package)
- Verification per row is provided by the Tests/ entries in the original remediation context (now cross-referenced via 15_End_To_End and the design specs)

### Depends On

- The target design specifications (Runtime_And_Orchestration, Agent_Subsystem, External_Interface...)
- Capability_Hierarchy_Baseline.md, Function_Hierarchy_Registry.md, and Capability_Function_Architecture_Traceability_Matrix.md for the capability/function mapping of the requirement IDs
- 15_End_To_End_Traceability_Attributes_Registry.md (historical appendix rows being closed by this backfill)
- scripts/verify_architecture_design_surface_coverage.py and sprint traceability verification
- Executable tests listed against each module in the broader registry and FQT plan
