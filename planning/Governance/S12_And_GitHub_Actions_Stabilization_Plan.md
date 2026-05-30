# S12 and GitHub Actions Stabilization Plan

Date: 2026-05-25
Owner: Sprint 2026-12 delivery and release governance
Status: Proposed for immediate execution

## 1. Objective

Close or stabilize open Sprint 2026-12 issues and stop recurring GitHub Actions failures from blocking confidence and release readiness.

## 1.1 Planning Model

- Capability is the top-level planning abstraction.
- Requirements are decomposed from capability intent and belong in sprint and multi-sprint plans.
- Functions are decomposed from capabilities and requirements, and they are documented in architecture and design artifacts.
- Implementation delivers the functions in code, scripts, and runtime behavior.
- Verification proves the implemented functions and their requirement coverage.
- The mapping is many-to-many, not 1:1: a capability may break into multiple requirements and functions, and a single requirement may be supported by multiple functions.

## 2. Evidence Baseline

Sources reviewed:
- planning/issues/Sprint_2026_12_Issue_Tracker.md
- planning/issues/Sprint_2026_12_GitHub_Issue_Drafts.md
- .github/workflows/ci.yml
- .github/workflows/sprint-traceability.yml
- GitHub Actions workflow pages for CI, Sprint Traceability Enforcement, Copilot cloud agent, Copilot code review, and Dependency Graph
- GitHub issue list (open issue set)

Observed state snapshot:
- CI workflow latest run #70 passed.
- Recent CI failures split into two patterns:
  - Unit test regression on feature branch (now corrected by latest CI-fix commit).
  - Live LLM lane failures on main while non-live lanes pass.
- Sprint Traceability Enforcement shows repeated failures on push to main.
- Copilot cloud agent, Copilot code review, and Dependency Graph workflows are green in recent history.
- Open GitHub issues currently include S12 issue numbers #63 through #70 and #62.

## 3. S12 Triage Matrix

### 3.1 Close-Ready After Verification Bundle Update

| Tracker ID | GitHub Issue | Current Tracker Status | Closure Decision | Required Closure Artifacts |
|---|---|---|---|---|
| S12-011 | #64 | In Review | Close after one final evidence refresh | Traceability row update, execution log entry, test evidence link |
| S12-012 | #63 | In Review | Close after one final evidence refresh | Traceability row update, execution log entry, test evidence link |
| S12-015 | #68 | In Review | Close after one final evidence refresh | Traceability row update, execution log entry, browser validation evidence |
| S12-016 | #69 | In Review | Close after one final evidence refresh | Traceability row update, execution log entry, run-selection UX evidence |
| S12-017 | #70 | In Review | Close after one final evidence refresh | Traceability row update, execution log entry, restart-safe retrieval test evidence |
| S12-018 | TBD | In Review | Close after issue number assignment and closure evidence sync | Create GitHub issue, link latest CI-fix evidence, update tracker row from TBD |

### 3.2 Active Build Scope (Not Close-Ready)

| Tracker ID | GitHub Issue | Current Tracker Status | Decision | Next Action |
|---|---|---|---|---|
| S12-013 | #67 | In Progress | Keep Open | Complete Gate 0 enforcement implementation and test bundle |
| S12-014 | #66 | In Progress | Keep Open | Complete post-Stage-1 normalization gate and test bundle |
| S12-031 | TBD | In Progress | Keep Open | Implement parse-segment timeline behavior and create GitHub issue |

### 3.3 Valid Backlog (Post-Run and Proposed)

| Tracker IDs | Current Status | Decision | Planning Action |
|---|---|---|---|
| S12-019 through S12-030 | Proposed or Proposed (Post-Run) | Keep Open as valid backlog | Group into implementation waves with explicit requirement-ID sync tasks |
| S12-032 | Proposed (Post-Run) | Keep Open as valid backlog | Treat as diagram-quality and decomposition hardening wave |
| D-S12-011 | Proposed | Keep Open as governance decision record | Hold product decision review and requirement delta update |

### 3.4 OBE Classification

No Sprint 2026-12 items are currently OBE based on tracker and issue evidence. Items are either close-ready, active implementation, or valid backlog.

## 4. GitHub Actions Problem Assessment

## 4.1 Workflow-by-Workflow Health

