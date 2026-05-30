# Sprint 2026_01 Remediation Restart Manifest

Date: 2026-05-30
Status: Scope preserved for restart
Purpose: Preserve the selected 42-item remediation scope while abandoning previously generated remediation planning and issue artifacts from the prior branch.

## Restart Rules

- Canonical sprint token for files, scripts, and automation: `2026_01`
- Optional human-readable label in prose only: `2026-Remediation-01`
- Do not reuse prior generated issue files, trackers, or remediation design packages from the abandoned branch.
- Restart from `main` plus governance salvage only.
- Regenerate sprint planning artifacts only after naming, intake, and validation rules are confirmed.

## Scope Summary

- Total items: 42
- Phase 1 items: 30
- Phase 2 items: 12
- Decomposition target: L0 -> L1 -> L2
- This manifest is the only carried-forward remediation artifact on this branch.

## Preserved 42-Item Scope

| ID | Phase | Requirement ID | Parent Capability ID | Parent Function ID | Child Function ID |
|---|---|---|---|---|---|
| R01-001 | Phase 1 | C01-ORCH-002 | C01-ORCH-001 | F-ORCH-TRACEABILITY-L1 | F-C01_ORCH_002-TRACE-L2 |
| R01-002 | Phase 1 | C01-ORCH-003 | C01-ORCH-001 | F-ORCH-TRACEABILITY-L1 | F-C01_ORCH_003-TRACE-L2 |
| R01-003 | Phase 1 | C11-LLM-004 | C11-LLM-001 | F-LLM-TRACEABILITY-L1 | F-C11_LLM_004-TRACE-L2 |
| R01-004 | Phase 1 | GUI-003A | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_003A-TRACE-L2 |
| R01-005 | Phase 1 | GUI-012A | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_012A-TRACE-L2 |
| R01-006 | Phase 1 | GUI-029 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_029-TRACE-L2 |
| R01-007 | Phase 1 | HITL-012 | C12-HITL-001 | F-HITL-TRACEABILITY-L1 | F-HITL_012-TRACE-L2 |
| R01-008 | Phase 1 | PRJ-024 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_024-TRACE-L2 |
| R01-009 | Phase 1 | VS-009 | C14-VER-001 | F-VER-TRACEABILITY-L1 | F-VS_009-TRACE-L2 |
| R01-010 | Phase 1 | PRJ-023 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_023-TRACE-L2 |
| R01-011 | Phase 1 | GUI-015 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_015-TRACE-L2 |
| R01-012 | Phase 1 | INT-005 | C15-INT-001 | F-INT-TRACEABILITY-L1 | F-INT_005-TRACE-L2 |
| R01-013 | Phase 1 | PRJ-011 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_011-TRACE-L2 |
| R01-014 | Phase 1 | PRJ-030 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_030-TRACE-L2 |
| R01-015 | Phase 1 | GUI-006 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_006-TRACE-L2 |
| R01-016 | Phase 1 | GUI-003 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_003-TRACE-L2 |
| R01-017 | Phase 1 | GUI-005 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_005-TRACE-L2 |
| R01-018 | Phase 1 | GUI-026 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_026-TRACE-L2 |
| R01-019 | Phase 1 | INT-002 | C15-INT-001 | F-INT-TRACEABILITY-L1 | F-INT_002-TRACE-L2 |
| R01-020 | Phase 1 | GUI-033 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_033-TRACE-L2 |
| R01-021 | Phase 1 | PRJ-029 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_029-TRACE-L2 |
| R01-022 | Phase 1 | GUI-007 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_007-TRACE-L2 |
| R01-023 | Phase 1 | GUI-009 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_009-TRACE-L2 |
| R01-024 | Phase 1 | PRJ-016 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_016-TRACE-L2 |
| R01-025 | Phase 1 | INT-009 | C15-INT-001 | F-INT-TRACEABILITY-L1 | F-INT_009-TRACE-L2 |
| R01-026 | Phase 1 | PRJ-001 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_001-TRACE-L2 |
| R01-027 | Phase 1 | PRJ-015 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_015-TRACE-L2 |
| R01-028 | Phase 1 | GUI-002 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_002-TRACE-L2 |
| R01-029 | Phase 1 | GUI-012 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_012-TRACE-L2 |
| R01-030 | Phase 1 | GUI-013 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_013-TRACE-L2 |
| R01-031 | Phase 2 | GUI-032 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_032-TRACE-L2 |
| R01-032 | Phase 2 | PRJ-003 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_003-TRACE-L2 |
| R01-033 | Phase 2 | PRJ-018 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_018-TRACE-L2 |
| R01-034 | Phase 2 | GUI-014 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_014-TRACE-L2 |
| R01-035 | Phase 2 | GUI-003C | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_003C-TRACE-L2 |
| R01-036 | Phase 2 | SCR-014 | C17-SCR-001 | F-SCR-TRACEABILITY-L1 | F-SCR_014-TRACE-L2 |
| R01-037 | Phase 2 | INT-001 | C15-INT-001 | F-INT-TRACEABILITY-L1 | F-INT_001-TRACE-L2 |
| R01-038 | Phase 2 | PRJ-002 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_002-TRACE-L2 |
| R01-039 | Phase 2 | PRJ-028 | C16-PRJ-001 | F-PRJ-TRACEABILITY-L1 | F-PRJ_028-TRACE-L2 |
| R01-040 | Phase 2 | C01-ORCH-001 | C01-ORCH-001 | F-ORCH-TRACEABILITY-L1 | F-C01_ORCH_001-TRACE-L2 |
| R01-041 | Phase 2 | GUI-008 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_008-TRACE-L2 |
| R01-042 | Phase 2 | GUI-010 | C13-UI-001 | F-UI-TRACEABILITY-L1 | F-GUI_010-TRACE-L2 |

## Immediate Next Steps For Restart

1. Confirm canonical naming and tracker generation rules before creating any sprint files.
1. Re-run sprint intake and hierarchy validation against this manifest before generating issue artifacts.
1. Generate one tracker format only, using `2026_01` for automation-facing names.
1. Add implementation, architecture, and verification evidence incrementally instead of pre-generating the full remediation package.
