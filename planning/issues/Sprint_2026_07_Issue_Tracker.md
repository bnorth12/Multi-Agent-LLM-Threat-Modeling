# Sprint 2026-07 Issue Tracker

This tracker is the canonical in-repo status view for sprint issues defined in the implementation plan.

## 1. Tracking Rules

- Update the status checkbox in each issue file first.
- Then update this tracker status table in the same commit.
- Every status change should include the date and initials in the Notes column.
- Use a single feature branch per sprint and keep all sprint issue changes on that branch.
- Link all GitHub issue numbers in the Notes column as GH #NNN.

## 2. Sprint 2026-07 (Workstreams A–F + Closeout)

| ID | GitHub Issue | Workstream | Owner Role | Status | Notes |
|----|--------------|-----------|------------|--------|-------|
| S07-01 | GH #26 | A | Documentation Owner | Not Started | Documentation and Traceability Cleanup: SCR naming, README status, traceability matrix, issue linking |
| S07-02 | GH #27 | B | HMI Architect and Orchestrator Engineer | Not Started | Model Provider Selection and Connection HMI (SCR-012/013/014): provider dropdown, connection details, validation, Custom/Intranet support |
| S07-03 | GH #28 | C | Validation and Schema Engineer | Not Started | Enforce Input Entry Model Validation Gate with Offline Override: validation state, offline mode banner, guard logic |
| S07-04 | GH #29 | D | Orchestrator Engineer and HMI Architect | Not Started | Prompt Editor and Version History HMI (SCR-010/011): per-agent editor, version history, temperature config |
| S07-05 | GH #30 | E (part 1) | HMI Architect and Test Lead | Not Started | Stage Results and Threat Review Screens (SCR-003/004): stage results viewer, threat/mitigation review |
| S07-06 | GH #31 | E (part 2) | HMI Architect and Data and Parsing Engineer | Not Started | Results Export and Snapshot Screens (SCR-007/008/009): export formats, snapshot save/restore workflows |
| S07-07 | GH #32 | F | Test Lead and DevOps Engineer | Not Started | Test and CI Gate Expansion for S07 GUI Work: unit/integration/e2e coverage, keep llm_live isolated, non-live CI green |
| S07-08 | GH #33 | Closeout | Product Owner and Technical Lead | Not Started | Required Online End-to-End Validation Gate for Sprint Closeout: online llm_live run, evidence collection, sprint cannot close without |

## 3. Completion Gate

A sprint issue can be marked Completed only when all of the following are true:

- Acceptance criteria in the GitHub issue are met.
- Tests are added or updated and passing.
- Requirement links are verified.
- Documentation changes are merged if behavior changed.
- Sprint issue status updated in this tracker with date and initials.

## 3. Discovered Issues (During Sprint Execution)

Issues discovered during sprint work that are not in the original 8 workstreams. Track here to prevent loss of scope if work is deferred.

| ID | GitHub Issue | Description | Severity | Status | Notes |
|----|--------------|-------------|----------|--------|-------|
| — | — | — | — | — | — |

## 4. Sprint Definition of Done

- All 8 workstream issues completed and passed completion gate.
- Non-live CI tests passing (all markers except llm_live).
- At least one online llm_live end-to-end validation run completed and evidenced.
- User manual and traceability matrix updated.
- Feature branch merged to main via PR with all issue links verified.
- All GitHub issues closed with Completion evidence.
- Discovered issues logged with GH issue numbers; deferred issues marked `deferred-to-sprint-2026-08`.
