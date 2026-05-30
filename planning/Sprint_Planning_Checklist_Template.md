# Sprint Planning Checklist Template

Use this checklist at the start of **each sprint** to ensure traceability governance is in place.

**Sprint**: [e.g., 2026-09]
**Sprint Lead**: [Name]
**Date**: [Date]
**Checklist Version**: 1.0 (May 8, 2026)

---

## 🎯 Pre-Planning (1-2 Days Before)

- [ ] **Requirements Groomed**: All backlog items have clear requirement IDs (HITL-*, PRJ-*, etc.)
- [ ] **Backlog Prioritized**: PO has ranked backlog for sprint commitment
- [ ] **Capacity Calculated**: Team estimated velocity for sprint
- [ ] **Previous Sprint Archived**:
  - [ ] `planning/Sprint_YYYY_MM_Closure_Checklist.md` completed and signed off
  - [ ] `planning/Sprint_YYYY_MM_Traceability_Matrix.md` archived to `planning/archives/`
  - [ ] Lessons documented: `planning/Sprint_YYYY_MM_Retrospective.md`

---

## 📋 Planning Session (Sprint Start Day)

### Requirement Acceptance

- [ ] **Requirements Reviewed**: Team reviews all requirements for scope, clarity, feasibility
- [ ] **Requirement Types Assigned**: Each accepted requirement has exactly one primary type from the canonical taxonomy
- [ ] **Requirements Assigned**: Each requirement assigned to owner(s)
- [ ] **AC Verified**: Acceptance Criteria clear and testable
- [ ] **Dependencies Identified**: Any inter-requirement dependencies documented
- [ ] **Questions Resolved**: All clarifications captured and answered by PO

### Issue Creation

For **each accepted requirement**, create corresponding issue:

- [ ] **Issue Created**: GitHub/issue tracker item created
  - **Title Format**: `[SPRINT] <REQ_ID>: <short_description>`
  - **Example**: `[SPRINT] HITL-012: Implement Conditional Gate State Reporting`
- [ ] **Issue Description**: Contains:
  - [ ] "Related Requirement" section with REQ ID link
  - [ ] Acceptance Criteria (copied from requirement or summarized)
  - [ ] "Test File" or "Tests" section referencing where tests will go
  - [ ] Any implementation notes or dependencies
- [ ] **Issue Labels**: Add labels
  - [ ] `sprint-2026-09`
  - [ ] `requires-test`
  - [ ] Component label (e.g., `component:hitl`, `component:ui`)
- [ ] **Issue Assigned**: Assigned to owner(s) with target date

### Traceability Matrix Setup

- [ ] **Matrix File Created**: Copy template to `planning/archives/2026-05/Sprint_2026_09_Traceability_Matrix.md`
  - **Command**: `cp planning/Sprint_YYYY_MM_Traceability_Matrix_TEMPLATE.md planning/archives/2026-05/Sprint_2026_09_Traceability_Matrix.md`
- [ ] **Header Updated**: Change sprint year/month in matrix header
- [ ] **Entries Added**: Every accepted requirement + issue added to matrix
  - **Format**:
    | HITL-012 | Functional | Conditional Gate State Tracking | D-S08-020 | Open | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation |
- [ ] **Matrix Committed**: Add to git and commit: `Add Sprint 2026-09 Traceability Matrix`
- [ ] **Matrix Linked**: Add link to sprint planning document or archive path as appropriate

### Governance Documentation

- [ ] **Definition of Done Reviewed**: Team reviews `docs/process/Definition_of_Done.md`
  - Confirm everyone understands criteria
  - Call out any waivers upfront
- [ ] **Requirements & Issues Policy Reviewed**: Reference `docs/process/Requirements_and_Issues_Policy.md`
  - Commit message format: `Fix D-S08-020: [desc]`
  - Test referencing requirement
  - Issue referencing requirement
  - Requirement type recorded and consistent with traceability matrix
- [ ] **Closure Checklist Prepared**: Copy template to `planning/Sprint_2026_09_Closure_Checklist.md`
  - Keep on shared location for sprint end reference

---

## 🛠️ Execution Phase (Throughout Sprint)

### Developer Responsibilities

For each issue assigned:

- [ ] **Branch Created**: Feature branch references issue ID
  - **Format**: `git checkout -b HITL-012/trigger-state-tracking` or `D-S08-020/state-reporting`
- [ ] **Commits Reference Issue**: Every commit message includes issue ID
  - **Good**: `Implements HITL-012: Add triggered field to HitlGateRecord`
  - **Bad**: `Fix bug` or `Update code`
  - **Command**: `git commit -m "Implements HITL-012: Add triggered field"`
- [ ] **Test File Created**: Corresponding test file created with same issue reference in comments
  - **File**: Tests/unit/test_hitl_gate_trigger_state.py
  - **Header Comment**: `# Tests for HITL-012: Conditional Gate State Tracking`
