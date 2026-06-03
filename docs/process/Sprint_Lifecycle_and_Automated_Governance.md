# Sprint Lifecycle & Automated Traceability Governance

**Purpose**: Define the complete sprint lifecycle with automatic enforcement of requirements → issues → code → tests traceability.

**Last Updated**: May 8, 2026
**Version**: 1.0

---

## 🎯 Sprint Lifecycle Overview

```
PLANNING PHASE (Day 0)
├─ Requirements grooming
├─ Issue creation
├─ Traceability matrix setup
└─ Team onboarding

EXECUTION PHASE (Days 1-9)
├─ Daily development
├─ Automated CI/CD checks (on every PR)
├─ Mid-sprint verification (Day 3-4)
└─ Issue tracking

CLOSURE PHASE (Day 10)
├─ Final verification
├─ Evidence collection
├─ Sprint sign-off
└─ Archive & handoff
```

---

## 📅 PHASE 1: PLANNING (Sprint Start - Day 0)

### 1a. Requirement Grooming (1-2 days before sprint)

**Goal**: Ensure all backlog items have clear, testable requirements with unique IDs

**Inputs**:

- Backlog of user stories and technical items
- Previous sprint retrospective feedback
- Business/product priorities

**Steps**:

1. **Review Backlog**
   - PO/Tech Lead review all items
   - Clarify acceptance criteria
   - Estimate complexity/story points

1. **Assign Requirement IDs**
   - Follow ID scheme: `COMPONENT-NNN[Letter]`
   - Examples: `HITL-012`, `GUI-003A`, `INT-015`, `PRJ-008`
   - If requirement created during sprint, assign next ID in sequence

1. **Document Requirements**
   - Create/update file in `Requirements/` folder
   - Include: ID, name, description, AC, test method, related issue link (if exists)
   - Example: `Requirements/HITL-012_Conditional_Gate_State_Tracking.md`

1. **Commit & Link**
   - Commit: `git add Requirements/; git commit -m "Groom backlog: Add HITL-012, HITL-013, HITL-014, HITL-015"`

**Automation**: None (manual PO responsibility)

**Success Criteria**:

- ✅ All sprint candidates have unique requirement ID
- ✅ All ACs are testable (verifiable, measurable)
- ✅ All requirements documented in `Requirements/` folder

**Tool References**:

- Requirement template: [Requirements/COMPONENT-NNN_Example.md]
- Traceability policy: [docs/process/Requirements_and_Issues_Policy.md]

---

### 1b. Issue Creation (Sprint Planning Day)

**Goal**: Create one issue per accepted requirement; establish bidirectional traceability

**Inputs**:

- Groomed requirements from Phase 1a
- Team capacity/velocity estimate

**Steps**:

1. **Accept Requirements into Sprint**
   - Team commits to sprint workload
   - PO confirms priority/scope for accepted items

1. **Create Issues** (one per requirement)

   ```bash
   # Example issue creation checklist per requirement:

   Requirement: HITL-012 - Conditional Gate Trigger State Tracking

   Issue Title:       [SPRINT] HITL-012: Implement Conditional Gate State Tracking
   Issue Description: Requirement: HITL-012
                     Acceptance Criteria:
                     - [ ] HitlGateRecord has triggered field
                     - [ ] HitlGateRecord has trigger_reason field
                     - [ ] Tests passing

                     Test File: Tests/unit/test_hitl_gate_trigger_state.py

   Issue Labels:      sprint-2026-09, requires-test, component:hitl
   Issue Assigned:    [Developer Name] - Target: [Sprint End Date]
   ```

1. **Verify Bidirectional Link**
   - Requirement → Issue: Requirement file links to issue ID
   - Issue → Requirement: Issue title/description references requirement ID
   - **Verification Command**: `grep -r "HITL-012" planning/ Requirements/`

1. **Commit Issues**
   - Each issue stored as: `planning/issues/issue_2026_09_HITL_012_*.md`
   - Commit: `git add planning/issues/; git commit -m "Create sprint issues for HITL-012 through HITL-015"`

