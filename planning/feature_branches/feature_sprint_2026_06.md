# Feature Branch: sprint_2026_06

## Purpose
Track all Sprint 2026-06 scope on one branch to reduce branching overhead and keep implementation traceability centralized.

## Branch Naming
feature/sprint_2026_06

## Policy
This sprint uses a single feature branch. Do not create per-issue or per-workstream branches for Sprint 2026-06 unless an emergency hotfix exception is approved.

## Included Issue IDs
- S06-01 Agent Pipeline Completeness
- S06-02 HITL Gate Set 2
- S06-03 Retrieval Evidence Linkage
- S06-04 Artifact Generation and E2E Validation
- S06-05 Release and Operational Readiness (expanded: screenshot evidence package)
- S06-06 User Manual
- S06-07 Streamlit Application Shell

## Tracking Sources
- planning/issues/Sprint_2026_05_06_Issue_Tracker.md
- planning/Sectioned_Implementation_Plan.md

## PR Target
origin/main

## Exit Conditions
- All Sprint 2026-06 issue acceptance criteria are complete.
- Definition of Done requirements are met for completed scope.
- PR includes links to updated issue files and requirement references.

## Auto-Close on Merge
The PR commit message must include the following to trigger GitHub auto-close:
- Closes #18 (S06-01)
- Closes #19 (S06-02)
- Closes #20 (S06-03)
- Closes #21 (S06-04)
- Closes #22 (S06-05)
- Closes #23 (S06-06)
- Closes #24 (S06-07)
- Closes #2 (OBE: framework source files — delivered in S05)
- Closes #3 (OBE: canonical graph schema validation — typed-model validation supersedes JSON schema file approach)