- [ ] **Tests Pass Locally**: Before creating PR, run: `pytest Tests/ -v`

### Code Review Requirements

For each PR:

- [ ] **Commit Messages Checked**: Reviewer verifies issue ID in all commits
- [ ] **Requirement Verified**: Reviewer confirms implementation matches requirement AC
- [ ] **Test Coverage Checked**: Reviewer verifies test file exists and tests pass
- [ ] **Traceability Verified**: Reviewer confirms:
  - [ ] PR links to issue
  - [ ] Issue links to requirement
  - [ ] Commit messages reference issue
  - [ ] Tests reference requirement
- [ ] **Approval**: Second reviewer signs off

### Sprint Tracking

- [ ] **Daily Standup**: Update issue status daily
  - Status: Not Started → In Progress → Review → Done
  - Notes: Any blockers, help needed
- [ ] **Backlog Grooming**: If scope changes, update Traceability Matrix and create/close issues
- [ ] **Mid-Sprint Check** (Day 3-4 of sprint):
  - [ ] Run: `python scripts/verify_sprint_traceability.py --sprint 2026-09`
  - [ ] Verify all issues have requirement links
  - [ ] Verify no orphan requirements
  - [ ] Address gaps before sprint end

---

## ✅ Sprint Closure (Sprint End Day)

- [ ] **All Issues Closed or Deferred**:
  - Closed issues: Have verification evidence attached
  - Deferred issues: Labeled `carryover-2026-10`, moved to backlog
- [ ] **Run Verification Script**:
  ```bash
  python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit
  ```
  - [ ] 0 orphan requirements
  - [ ] 0 orphan issues
  - [ ] All test files exist
  - [ ] Traceability matrix > 90% complete
- [ ] **Complete Closure Checklist**: `planning/Sprint_2026_09_Closure_Checklist.md`
  - [ ] All sections completed
  - [ ] Technical Lead signs off
  - [ ] Artifacts archived
- [ ] **Retrospective Documented**: `planning/Sprint_2026_09_Retrospective.md`
  - What worked? What didn't?
  - Process improvements?
  - Update governance docs if needed

---

## 🔄 Automation & Tooling

### CI/CD Enforcement (Automatic)

When code is pushed:

- ✅ GitHub Actions runs `sprint-traceability.yml`
- ✅ Verifies commit messages have issue IDs
- ✅ Verifies issues link to requirements
- ✅ Verifies code changes are traced
- ✅ Blocks PR if traceability missing (blocking gate)

### Pre-Commit Hook (Optional but Recommended)

Install locally:

```bash
# One-time setup
scripts/setup-git-hooks.sh

# Then every commit gets checked before creation
# If you have issues, you can skip with: git commit --no-verify
```

### Verification Commands (Run Anytime)

```bash
# Check current sprint traceability
python scripts/verify_sprint_traceability.py --sprint 2026-09

# Full audit mode (for sprint closure)
python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit

# Check specific files
grep -r "D-S08-020" planning/
grep -r "HITL-012" Requirements/
```

---

## 📊 Traceability Matrix Template

See: `planning/Sprint_2026_09_Traceability_Matrix.md`

| Requirement ID | Requirement Type | Requirement Name | Issue ID | Issue Status | Test File | Verification Status |
|---|---|---|---|---|---|---|
| HITL-012 | Functional | Conditional Gate Trigger State Tracking | D-S08-020 | Open | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation |
| HITL-013 | Functional | Conditional Gate State Enumeration | D-S08-020 | Open | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation |
| HITL-014 | Functional | Dashboard Conditional Gate Status Display | D-S08-020 | Open | Tests/integration/test_hitl_dashboard_conditional_gates.py | ⏳ Pending Implementation |
| HITL-015 | Functional | Conditional Gate Trigger Metadata | D-S08-020 | Open | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation |

---

## 🚨 Common Issues & Resolutions

| Issue | Resolution |
|-------|---|
| Requirement has no type | Assign one primary canonical type; split or reword if the row mixes concerns |
| Commit message lacks issue ID | Update commit message with `git commit --amend -m "Fix D-S08-020: ..."` |
| Issue has no requirement link | Edit issue, add "Related Requirement: HITL-012" to description |
| Test file not created | Create test file immediately, add to issue description, commit with issue ref |
| CI/CD rejects PR | Run local verification script to identify issues, fix before resubmitting |
| Traceability matrix outdated | Update during daily standups; verify in mid-sprint check; finalize at closure |

---

## 📝 Sign-Off

**Sprint Planning Lead**: ________________ **Date**: ________________

**Verification**:
- [ ] All accepted requirements have issues
- [ ] All issues in Traceability Matrix
- [ ] Team understands Definition of Done
- [ ] CI/CD pipeline verified working
- [ ] Ready to execute sprint

**Notes**:
```
[Any special considerations or process notes for this sprint]
```

---

**This checklist ensures automatic enforcement of requirements → issues → code → tests traceability throughout the sprint lifecycle.**