**Automation**: CI/CD will verify links later (Phase 2)

**Success Criteria**:

- ✅ Every accepted requirement has corresponding issue
- ✅ Every issue title references requirement ID
- ✅ Every issue description contains requirement ID
- ✅ Every issue assigned to owner with target date

---

### 1c. Traceability Matrix Setup (Sprint Planning Day)

**Goal**: Create single source of truth for sprint requirements → issues → code → tests

**Inputs**:

- Accepted requirements + created issues from Phases 1a-1b

**Steps**:

1. **Copy Template**
   ```bash
   cp planning/Sprint_Traceability_Matrix_Template.md \
      planning/Sprint_2026_09_Traceability_Matrix.md
   ```

1. **Update Header**
   - Sprint: 2026-09
   - Start Date: [Sprint Start]
   - End Date: [Sprint End]
   - Status: 🔄 Active

1. **Populate Requirement Rows**
   - One row per accepted requirement
   - Columns:
     | # | REQ ID | REQ Name | Issue ID | Status | Assigned To | Test File | Verification Status | Notes |
   - Example:
     | 1 | HITL-012 | Trigger State Tracking | D-S08-020 | Open | Jane Doe | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation | Track triggered field |

1. **Add to Version Control**
   ```bash
   git add planning/Sprint_2026_09_Traceability_Matrix.md
   git commit -m "Create Sprint 2026-09 Traceability Matrix with 4 requirements"
   ```

1. **Link in Planning Docs**
   - Add link to `planning/README.md` or sprint summary
   - Share link in sprint kickoff meeting

**Automation**: Script `scripts/verify_sprint_traceability.py` will read this file during execution phase

**Success Criteria**:

- ✅ Traceability matrix file exists with all sprint requirements
- ✅ Every requirement row has: REQ ID, Issue ID, Assigned To, Test File column
- ✅ Matrix committed to version control
- ✅ Matrix linked from sprint planning document

---

### 1d. Team Onboarding (Sprint Planning Day - End)

**Goal**: Ensure entire team understands traceability processes and automation

**Steps**:

1. **Review Definition of Done**
   - Share: `docs/process/Definition_of_Done.md`
   - Team reviews all DoD criteria
   - Call out any waivers for this sprint

1. **Review Requirements & Issues Policy**
   - Share: `docs/process/Requirements_and_Issues_Policy.md`
   - Emphasize: Commit message format, issue reference requirements
   - Demonstrate: Good vs. bad commit messages

1. **Demo CI/CD Automation**
   - Show: `.github/workflows/sprint-traceability.yml`
   - Explain: What CI/CD will check, what will block PR
   - Demo: Example PR that passes vs. fails traceability checks

1. **Distribute Tools Reference**
   - Email/Slack:
     - Verification script: `python scripts/verify_sprint_traceability.py --sprint 2026-09`
     - Definition of Done: `docs/process/Definition_of_Done.md`
     - GitHub Actions results: `.github/workflows/sprint-traceability.yml`

1. **Sign-Off**
   - Team confirms understanding
   - Document in: `planning/Sprint_2026_09_Planning_Checklist.md` → Sprint Planning Sign-Off section
   - Sprint Lead signature

**Automation**: Documentation auto-generated (no execution automation)

**Success Criteria**:

- ✅ Team understands commit message format
- ✅ Team knows CI/CD will block PRs without issue references
- ✅ Team knows DoD requirements before starting work

---

## 🏗️ PHASE 2: EXECUTION (Sprint Days 1-9)

### 2a. Daily Development (Ongoing)

**Goal**: Implement requirements while maintaining traceability at every commit

**Workflow for Each Task**:

1. **Create Feature Branch**
   ```bash
   # Branch name references issue
   git checkout -b HITL-012/trigger-state-tracking
   # or
   git checkout -b D-S08-020/state-reporting
   ```

1. **Write Code + Tests Together**
   - Create/modify code file: `src/threat_modeler/hitl/models.py`
   - Create test file: `Tests/unit/test_hitl_gate_trigger_state.py`
   - Tests reference requirement in header comment: `# Tests for HITL-012`

