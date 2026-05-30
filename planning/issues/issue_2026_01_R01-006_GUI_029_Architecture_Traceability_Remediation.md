# R01-006 / GUI-029 Architecture-Design Traceability Remediation

Sprint: 2026-Remediation-01
Remediation Phase: Phase 1
Requirement ID: GUI-029
Parent Capability ID: C13-UI-001
Parent Function ID: F-UI-TRACEABILITY-L1
Child Function ID: F-GUI_029-TRACE-L2
Decomposition Level: L2
Allocated Component/Module: Tests/unit/test_last_prompt_runtime.py
Verification Method: Artifact-based verification evidence
Data-Flow ID: DF-UI-TRACE-GUI_029
Status: Planned -> In Progress

## Purpose

Close architecture/design/capability/function trace gaps while preserving existing implementation behavior unless assumption checks fail.

## Related Requirements

- GUI-029

## Source References (from latest independent review)

- Requirements/10_GUI_Requirements.md
- Requirements/15_End_To_End_Traceability_Attributes_Registry.md

## Existing Implementation Evidence

- Tests/unit/test_last_prompt_runtime.py
- src/threat_modeler/ui/screens/last_prompt.py

## Existing Verification Evidence

- Tests/
- test_last_prompt_runtime.py

## Hierarchy Chain

- L0 Capability: CAP-L0-THREAT-MODELER
- L1 Parent Capability: C13-UI-001
- L1 Parent Function: F-UI-TRACEABILITY-L1
- L2 Child Function: F-GUI_029-TRACE-L2

## Remediation Targets

- docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md
- docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md
- Requirements/15_End_To_End_Traceability_Attributes_Registry.md

## Exit Criteria

- Requirement has complete structural trace legs in next independent review pass.
- Hierarchy fields are present and consistent across tracker, issue file, architecture matrix, design package, and registry.
- Allocation and verification method remain linked to implementation and verification evidence.
