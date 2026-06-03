# Traceability Blocker Backlog (Latest)

- Timestamp: 2026-06-03T05:34:33
- Sprint: 2026_013
- Source verifier exit code: 0

## Missing Requirement Documentation IDs
- none

## Issues Missing Explicit Test Evidence
- none

## Missing Function Root Links (Issue:Function)
- none

## Missing Requirements/15 Registry Links (Issue:Requirement)
- S13-002:ADM-002
- S13-002:ADM-003
- S13-002:ADM-005
- S13-002:ADM-006
- S13-003:ADM-002
- S13-003:ADM-003
- S13-003:ADM-005
- S13-003:ADM-006
- S13-004:PRJ-026

## Likely Abstraction-Level Mismatches
- none

## Suggested Remediation Order
1. Resolve missing requirement-documentation IDs in a dedicated requirements commit.
2. Validate each requirement at the same abstraction level it is written (system/project, capability/function, interface, component, or UI); rewrite or split requirement text when verification cannot be stated at that same level.
3. Create missing function hierarchy entries in docs/architecture/Function_Hierarchy_Registry.md grouped by parent capability.
4. Add or update Requirements/15 registry rows for missing issue/requirement links with architecture/design/implementation/verification references.
5. Add explicit test evidence references for remaining issue files in a separate evidence commit.
6. Re-run sprint traceability validation and capture post-remediation output.

## Raw Verification Output (Tail)
- [92m[PASS] ADM-001 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-002 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md[0m
- [92m[PASS] ADM-003 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md[0m
- [92m[PASS] ADM-004 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md[0m
- [92m[PASS] ADM-005 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md[0m
- [92m[PASS] ADM-006 documented in: Requirements\04_Traceability_Matrix.md, Requirements\06_Project_Administration_Requirements.md[0m
- [92m[PASS] GUI-018 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] GUI-019 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] GUI-020 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] GUI-021 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] GUI-024 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] GUI-025 documented in: Requirements\04_Traceability_Matrix.md, Requirements\10_GUI_Requirements.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] INT-005 documented in: Requirements\02_Interface_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md, Requirements\Partial_15_Wave_Requirements_Backfill.md[0m
- [92m[PASS] ORCH-001 documented in: Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md, Requirements\Partial_15_Wave_Requirements_Backfill.md[0m
- [92m[PASS] PRJ-005 documented in: Requirements\01_Project_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\15_End_To_End_Traceability_Attributes_Registry.md, Requirements\Partial_15_Wave_Requirements_Backfill.md[0m
- [92m[PASS] PRJ-026 documented in: Requirements\01_Project_Requirements.md, Requirements\04_Traceability_Matrix.md[0m
- [92m[PASS] SCR-002 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-003 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-004 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-007 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-008 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-012 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-013 documented in: Requirements\02_Interface_Requirements.md, Requirements\04_Traceability_Matrix.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-014 documented in: Requirements\04_Traceability_Matrix.md, Requirements\Partial_15_Wave_Requirements_Backfill.md, Requirements\Reachable_Module_Requirements_Backfill.md[0m
- [92m[PASS] SCR-015 documented in: Requirements\Reachable_Module_Requirements_Backfill.md[0m
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
- [93m[WARN] Requirement ORCH-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Issue S13-002 requirement ADM-002 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Issue S13-002 requirement ADM-003 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Issue S13-002 requirement ADM-005 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Issue S13-002 requirement ADM-006 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Issue S13-003 requirement ADM-002 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Issue S13-003 requirement ADM-003 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Issue S13-003 requirement ADM-005 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Issue S13-003 requirement ADM-006 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [93m[WARN] Requirement PRJ-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)[0m
- [93m[WARN] Issue S13-004 requirement PRJ-026 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage[0m
- [96m[INFO] Parsed 4 issue status entrie(s) from sprint tracker[0m
- 
- [1m--- Summary ---[0m
- 
- [93m16 warning(s)[0m
-   - Requirement INT-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Requirement ORCH-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Issue S13-002 requirement ADM-002 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Issue S13-002 requirement ADM-003 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Issue S13-002 requirement ADM-005 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Issue S13-002 requirement ADM-006 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Requirement ADM-001 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Issue S13-003 requirement ADM-002 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Issue S13-003 requirement ADM-003 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Requirement ADM-004 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Issue S13-003 requirement ADM-005 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Issue S13-003 requirement ADM-006 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
-   - Requirement PRJ-005 row exists in registry but is missing root hierarchy references (Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md)
-   - Issue S13-004 requirement PRJ-026 has no aligned row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md for parent capability/function linkage
- [92m[PASS] All requested traceability checks passed[0m