1. **Commit with Issue Reference** (AUTOMATIC ENFORCEMENT)
   ```bash
   # Good commit message (will PASS CI/CD):
   git commit -m "Implements HITL-012: Add triggered field to HitlGateRecord

   - Add triggered: bool = False field
   - Add trigger_reason: str | None = None field
   - Update to_dict() and from_dict() methods
   - All tests passing"

   # Bad commit message (will FAIL CI/CD):
   git commit -m "Fix bug in models.py"  # ❌ No issue reference
   ```

1. **Run Tests Locally**
   ```bash
   pytest Tests/unit/test_hitl_gate_trigger_state.py -v
   ```

1. **Push & Create PR**
   ```bash
   git push origin HITL-012/trigger-state-tracking
   # Create PR on GitHub with title: "[SPRINT] HITL-012: Implement Conditional Gate State Tracking"
   ```

**Automation Trigger Point**: On PR creation, GitHub Actions runs **sprint-traceability.yml**

---

### 2b. Automated CI/CD Verification (Triggers on Every PR)

**What Runs Automatically** (no manual action needed):

✅ **Commit Message Verification**

- Regex check: Does commit message contain issue ID (D-S08-*, HITL-*, etc.)?
- **Result**:
  - ✅ PASS: Green check, PR allowed to proceed
  - ❌ FAIL: Red check, PR blocked with error message
  - **Error Message**: "Commit message must reference issue ID (e.g., `Fix D-S08-020: ...`)"

✅ **Issue → Requirement Traceability Check**

- Script runs: `python scripts/verify_sprint_traceability.py --sprint 2026-09`
- Checks: Does issue link to requirement?
- **Result**:
  - ✅ PASS: Green check
  - ❌ FAIL: Red check, blocks merge

✅ **Test File Reference Check**

- Looks for: "Tests/" or "Test File" in issue description
- **Result**:
  - ✅ PASS: Green check
  - ⚠️ WARN: Yellow check (non-blocking) if missing
  - ❌ FAIL: Red check if code file changed but no test referenced

**How to Fix CI/CD Failures**:

| Failure | Fix | Command |
|---------|-----|---------|
| "Commit message lacks issue" | Update commit message | `git commit --amend -m "Fix D-S08-020: ..."` then `git push --force` |
| "Issue has no requirement" | Add requirement link to issue | Edit issue on GitHub, add "Requirement: HITL-012" to description |
| "Test file not referenced" | Add test file to issue description | Edit issue, add "Test File: Tests/unit/test_*.py" |

**Status Check**: Look for green ✅ or red ❌ checkmarks in PR

---

### 2c. Code Review (Peer Review Before Merge)

**Reviewer Checklist** (in addition to normal code review):

```markdown
## Traceability Checklist

- [ ] Commit messages reference issue ID (e.g., D-S08-020)
- [ ] Issue title includes requirement ID (e.g., HITL-012)
- [ ] Implementation matches requirement AC
- [ ] Test file exists and covers requirement AC
- [ ] Tests pass locally: `pytest Tests/ -v`
- [ ] Traceability matrix will be updated after merge
```

**Automated Gate**: CI/CD must pass before merge allowed (non-negotiable)

**Manual Gate**: Code reviewer confirms traceability looks good (second check)

---

### 2d. Mid-Sprint Verification (Day 3-4 of Sprint)

**Goal**: Catch traceability gaps early; ensure on-track to close sprint

**When**: Mid-sprint (typically Thursday if sprint is Mon-Fri)

**Who**: Technical Lead or designated scrum master

**Steps**:

1. **Run Verification Script**
   ```bash
   cd /path/to/workspace
   python scripts/verify_sprint_traceability.py --sprint 2026-09
   ```

1. **Review Output**
   - Look for ✅ PASS indicators
   - Look for ❌ FAIL or ⚠️ WARN indicators
   - Review any orphan issues or requirements

1. **Address Gaps**
   - If orphan requirement (no issue): Create issue immediately
   - If orphan issue (no requirement): Link to requirement or create one
   - If missing test file: Add to issue description
   - If tests failing: Escalate to developer

