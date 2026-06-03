# Traceability Blocker Backlog (Latest)

- Timestamp: 2026-06-01T19:11:21
- Sprint: 2026_013
- Source verifier exit code: 0

## Missing Requirement Documentation IDs

- none

## Issues Missing Explicit Test Evidence

- none

## Missing Function Root Links (Issue:Function)

- none

## Missing Requirements/15 Registry Links (Issue:Requirement)

- none

## Likely Abstraction-Level Mismatches

- none

## Suggested Remediation Order

1. Resolve missing requirement-documentation IDs in a dedicated requirements commit.
1. Validate each requirement at the same abstraction level it is written (system/project, capability/function, interface, component, or UI); rewrite or split requirement text when verification cannot be stated at that same level.
1. Create missing function hierarchy entries in docs/architecture/Function_Hierarchy_Registry.md grouped by parent capability.
1. Add or update Requirements/15 registry rows for missing issue/requirement links with architecture/design/implementation/verification references.
1. Add explicit test evidence references for remaining issue files in a separate evidence commit.
1. Re-run sprint traceability validation and capture post-remediation output.

## Raw Verification Output (Tail)

-
- [95m=== Sprint 2026-013 Traceability Verification ===[0m
-
- [96m[INFO] Indexed 224 requirement IDs from Requirements/[0m
- [96m[INFO] Loaded 4 sprint issue file(s)[0m
- [96m[INFO] Using matrix source: planning\Sprint_2026_013_Traceability_Matrix.md[0m
- [96m[INFO] Matrix contributes 10 sprint-scoped requirement ID(s)[0m
-
- [1m--- Issue -> Requirement Traceability ---[0m
-
- [92m[PASS] S13-001 links to: INT-005, ORCH-001[0m
- [92m[PASS] S13-002 links to: ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006[0m
- [92m[PASS] S13-003 links to: ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006[0m
- [92m[PASS] S13-004 links to: PRJ-005, PRJ-026[0m
-
- [1m--- Requirement Documentation ---[0m
-
- [92m[PASS] ADM-001 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-002 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-003 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-004 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-005 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-006 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] INT-005 documented in: Requirements\02_Interface_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ORCH-001 documented in: Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] PRJ-005 documented in: Requirements\01_Project_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] PRJ-026 documented in: Requirements\01_Project_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
-
- [1m--- Test Evidence Linkage ---[0m
-
- [92m[PASS] S13-001 has test evidence: Tests/unit/test_framework_orchestrator_langgraph.py[0m
- [92m[PASS] S13-002 has test evidence: Tests/unit/test_administration_controls.py[0m
- [92m[PASS] S13-003 has test evidence: Tests/unit/test_administration_controls.py[0m
- [92m[PASS] S13-004 has test evidence: Tests/integration/test_agent_pipeline_completeness.py[0m
-
- [1m--- Hierarchy Field Coverage ---[0m
-
- [92m[PASS] S13-001 includes required hierarchy fields[0m
- [92m[PASS] S13-002 includes required hierarchy fields[0m
- [92m[PASS] S13-003 includes required hierarchy fields[0m
- [92m[PASS] S13-004 includes required hierarchy fields[0m
-
- [1m--- Root Hierarchy Linkage ---[0m
-
- [93m[WARN] Requirement INT-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-002 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-003 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-006 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-002 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-003 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-006 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement PRJ-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement PRJ-026 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [96m[INFO] Parsed 4 issue status entrie(s) from sprint tracker[0m
-
- [1m--- Summary ---[0m
-
- [93m15 warning(s)[0m
- - Requirement INT-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-002 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-003 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-006 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-002 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-003 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement ADM-006 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement PRJ-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- - Requirement PRJ-026 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
- [92m[PASS] All requested traceability checks passed[0m
