# Sprint 2026_102 Issue Tracker

Date: 2026-05-31
Status: Open
Sprint Goal: Close needed unimplemented requirements and triage deletion candidates.

## Active Issues

| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |
|---|---|---|---|---|---|---|---|

## Closure Policy

A sprint issue may be closed only when implementation, verification, and traceability evidence are all present.

<!-- AUTO-UNIMPLEMENTED-TRIAGE:START -->
## Automated Intake Candidates (Needed + Unimplemented)

| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |
|---|---|---|---|---|---|---|---|
| BL-099-005 | #104 | Remediation / Implementation | P0 | GitHub Created | Agent 2: merge new submissions into existing canonical graphs without deleting existing approved e... | C03-A02-001 | planning/issues/issue_2026_102_BL_099_005_C03_A02_001.md |
| BL-099-006 | #105 | Remediation / Implementation | P0 | GitHub Created | Agent 2: record merge-conflict notes for analyst review when contradictory source claims are detected | C03-A02-002 | planning/issues/issue_2026_102_BL_099_006_C03_A02_002.md |
| BL-099-007 | #106 | Remediation / Implementation | P0 | GitHub Created | Agent 2: preserve the input-compliance and provenance metadata produced by Agent 1 and SHALL emit... | C03-A02-003 | planning/issues/issue_2026_102_BL_099_007_C03_A02_003.md |
| BL-099-008 | #107 | Remediation / Implementation | P0 | GitHub Created | Agent 3: evaluate each data flow for trust-boundary crossing status using configured policy rules | C04-A03-001 | planning/issues/issue_2026_102_BL_099_008_C04_A03_001.md |
| BL-099-009 | #108 | Remediation / Implementation | P0 | GitHub Created | Agent 3: emit trust-boundary review flags for human approval when confidence is below policy thres... | C04-A03-002 | planning/issues/issue_2026_102_BL_099_009_C04_A03_002.md |
| BL-099-010 | #109 | Remediation / Implementation | P0 | GitHub Created | Agent 4: assign STRIDE severity scores for each data flow using the configured scoring scale | C05-A04-001 | planning/issues/issue_2026_102_BL_099_010_C05_A04_001.md |
| BL-099-011 | #110 | Remediation / Implementation | P0 | GitHub Created | Agent 4: provide concise justification text for each STRIDE dimension score | C05-A04-002 | planning/issues/issue_2026_102_BL_099_011_C05_A04_002.md |
| BL-099-012 | #111 | Remediation / Implementation | P0 | GitHub Created | Agent 4: preserve analyst-overridden scores and associated rationale metadata | C05-A04-003 | planning/issues/issue_2026_102_BL_099_012_C05_A04_003.md |
| BL-099-013 | #112 | Remediation / Implementation | P0 | GitHub Created | Agent 5: generate concrete threats for flows meeting configured risk trigger criteria | C06-A05-001 | planning/issues/issue_2026_102_BL_099_013_C06_A05_001.md |
| BL-099-014 | #113 | Remediation / Implementation | P0 | GitHub Created | Agent 5: attach threat taxonomy references where available, including ATTACK, CAPEC, and CWE ident... | C06-A05-002 | planning/issues/issue_2026_102_BL_099_014_C06_A05_002.md |
| BL-099-015 | #114 | Remediation / Implementation | P0 | GitHub Created | Agent 5: emit likelihood and impact values for each generated threat | C06-A05-003 | planning/issues/issue_2026_102_BL_099_015_C06_A05_003.md |
| BL-099-016 | #115 | Remediation / Implementation | P0 | GitHub Created | Agent 6: transform approved threat artifacts into a valid STIX 2.1 bundle | C07-A06-001 | planning/issues/issue_2026_102_BL_099_016_C07_A06_001.md |
| BL-099-017 | #116 | Remediation / Implementation | P0 | GitHub Created | Agent 6: include stable object identifiers and relationship links for generated STIX entities | C07-A06-002 | planning/issues/issue_2026_102_BL_099_017_C07_A06_002.md |
| BL-099-018 | #117 | Remediation / Implementation | P0 | GitHub Created | Agent 7: map each approved threat to technical and administrative controls based on configured con... | C08-A07-001 | planning/issues/issue_2026_102_BL_099_018_C08_A07_001.md |
| BL-099-019 | #118 | Remediation / Implementation | P0 | GitHub Created | Agent 7: assign residual-risk estimates after proposed controls | C08-A07-002 | planning/issues/issue_2026_102_BL_099_019_C08_A07_002.md |
| BL-099-020 | #119 | Remediation / Implementation | P0 | GitHub Created | Agent 7: include rationale linking control selections to threat mechanics | C08-A07-003 | planning/issues/issue_2026_102_BL_099_020_C08_A07_003.md |
| BL-099-021 | #120 | Remediation / Implementation | P0 | GitHub Created | Agent 7: store mitigations_technical and mitigations_administrative arrays under each threat objec... | C08-A07-004 | planning/issues/issue_2026_102_BL_099_021_C08_A07_004.md |
| BL-099-022 | #121 | Remediation / Implementation | P0 | GitHub Created | Agent 8: generate Level 0, Level 1, and selected Level 2 Mermaid diagrams from canonical graph data | C09-A08-001 | planning/issues/issue_2026_102_BL_099_022_C09_A08_001.md |
| BL-099-023 | #122 | Remediation / Implementation | P0 | GitHub Created | Agent 8: render trust boundaries and risk severity overlays using configured visual conventions | C09-A08-002 | planning/issues/issue_2026_102_BL_099_023_C09_A08_002.md |
| BL-099-024 | #123 | Remediation / Implementation | P0 | GitHub Created | Agent 8: preserve deterministic node and edge identifiers across regenerations for unchanged struc... | C09-A08-003 | planning/issues/issue_2026_102_BL_099_024_C09_A08_003.md |
| BL-099-025 | #124 | Remediation / Implementation | P0 | GitHub Created | Model Adapter: support policy-constrained model allowlists by deployment mode | C11-LLM-002 | planning/issues/issue_2026_102_BL_099_025_C11_LLM_002.md |
| BL-099-026 | #125 | Remediation / Implementation | P0 | GitHub Created | Model Adapter: support future provider additions without agent contract changes | C11-LLM-003 | planning/issues/issue_2026_102_BL_099_026_C11_LLM_003.md |
| BL-099-027 | #126 | Remediation / Implementation | P0 | GitHub Created | The system: enforce role-based permissions for all HITL actions | C12-HITL-002 | planning/issues/issue_2026_102_BL_099_027_C12_HITL_002.md |
| BL-099-028 | #127 | Remediation / Implementation | P0 | GitHub Created | The system: record a complete audit trail for all HITL actions, including rationale and before/after... | C12-HITL-003 | planning/issues/issue_2026_102_BL_099_028_C12_HITL_003.md |
| BL-099-029 | #128 | Remediation / Implementation | P0 | GitHub Created | The system: require rationale for all analyst overrides at gates | C12-HITL-004 | planning/issues/issue_2026_102_BL_099_029_C12_HITL_004.md |
| BL-099-030 | #129 | Remediation / Implementation | P0 | GitHub Created | The system: evaluate configured trigger rules for conditional Merge Conflict Resolution and Export Co... | C12-HITL-005 | planning/issues/issue_2026_102_BL_099_030_C12_HITL_005.md |
| BL-099-031 | #130 | Remediation / Implementation | P0 | GitHub Created | Audit Service: capture analyst decision records for Gate 0 input integrity review before context merge | C12-HITL-006 | planning/issues/issue_2026_102_BL_099_031_C12_HITL_006.md |
| BL-099-032 | #131 | Remediation / Implementation | P0 | GitHub Created | The GUI: render gate-review artifacts in human-readable summaries in addition to raw structured pa... | GUI-002A | planning/issues/issue_2026_102_BL_099_032_GUI_002A.md |
| BL-099-033 | #132 | Remediation / Implementation | P0 | GitHub Created | The GUI: keep the primary navigation rail visible at all times on the main HMI shell and SHALL NOT... | GUI-035 | planning/issues/issue_2026_102_BL_099_033_GUI_035.md |
| BL-099-034 | #133 | Remediation / Implementation | P0 | GitHub Created | The GUI: render a top-of-content control strip that mirrors the primary operator workflow sections... | GUI-036 | planning/issues/issue_2026_102_BL_099_034_GUI_036.md |
| BL-099-035 | #134 | Remediation / Implementation | P0 | GitHub Created | Conditional gate state in the run record: have one of three explicit values: (1) "Open" when condition is triggered a... | HITL-013 | planning/issues/issue_2026_102_BL_099_035_HITL_013.md |
| BL-099-036 | #135 | Remediation / Implementation | P0 | GitHub Created | The Run Dashboard HITL Gate States table: display conditional gates with status "🟢 Auto-Bypassed" (distinct emoji) wh... | HITL-014 | planning/issues/issue_2026_102_BL_099_036_HITL_014.md |
| BL-099-037 | #136 | Remediation / Implementation | P0 | GitHub Created | Conditional gate record in the run result: include trigger_condition_met (boolean) and trigger_reason (string) fields... | HITL-015 | planning/issues/issue_2026_102_BL_099_037_HITL_015.md |
| BL-099-038 | #137 | Remediation / Implementation | P0 | GitHub Created | Threat Modeler: provide an operational web/API runtime that does not require Streamlit, and SHALL reserve... | PRJ-025 | planning/issues/issue_2026_102_BL_099_038_PRJ_025.md |
| BL-099-039 | #138 | Remediation / Implementation | P0 | GitHub Created | Consistent authoring model improves maintainability and review quality. | PRM-S01 | planning/issues/issue_2026_102_BL_099_039_PRM_S01.md |
| BL-099-040 | #139 | Remediation / Implementation | P0 | GitHub Created | Reduces prompt bloat and lowers change-coupling between behavior and... | PRM-S02 | planning/issues/issue_2026_102_BL_099_040_PRM_S02.md |
| BL-099-041 | #140 | Remediation / Implementation | P0 | GitHub Created | Improves resilience under partial or low-confidence model outputs. | PRM-S03 | planning/issues/issue_2026_102_BL_099_041_PRM_S03.md |
| BL-099-042 | #141 | Remediation / Implementation | P0 | GitHub Created | Supports safe evolution and audit traceability. | PRM-S04 | planning/issues/issue_2026_102_BL_099_042_PRM_S04.md |
| BL-099-043 | #142 | Remediation / Implementation | P0 | GitHub Created | POST /runs, POST /config | RHMI-001 | planning/issues/issue_2026_102_BL_099_043_RHMI_001.md |
| BL-099-044 | #143 | Remediation / Implementation | P0 | GitHub Created | POST /config/verify | RHMI-002 | planning/issues/issue_2026_102_BL_099_044_RHMI_002.md |
| BL-099-045 | #144 | Remediation / Implementation | P0 | GitHub Created | POST /runs, POST /runs/{run_id} | RHMI-003 | planning/issues/issue_2026_102_BL_099_045_RHMI_003.md |
| BL-099-046 | #145 | Remediation / Implementation | P0 | GitHub Created | GET /prompts, GET/POST /prompts/{agent_id} | RHMI-004 | planning/issues/issue_2026_102_BL_099_046_RHMI_004.md |
| BL-099-047 | #146 | Remediation / Implementation | P0 | GitHub Created | POST /runs/{run_id}/metadata | RHMI-006 | planning/issues/issue_2026_102_BL_099_047_RHMI_006.md |
| BL-099-048 | #147 | Remediation / Implementation | P0 | GitHub Created | DELETE /runs/{run_id}/purge | RHMI-007 | planning/issues/issue_2026_102_BL_099_048_RHMI_007.md |
| BL-099-049 | #148 | Remediation / Implementation | P0 | GitHub Created | POST /runs/purge, DELETE /runs/{run_id}/purge | RHMI-008 | planning/issues/issue_2026_102_BL_099_049_RHMI_008.md |
| BL-099-050 | #149 | Remediation / Implementation | P0 | GitHub Created | API integration test + UI functional test | RHMI-009 | planning/issues/issue_2026_102_BL_099_050_RHMI_009.md |
| BL-099-051 | #150 | Remediation / Implementation | P0 | GitHub Created | N/A (shell layout requirement) | RHMI-011 | planning/issues/issue_2026_102_BL_099_051_RHMI_011.md |
| BL-099-052 | #151 | Remediation / Implementation | P0 | GitHub Created | GET /runs/{run_id}/artifacts/canonical | RHMI-012 | planning/issues/issue_2026_102_BL_099_052_RHMI_012.md |
| BL-099-053 | #152 | Remediation / Implementation | P0 | GitHub Created | N/A (shell layout requirement) | RHMI-013 | planning/issues/issue_2026_102_BL_099_053_RHMI_013.md |
| BL-099-054 | #153 | Remediation / Implementation | P0 | GitHub Created | N/A (shell layout requirement) | RHMI-014 | planning/issues/issue_2026_102_BL_099_054_RHMI_014.md |
| BL-099-055 | #154 | Remediation / Implementation | P0 | GitHub Created | Component behavior validation + API integration test | RHMI-018 | planning/issues/issue_2026_102_BL_099_055_RHMI_018.md |
| BL-099-056 | #155 | Remediation / Implementation | P0 | GitHub Created | Contract validation test + release checklist inspection | RHMI-019 | planning/issues/issue_2026_102_BL_099_056_RHMI_019.md |
| BL-099-057 | #156 | Remediation / Implementation | P0 | GitHub Created | Frontend submission preprocessing: preserve parse parity with backend expectations by placing parsed table data into... | RIC-003 | planning/issues/issue_2026_102_BL_099_057_RIC_003.md |
| BL-099-058 | #157 | Remediation / Implementation | P0 | GitHub Created | Prompt expected-output declarations: remain aligned with enforced JSON/schema contracts; mismatch conditions SHALL be... | RIC-004 | planning/issues/issue_2026_102_BL_099_058_RIC_004.md |
| BL-099-059 | #158 | Remediation / Implementation | P0 | GitHub Created | Requirement Owner: assign at least one verification method to each requirement ID | VS-001 | planning/issues/issue_2026_102_BL_099_059_VS_001.md |
| BL-099-060 | #159 | Remediation / Implementation | P0 | GitHub Created | Requirement Owner: define objective pass criteria for each requirement ID | VS-002 | planning/issues/issue_2026_102_BL_099_060_VS_002.md |
| BL-099-061 | #160 | Remediation / Implementation | P0 | GitHub Created | Test Team: map automated tests to requirement IDs for all schema, orchestration, and interface contr... | VS-003 | planning/issues/issue_2026_102_BL_099_061_VS_003.md |
| BL-099-062 | #161 | Remediation / Implementation | P0 | GitHub Created | Review Team: perform inspection-based verification for HITL workflow and audit controls | VS-004 | planning/issues/issue_2026_102_BL_099_062_VS_004.md |
| BL-099-063 | #162 | Remediation / Implementation | P0 | GitHub Created | Integration Team: perform end-to-end demonstration of a complete run with approvals and exports | VS-005 | planning/issues/issue_2026_102_BL_099_063_VS_005.md |
| BL-099-064 | #163 | Remediation / Implementation | P0 | GitHub Created | Sprint Team: record demonstration evidence (annotated screenshots or screen recording) for every sprin... | VS-006 | planning/issues/issue_2026_102_BL_099_064_VS_006.md |
| BL-099-065 | #164 | Remediation / Implementation | P0 | GitHub Created | Sprint demonstration: cover, at minimum, the user-facing deliverables of that sprint: pipeline execution for pi... | VS-007 | planning/issues/issue_2026_102_BL_099_065_VS_007.md |
| BL-099-066 | #165 | Remediation / Implementation | P0 | GitHub Created | For release-candidate sprints that intentionally exclude automation from release gating, Sprint Team: execute and doc... | VS-008 | planning/issues/issue_2026_102_BL_099_066_VS_008.md |
| BL-099-067 | #166 | Remediation / Implementation | P0 | GitHub Created | For runtime state transitions and HITL gate publication paths, Sprint Team: execute a race-condition verification con... | VS-010 | planning/issues/issue_2026_102_BL_099_067_VS_010.md |

## Automated Deletion Candidates

See independent_reviews/latest/unimplemented_requirement_triage_2026_099.md for deletion-candidate rationale.
<!-- AUTO-UNIMPLEMENTED-TRIAGE:END -->

<!-- AUTO-COMMITTED-REMEDIATION:START -->
## Committed Remediation Work Items

| ID | GitHub Issue | Type | Priority | Status | Summary | Related Requirements | Primary Files |
|---|---|---|---|---|---|---|---|
| RR-2026_102-IMPLEMENTATION-EVIDENCE | Pending Create | Remediation / Implementation | P0 | Sprint Committed | Implementation evidence closure | 74 requirement ids in the top readiness theme | planning/issues/issue_2026_102_Implementation_Evidence_Closure.md |

<!-- AUTO-COMMITTED-REMEDIATION:END -->