1. **Update Traceability Matrix**
   - Update "Verification Status" column
   - If issue moved to "In Progress": update status
   - If new test results available: update test pass rate

1. **Report to Team**
   - Share results in standup
   - Highlight any blockers
   - Confirm on track to closure

**Automation**: Verification script auto-generated output (manual interpretation)

**Success Criteria**:

- ✅ 0 orphan requirements
- ✅ 0 orphan issues
- ✅ All issues have test file reference
- ✅ No blockers found

---

### 2e. Daily Standup (Every Day)

**Traceability Update** (1-minute mention):

- **Dev Status**: Issue → In Progress/In Review/Done
- **Blocker Check**: Any traceability issues?
- **Test Status**: Tests passing locally? CI/CD green?

**Example**:
```
Dev: "HITL-012 is 80% done, tests all passing locally, PR under review.
      CI/CD checks passed. Should merge tomorrow."
```

---

## 🔒 PHASE 3: CLOSURE (Sprint End - Day 10)

### 3a. Final Verification (Sprint End Morning)

**Goal**: Verify 100% traceability before sprint sign-off

**Steps**:

1. **Run Audit Mode Verification**
   ```bash
   python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit
   ```

1. **Review Full Matrix**
   - All requirements: ✅ PASS
   - All issues: Closed or labeled "carryover"
   - All tests: Passing
   - All evidence: Collected

1. **Check for Waivers**
   - Any `dod-waiver:*` labels on issues?
   - If yes: Technical Lead must have approved
   - Document in Traceability Matrix "Notes" column

1. **Verify CI/CD Green**
   - All PRs merged with green ✅ checks
   - No red ❌ indicators remaining
   - All commits reference issues

**Output**: Verification report shows 0 orphans, all tests PASS

---

### 3b. Evidence Collection (Sprint End Morning-Afternoon)

**Goal**: Archive all verification evidence for audit trail

**What to Collect**:

1. **Test Results**
   - Screenshot/log: `pytest Tests/ -v` output showing all PASS
   - Coverage report (if applicable)
   - CI/CD run summary

1. **Issue Evidence**
   - For each closed issue: screenshot or link to verification artifact
   - Example: "Added screenshot of dashboard showing 🟢 Auto-Bypassed emoji"
   - Added to issue description or PR

1. **Requirement Evidence**
   - For each requirement: Link to closed issue
   - Link to merged PR/commit
   - Test file reference

1. **Archive Artifacts**
   ```bash
   mkdir -p planning/archives/sprint_2026_09_evidence/
   cp planning/Sprint_2026_09_Traceability_Matrix.md \
      planning/archives/sprint_2026_09_evidence/Traceability_Matrix_FINAL.md
   cp tests_output.log planning/archives/sprint_2026_09_evidence/
   # Add screenshots, test runs, etc.
   ```

---

### 3c. Sprint Closure Checklist (Sprint End Afternoon)

**Goal**: Complete formal checklist; get Technical Lead sign-off

**Task**: Complete `planning/Sprint_2026_09_Closure_Checklist.md`

**Sections**:

- ✅ Traceability Matrix Complete
- ✅ Issue Status Verified
- ✅ Test Evidence Complete
- ✅ Requirement Sync Complete
- ✅ Code Quality Gates
- ✅ Documentation Updated
- ✅ Artifacts Collected
- ✅ Sign-Off & Approval

**Sign-Off**: Technical Lead reviews and signs all checkboxes

**Result**: Formal sprint closure document archived

---

### 3d. Retrospective & Lessons Learned (Sprint End - Post-Standup)

**Goal**: Continuous improvement of sprint process

**Create**: `planning/Sprint_2026_09_Retrospective.md`

**Questions to Document**:

- What worked? What didn't?
- Did traceability governance help or hinder?
- Any process improvements for next sprint?
- Any policy updates needed to Definition of Done or Requirements & Issues Policy?

**Handoff to Next Sprint**: Update templates and checklists based on feedback

---

### 3e. Handoff to Next Sprint (Sprint End - End of Day)

**Steps**:

