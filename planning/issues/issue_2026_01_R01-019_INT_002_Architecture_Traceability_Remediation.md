# R01-019 / INT-002 Architecture-Design Traceability Remediation

Sprint: 2026-Remediation-01
Remediation Phase: Phase 1
Requirement ID: INT-002
Parent Capability ID: C15-INT-001
Parent Function ID: F-INT-TRACEABILITY-L1
Child Function ID: F-INT_002-TRACE-L2
Decomposition Level: L2
Allocated Component/Module: Tests/unit/test_input_ingestion.py
Verification Method: Artifact-based verification evidence
Data-Flow ID: DF-INT-TRACE-INT_002
Status: Planned -> In Progress

## Purpose

Close architecture/design/capability/function trace gaps while preserving existing implementation behavior unless assumption checks fail.

## Related Requirements

- INT-002

## Source References (from latest independent review)

- Requirements/02_Interface_Requirements.md
- Requirements/04_Traceability_Matrix.md
- Requirements/15_End_To_End_Traceability_Attributes_Registry.md

## Existing Implementation Evidence

- Tests/unit/test_input_ingestion.py
- frontend/src/components/
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/orchestrator.py
- src/threat_modeler/server/api.py

## Existing Verification Evidence

- Tests/
- test_input_ingestion.py

## Hierarchy Chain

- L0 Capability: CAP-L0-THREAT-MODELER
- L1 Parent Capability: C15-INT-001
- L1 Parent Function: F-INT-TRACEABILITY-L1
- L2 Child Function: F-INT_002-TRACE-L2

## Remediation Targets

- docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md
- docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md
- Requirements/15_End_To_End_Traceability_Attributes_Registry.md

## Exit Criteria

- Requirement has complete structural trace legs in next independent review pass.
- Hierarchy fields are present and consistent across tracker, issue file, architecture matrix, design package, and registry.
- Allocation and verification method remain linked to implementation and verification evidence.
