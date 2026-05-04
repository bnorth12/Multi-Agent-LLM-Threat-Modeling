# Sprint 2026-05 and 2026-06 Issue Tracker

This tracker is the canonical in-repo status view for sprint issues defined in the implementation plan.

## 1. Tracking Rules

- Update the status checkbox in each issue file first.
- Then update this tracker status table in the same commit.
- Every status change should include the date and initials in the Notes column.
- Use a single feature branch per sprint and keep all sprint issue changes on that branch.

## 2. Sprint 2026-05

| ID | Issue File | Owner Role | Branch | Status | Notes |
|----|------------|------------|--------|--------|-------|
| S05-01 | issue_2026_05_Runtime_Baseline_Hardening.md | Technical Lead and Orchestrator Engineer | feature/sprint_2026_05 | Completed | GH #7; 2026-05-03 BN: duplicate stubs removed, pytest 6/6, committed 8e2c113, pushed |
| S05-02 | issue_2026_05_Input_Ingestion_Spreadsheet_And_Documents.md | Data and Parsing Engineer | feature/sprint_2026_05 | Completed | GH #8; 2026-05-03 BN: Function+Interface entities, fixtures rebuilt (CSV/XLSX/MD/TXT), parser updated, 43 unit tests passing |
| S05-03 | issue_2026_05_Validation_Gates_At_Stage_Boundaries.md | Validation and Schema Engineer | feature/sprint_2026_05 | Completed | GH #9; 2026-05-03 BN: halt behavior wired, 12 integration tests passing, all ACs met, 55 total tests |
| S05-04 | issue_2026_05_HITL_Gate_Set_1.md | HITL and Audit Engineer | feature/sprint_2026_05 | Completed | GH #10; 2026-05-03 BN: Gate 0/1/2 implemented; GateEngine, HitlService, HitlAuditLog; orchestrator wired; 30 integration tests; 85 total tests passing |
| S05-05 | issue_2026_05_Testing_And_CI_Baseline.md | Test Lead and DevOps Engineer | feature/sprint_2026_05 | Completed | GH #11; 2026-05-03 BN: 55 tests passing (43 unit + 12 integration); .github/workflows/ci.yml created; all 4 ACs met |
| S05-06 | issue_2026_05_Documentation_Synchronization.md | Documentation Owner | feature/sprint_2026_05 | Completed | GH #12; 2026-05-03 BN: HMI blueprint, README/src/Tests/fixtures docs updated, fixture format documented, traceability matrix updated |
| S05-10 | issue_2026_05_HMI_Architecture_Blueprint.md | HMI Architect and Documentation Owner | feature/sprint_2026_05 | Completed | GH #17; 2026-05-03 BN: docs/HMI_Architecture_Blueprint.md v0.1; 11 sections, 3 Mermaid flows, screen inventory SCR-001–014, 6 shared components, role matrix; all 7 ACs met |
| S05-07 | issue_2026_05_Sprint_Branch_And_PR_Lifecycle.md | Technical Lead and DevOps Engineer | feature/sprint_2026_05 | Completed | GH #13; 2026-05-03 BN: branch created; all sprint work committed; PR created against main; all 4 ACs met |
| S05-08 | issue_2026_05_Regression_And_Requirement_Test_Execution.md | Test Lead and Validation and Schema Engineer | feature/sprint_2026_05 | Completed | GH #14; 2026-05-03 BN: 85/85 tests passing; requirement mapping in Test_Execution_Summary_Sprint_2026_05.md; all 4 ACs met |
| S05-09 | issue_2026_05_Issue_Closure_And_Validation.md | Product Owner and Technical Lead | feature/sprint_2026_05 | Completed | GH #15; 2026-05-03 BN: all 10 issues carry evidence, dates, initials; no issue closed without requirement + test linkage; all 3 ACs met |

## 3. Sprint 2026-06

| ID | Issue File | Owner Role | Branch | Status | Notes |
|----|------------|------------|--------|--------|-------|
| S06-01 | issue_2026_06_Agent_Pipeline_Completeness.md | Orchestrator Engineer and Technical Lead | feature/sprint_2026_06 | Not started | |
| S06-02 | issue_2026_06_HITL_Gate_Set_2.md | HITL and Audit Engineer | feature/sprint_2026_06 | Not started | |
| S06-03 | issue_2026_06_Retrieval_Evidence_Linkage.md | Data and Parsing Engineer and Validation and Schema Engineer | feature/sprint_2026_06 | Not started | |
| S06-04 | issue_2026_06_Artifact_Generation_And_E2E_Validation.md | Test Lead and Orchestrator Engineer | feature/sprint_2026_06 | Not started | |
| S06-05 | issue_2026_06_Release_And_Operational_Readiness.md | DevOps Engineer and Documentation Owner | feature/sprint_2026_06 | Not started | |

## 4. Completion Gate

A sprint issue can be marked Completed only when all of the following are true.

- Acceptance criteria in the issue file are met.
- Tests are added or updated and passing.
- Requirement links are verified.
- Documentation changes are merged if behavior changed.