1. **Archive Sprint Artifacts**
   ```bash
   mv planning/Sprint_2026_09_Traceability_Matrix.md \
      planning/archives/Sprint_2026_09_Traceability_Matrix_FINAL.md
   ```

1. **Prepare Next Sprint Template**
   ```bash
   cp planning/Sprint_Traceability_Matrix_Template.md \
      planning/Sprint_2026_10_Traceability_Matrix.md
   # Update header with new sprint dates
   ```

1. **Archive Carryover Items**
   - Move unfinished issues to backlog
   - Label: `carryover-2026-10`
   - Link to next sprint

1. **Commit & Push**
   ```bash
   git add planning/archives/ planning/Sprint_2026_10_Traceability_Matrix.md
   git commit -m "Close Sprint 2026-09; archive artifacts and prepare Sprint 2026-10"
   git push
   ```

1. **Communicate to Team**
   - Sprint officially closed
   - Next sprint ready to kick off
   - Link to lessons learned

---

## 🤖 Automation Summary

### What's Automatic vs. Manual

| Step | Automatic? | Tool/Process |
|------|---|---|
| Requirement grooming | Manual | PO responsibility |
| Issue creation | Manual | GitHub/issue tracker |
| Traceability matrix setup | Manual | Template + copy |
| **Commit message verification** | ✅ **YES** | CI/CD workflow: sprint-traceability.yml |
| **Issue → Requirement verification** | ✅ **YES** | CI/CD workflow + verify_sprint_traceability.py |
| **Test file verification** | ✅ **YES** | CI/CD workflow |
| **Mid-sprint check** | Manual (script helps) | `verify_sprint_traceability.py --sprint 2026-09` |
| **Sprint closure** | Manual | Closure checklist + script |
| **Retrospective** | Manual | Documented reflection |

### Key Automation Points

1. **Commit Time** (Developer creates commit)
   - Pre-commit hook (optional): Warns about issue reference
   - ⚠️ If `--no-verify`: Can bypass (not recommended)

1. **PR Creation Time** (Developer pushes, creates PR)
   - ✅ GitHub Actions runs sprint-traceability.yml
   - ✅ Verifies commit message, issue link, test reference
   - ✅ Blocks merge if verification fails (non-waivable)

1. **Review Time** (Reviewer approves)
   - Manual: Reviewer checks traceability too
   - CI/CD must pass before review even considered

1. **Merge Time** (PR merged)
   - Issue auto-closes (if configured)
   - Traceability matrix updated manually (or via script)

---

## 📋 Key Documents Reference

| Document | Purpose | When to Use |
|---|---|---|
| [Definition of Done](../docs/process/Definition_of_Done.md) | DoD criteria all work must meet | Team onboarding, code review, issue closure |
| [Requirements & Issues Policy](../docs/process/Requirements_and_Issues_Policy.md) | Traceability governance rules | Team onboarding, policy questions |
| [Sprint Planning Checklist](./Sprint_Planning_Checklist_Template.md) | Sprint setup tasks | Sprint start |
| [Traceability Matrix Template](./Sprint_Traceability_Matrix_Template.md) | Copy for each sprint | Sprint planning |
| [Sprint Closure Checklist](./Sprint_2026_09_Closure_Checklist.md) | Sprint closure formal checklist | Sprint end |
| [Verification Script](../scripts/verify_sprint_traceability.py) | Automated traceability checks | Mid-sprint + closure |
| [CI/CD Workflow](../.github/workflows/sprint-traceability.yml) | GitHub Actions enforcement | On every PR (automatic) |

---

## 🎓 Example Sprint Walkthrough

### Example: Implementing HITL-012

**Day 0 (Planning)**
```
1. PO grooms HITL-012: "Conditional Gate Trigger State Tracking"
2. Team accepts HITL-012 into sprint 2026-09
3. Dev (Jane) creates issue: "[SPRINT] HITL-012: Implement Conditional Gate State Tracking"
4. Issue description contains: "Requirement: HITL-012"
5. Issue Test File field: "Tests/unit/test_hitl_gate_trigger_state.py"
6. Traceability matrix row added: | 1 | HITL-012 | ... | D-S08-020 | Open | Jane | Tests/unit/... | ⏳ Pending |
```