| Workflow | Current Health | Primary Problem Pattern |
|---|---|---|
| CI | Mixed, now green on latest run | Historical unit regression and recurring live-LMM lane instability on main |
| Sprint Traceability Enforcement | Unstable (frequent failures) | Hard-fail behavior on push to main and strict governance checks without staged enforcement |
| Copilot cloud agent | Stable | No immediate reliability issue observed |
| Copilot code review | Stable | No immediate reliability issue observed |
| Dependency Graph | Stable | No immediate reliability issue observed |

## 4.2 Cross-Cutting CI/Actions Risks

1. Trigger mismatch risk
- CI runs on main and feature branches, but not on dev, creating false confidence when work lands on dev first.

2. Live-test coupling risk
- Live LLM tests run as part of CI on push to main and dominate failure signal even when all non-live quality gates pass.

3. Governance gate noise risk
- Sprint Traceability workflow currently fails frequently, reducing signal quality and conditioning teams to ignore red builds.

4. Runtime deprecation risk
- Node 20 deprecation warnings are present in both CI and traceability workflows and will become disruptive if not upgraded.

## 5. Stabilization Plan

## Phase A: Stop Failure Noise (0 to 2 days)

1. Split live lane from blocking CI gate
- Keep non-live suite as required merge gate.
- Move live LLM tests to separate workflow triggered by schedule and workflow_dispatch.
- Keep optional main-branch live run, but non-blocking for merge readiness.

2. Re-scope traceability enforcement severity
- Keep pull request checks strict and blocking.
- Convert push-to-main traceability from fail-fast to audit/report mode with warning output and artifact report.

3. Add trigger parity for dev quality visibility
- Add dev branch trigger for non-blocking CI visibility or enforce feature-branch only push model with branch protection.

4. Resolve Node runtime deprecation exposure
- Upgrade action versions to Node 24-compatible releases.
- Add temporary explicit Node 24 opt-in variable if needed during migration window.

## Phase B: Restore Governance Signal Quality (2 to 5 days)

1. Introduce workflow-level concurrency groups
- Cancel superseded runs on same branch for CI and traceability workflows.

2. Add path-aware execution controls
- Skip full non-live test fan-out for documentation-only deltas when appropriate.
- Retain mandatory checks for source, tests, requirements, and planning issue changes.

3. Publish failure taxonomy and runbook
- Create one-page runbook mapping job failure types to owner and first action.

## Phase C: S12 Closure Execution (parallel with Phase A and B)

1. Close-ready batch execution
- Close S12-011, S12-012, S12-015, S12-016, S12-017 once closure evidence is refreshed.
- Create GitHub issue for S12-018 and close it with linked CI-fix evidence.

2. Active build batch execution
- Complete S12-013, S12-014, and S12-031 with explicit requirement and test trace links before closure.

3. Backlog normalization
- Create missing GitHub issues for S12-019 through S12-032.
- Assign each item to one of three waves:
  - Wave 1: runtime correctness and gate compliance (S12-023, S12-024, S12-025)
  - Wave 2: artifact UX and export surface (S12-019, S12-021, S12-022, S12-026, S12-027, S12-029, S12-030)
  - Wave 3: incremental model enrichment and diagram depth quality (S12-028, S12-032)

## 6. Governance Deliverables

Required artifacts to complete this plan:

1. S12 status matrix update
- Update planning/issues/Sprint_2026_12_Issue_Tracker.md with triage decision and closure target date per row.

2. Traceability alignment report
- Add an appendix in planning/Sprint_2026_12_Traceability_Matrix.md mapping each S12 issue to requirement IDs, tests, and evidence links.

3. Actions reliability checklist
- Add planning/Governance/GitHub_Actions_Reliability_Checklist.md with:
  - trigger policy
  - blocking vs non-blocking lane definitions
  - live-lane policy
  - deprecation monitoring checklist

4. Workflow change PR bundle
- One PR for workflow hardening changes in .github/workflows/ci.yml and .github/workflows/sprint-traceability.yml.
- One PR for S12 issue tracker and traceability synchronization updates.

5. Planning hierarchy alignment
- Keep the capability-to-requirement-to-function hierarchy visible in sprint and multi-sprint planning artifacts so architecture, implementation, and verification stay linked to the same intent.

## 7. Exit Criteria

Plan is complete when all are true:

- CI non-live gate is consistently green on active development branches.
- Live LLM failures do not block non-live merge readiness.
- Sprint Traceability failures are reduced to actionable pull-request governance defects.
- Close-ready S12 items are closed with linked evidence.
- Active S12 items have implementation branches and target dates.
- Backlog S12 items all have GitHub issue numbers and wave assignment.
