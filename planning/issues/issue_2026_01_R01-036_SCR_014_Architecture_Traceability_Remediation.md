# R01-036 / SCR-014 Architecture-Design Traceability Remediation

Sprint: 2026-Remediation-01
Remediation Phase: Phase 2
Requirement ID: SCR-014
Parent Capability ID: C17-SCR-001
Parent Function ID: F-SCR-TRACEABILITY-L1
Child Function ID: F-SCR_014-TRACE-L2
Decomposition Level: L2
Allocated Component/Module: Tests/unit/test_token_usage_runtime.py
Verification Method: Artifact-based verification evidence
Data-Flow ID: DF-SCR-TRACE-SCR_014
Status: Planned -> In Progress

## Purpose

Close architecture/design/capability/function trace gaps while preserving existing implementation behavior unless assumption checks fail.

## Related Requirements

- SCR-014

## Source References (from latest independent review)

- Requirements/04_Traceability_Matrix.md

## Existing Implementation Evidence

- Tests/unit/test_token_usage_runtime.py
- src/threat_modeler/ui/screens/token_usage.py

## Existing Verification Evidence

- Tests/
- test_token_usage_runtime.py

## Hierarchy Chain

- L0 Capability: CAP-L0-THREAT-MODELER
- L1 Parent Capability: C17-SCR-001
- L1 Parent Function: F-SCR-TRACEABILITY-L1
- L2 Child Function: F-SCR_014-TRACE-L2

## Remediation Targets

- docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md
- docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md
- Requirements/15_End_To_End_Traceability_Attributes_Registry.md

## Exit Criteria

- Requirement has complete structural trace legs in next independent review pass.
- Hierarchy fields are present and consistent across tracker, issue file, architecture matrix, design package, and registry.
- Allocation and verification method remain linked to implementation and verification evidence.