**Days 1-2 (Implementation)**
```
1. Jane creates branch: git checkout -b HITL-012/trigger-state-tracking
2. Jane writes code in src/threat_modeler/hitl/models.py:
   - Adds triggered: bool = False field
   - Adds trigger_reason: str | None = None field
3. Jane writes tests in Tests/unit/test_hitl_gate_trigger_state.py:
   - Header: # Tests for HITL-012: Conditional Gate Trigger State Tracking
   - Tests cover all AC from HITL-012
4. Jane commits: git commit -m "Implements HITL-012: Add triggered and trigger_reason fields"
5. Jane pushes: git push origin HITL-012/trigger-state-tracking
6. Jane creates PR with title: "[SPRINT] HITL-012: Implement Conditional Gate State Tracking"
```

**CI/CD Automatic Check**:
```
GitHub Actions runs sprint-traceability.yml:
✅ Commit message has "HITL-012" → PASS
✅ Issue #D-S08-020 has "HITL-012" in title → PASS
✅ Issue description references test file → PASS
✅ PR approved to proceed to review
```

**Day 3 (Code Review)**
```
1. Bob (reviewer) reads PR
2. Bob verifies:
   - Commit message references HITL-012 ✅
   - Issue links to requirement HITL-012 ✅
   - Implementation matches HITL-012 AC ✅
   - Tests pass locally ✅
3. Bob approves PR: "✅ Traceability verified. Code looks good."
```

**Day 3 (Merge)**
```
1. PR merged to main
2. All CI/CD checks PASS
3. Issue automatically closes
4. Jane updates Traceability Matrix:
   - Status: Merged
   - Verification Status: ✅ PASS
   - Evidence: Link to PR #123, test output screenshot
```

**Day 4 (Mid-Sprint Check)**
```
Tech Lead runs: python scripts/verify_sprint_traceability.py --sprint 2026-09
Output shows: HITL-012 ✅ PASS with D-S08-020 and Tests/unit/test_hitl_gate_trigger_state.py
```

**Day 10 (Sprint Closure)**
```
Tech Lead runs: python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit
Result: All 4 requirements (HITL-012-015) → PASS with evidence
Traceability matrix archived
Sprint officially closed
```

---

## ✅ Implementation Checklist

Deploy this automated governance by creating these files:

- [x] [docs/process/Definition_of_Done.md](../docs/process/Definition_of_Done.md)
- [x] [docs/process/Requirements_and_Issues_Policy.md](../docs/process/Requirements_and_Issues_Policy.md)
- [x] [planning/Sprint_Planning_Checklist_Template.md](./Sprint_Planning_Checklist_Template.md)
- [x] [planning/Sprint_Traceability_Matrix_Template.md](./Sprint_Traceability_Matrix_Template.md)
- [x] [planning/Sprint_2026_09_Closure_Checklist.md](./Sprint_2026_09_Closure_Checklist.md)
- [x] [scripts/verify_sprint_traceability.py](../scripts/verify_sprint_traceability.py)
- [x] [.github/workflows/sprint-traceability.yml](../.github/workflows/sprint-traceability.yml)
- [ ] [scripts/setup-git-hooks.sh] (Optional: pre-commit hook for local verification)

---

## 🚀 Next Actions

1. **Team Training** (Immediately after sprint planning):
   - Review Definition of Done
   - Review Requirements & Issues Policy
   - Demo CI/CD workflow
   - Q&A

1. **First Sprint Execution** (Sprint 2026-09):
   - Follow Sprint Lifecycle checklist
   - Developers use commit message format
   - Note any friction points
   - Capture in retrospective

1. **Continuous Improvement** (Every sprint):
   - Sprint retrospective: What worked? What didn't?
   - Update policy/templates as needed
   - Refine automation based on feedback

---

**This Sprint Lifecycle ensures that every piece of work is tied to a requirement, tracked via an issue, verified with tests, and documented for auditability.**
