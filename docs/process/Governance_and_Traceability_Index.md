# Governance & Traceability Process Index

**Purpose**: Central reference for all requirements-driven development governance, process automation, and sprint lifecycle management.

**This is the single source of truth for how we execute sprints with enforced traceability.**

**Last Updated**: May 8, 2026
**Version**: 1.0
**Applies to**: All future sprints (2026-09 onwards)

---

## 📚 Core Governance Documents

These documents define how requirements flow into code with full traceability:

### 1. **Definition of Done**
   📄 [docs/process/Definition_of_Done.md](../docs/process/Definition_of_Done.md)

   **What**: Mandatory checklist every work item must satisfy before closure

   **Criteria**:
   - Requirement identified (REQ ID)
   - Issue created (linked to requirement)
   - Code committed (references issue in commit message)
   - Tests written and passing
   - Verification evidence attached
   - Traceability matrix updated

   **When to Use**:
   - Team onboarding (sprint start)
   - Code review (before approval)
   - Issue closure (before marking done)
   - Sprint retrospective (process improvement)

   **Waiver Process**: Document waiver reason, get Technical Lead approval, note in Traceability Matrix

---

### 2. **Requirements & Issues Policy**
   📄 [docs/process/Requirements_and_Issues_Policy.md](../docs/process/Requirements_and_Issues_Policy.md)

   **What**: Team agreement on traceability rules and enforcement

   **Key Rules**:
   - Rule 1: No code without issue
   - Rule 2: No issue without requirement
   - Rule 3: No sprint requirement without issue
   - Rule 4: Sprint closure gate (100% traceability)
   - Rule 5: Verification evidence required

   **Enforcement Points**:
   - Sprint planning: Reject story without requirement
   - Code review: Reject PR without issue reference in commits
   - Issue closure: Reject without test evidence
   - Sprint closure: Block until traceability matrix signed off

   **Roles**:
   - PO: Groom requirements, create IDs, ensure clarity
   - Tech Lead: Enforce DoD, sign off traceability matrix
   - Developer: Write code with issue refs, create tests, provide evidence
   - Code Reviewer: Verify traceability in PR

   **When to Use**:
   - Policy questions during sprint
   - Waivers or exceptions
   - Process disputes
   - Update after retrospective

---

## 🔄 Sprint Lifecycle

Complete walkthrough of how traceability is maintained throughout a sprint:

### 3. **Sprint Lifecycle & Automated Governance**
   📄 [docs/process/Sprint_Lifecycle_and_Automated_Governance.md](../docs/process/Sprint_Lifecycle_and_Automated_Governance.md)

   **What**: End-to-end sprint playbook with automation points

   **Phases**:
   - **Planning Phase** (Day 0)
     - 1a. Requirement grooming → Requirements/ folder
     - 1b. Issue creation → planning/issues/
     - 1c. Traceability matrix setup → planning/Sprint_YYYY_MM_Traceability_Matrix.md
     - 1d. Team onboarding → Definition of Done reviewed

   - **Execution Phase** (Days 1-9)
     - 2a. Daily development → Commits reference issues
     - 2b. Automated CI/CD verification → GitHub Actions checks (blocking)
     - 2c. Code review → Peer traceability verification
     - 2d. Mid-sprint verification (Day 3-4) → Run verify script
     - 2e. Daily standup → 1-min traceability update

   - **Closure Phase** (Day 10)
     - 3a. Final verification → Audit mode script
     - 3b. Evidence collection → Archive artifacts
     - 3c. Closure checklist → TL sign-off
     - 3d. Retrospective → Lessons learned
     - 3e. Handoff to next sprint → Template prep

   **When to Use**: Reference during sprint execution; follow step-by-step

---

## 📋 Sprint Templates & Checklists

Ready-to-use documents for each sprint:

### 4. **Sprint Planning Checklist Template**
   📄 [planning/Sprint_Planning_Checklist_Template.md](./Sprint_Planning_Checklist_Template.md)

   **What**: Checklist for sprint start (Day 0); ensures traceability setup

   **Sections**:
   - Pre-planning (1-2 days before)
   - Requirement acceptance & grooming
   - Issue creation & linking
   - Traceability matrix setup
   - Team onboarding
   - Governance doc review
   - Sign-off

   **Usage**:
   1. Copy template: `cp planning/Sprint_Planning_Checklist_Template.md planning/Sprint_2026_09_Planning_Checklist.md`
   2. Update sprint number (2026-09)
   3. Sprint Lead completes checklist during planning day
   4. Get team sign-off
   5. Archive in planning/Sprint_2026_09/ folder

   **When to Use**: Sprint start day (Day 0)

---

### 5. **Traceability Matrix Template**
   📄 [planning/Sprint_Traceability_Matrix_Template.md](./Sprint_Traceability_Matrix_Template.md)

   **What**: Single source of truth for sprint requirements → issues → code → tests

   **Columns**:
   - # (row number)
   - Requirement ID (e.g., HITL-012)
   - Requirement Name
   - Issue ID (e.g., D-S08-020)
   - Issue Status (Open → In Progress → Merged → Completed)
   - Assigned To (owner)
   - Test File (e.g., Tests/unit/test_hitl_*.py)
   - Verification Status (⏳ Pending → 🔄 In Dev → 🧪 Testing → ✅ PASS or ❌ FAIL)
   - Notes

   **Status Legend**:
   - Issue Status: Open, In Progress, In Review, Merged, Completed
   - Verification Status: ⏳ Pending, 🔄 In Dev, 🧪 Testing, ✅ PASS, ❌ FAIL, ⚠️ Manual Test

   **Updates**:
   - Sprint start: Populate all rows from backlog
   - Mid-sprint (Day 3-4): Update status and verification columns
   - Daily: Optional, update as issues change state
   - Sprint end: Mark all as ✅ or carryover

   **Usage**:
   1. Copy template: `cp planning/Sprint_Traceability_Matrix_Template.md planning/Sprint_2026_09_Traceability_Matrix.md`
   2. Update header (sprint dates)
   3. Add requirement rows from sprint backlog
   4. Add to version control & link from sprint plan
   5. Update throughout sprint

   **When to Use**: Sprint planning (Day 0), throughout execution, closure

---

### 6. **Sprint Closure Checklist**
   📄 [planning/Sprint_2026_09_Closure_Checklist.md](./Sprint_2026_09_Closure_Checklist.md)

   **What**: Formal checklist for sprint end; gates closure on 100% traceability

   **Sections**:
   - ✅ Traceability Matrix Complete (verify 0 orphans)
   - ✅ Issue Status Verified (all closed or deferred)
   - ✅ Test Evidence Complete (tests passing, evidence collected)
   - ✅ Requirement Sync Complete (requirements updated if needed)
   - ✅ Code Quality Gates (linting, no TODOs)
   - ✅ Documentation Updated
   - ✅ Artifacts Collected (archive to planning/archives/)
   - ✅ Sign-Off & Approval (TL signature required)

   **Usage**:
   1. Copy template: `cp planning/Sprint_YYYY_MM_Closure_Checklist.md planning/Sprint_2026_09_Closure_Checklist.md`
   2. Complete all sections during sprint end day
   3. Get Technical Lead signature (non-waivable)
   4. Archive final artifacts
   5. Mark sprint as CLOSED

   **When to Use**: Sprint end day (Day 10, afternoon)

---

## 🤖 Automation & Tooling

Scripts and workflows that automatically enforce traceability:

### 7. **Verification Script**
   🐍 [scripts/verify_sprint_traceability.py](../scripts/verify_sprint_traceability.py)

   **What**: Python script that audits traceability matrix completeness

   **Checks**:
   - Every requirement has linked issue
   - Every issue has linked requirement
   - No orphan requirements
   - No orphan issues
   - All test files referenced
   - All tests passing (optional)

   **Usage**:
   ```bash
   # Mid-sprint check
   python scripts/verify_sprint_traceability.py --sprint 2026-09

   # Full audit (before closure)
   python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit

   # Output: Colored terminal report showing ✅ PASS or ❌ FAIL
   ```

   **When to Run**:
   - Mid-sprint (Day 3-4): Identify gaps early
   - Pre-closure (Day 10): Ensure 100% before sign-off
   - Any time during sprint: Spot-check compliance

   **Output Interpretation**:
   - Green ✅: Traceability complete for that item
   - Red ❌: Blocker found (must fix before closure)
   - Yellow ⚠️: Warning (non-blocking but should address)

---

### 8. **GitHub Actions CI/CD Workflow**
   ⚙️ [.github/workflows/sprint-traceability.yml](../.github/workflows/sprint-traceability.yml)

   **What**: Automated CI/CD pipeline that blocks PRs without proper traceability

   **Triggers**: On every PR creation and push to main

   **Checks** (AUTOMATIC):
   - ✅ Commit message verification (has issue ID?)
   - ✅ Issue → Requirement link (issue references requirement?)
   - ✅ Test file reference (issue mentions test file?)
   - ✅ Code change traceability (code changes referenced?)

   **Result**:
   - ✅ PASS (green): PR can proceed to review
   - ❌ FAIL (red): PR blocked, cannot merge

   **How It Works**:
   1. Developer commits: `git commit -m "Implements HITL-012: ..."` (includes issue ref)
   2. Developer pushes: `git push origin branch-name`
   3. Developer creates PR on GitHub
   4. GitHub Actions AUTOMATICALLY runs sprint-traceability.yml
   5. Workflow checks commit message for "HITL-012" or similar issue ID

---

## 🧾 Resolution Records

### 9. **Runtime State and Gate Contract Resolution (2026-05)**
   📄 [docs/process/Runtime_State_And_Gate_Contract_Resolution_2026_05.md](../docs/process/Runtime_State_And_Gate_Contract_Resolution_2026_05.md)

   **What**: Formal resolution record for Gate 0 readiness sequencing, terminal cancelled-state behavior, UI status precedence, and requirement/issue synchronization.

   **Links**:
   - Requirement set: `Requirements/13_Runtime_State_And_Input_Contract_Requirements.md`
   - Issue record: `planning/issues/issue_2026_13_D_S13_022_Run_State_And_Gate_Contract_Corrections.md`

   **When to Use**:
   - Reviewing cancellation and Gate 0 behavior corrections
   - Verifying traceability package completeness for this defect cluster
   - Preparing sprint closeout evidence and governance sign-off
   6. Workflow runs verification script to check requirement link
   7. Workflow checks for test file in issue description
   8. Result: Green ✅ or Red ❌ shown in PR
   9. Reviewer cannot approve until checks pass
   10. Cannot merge until CI/CD checks pass

   **What Happens on Failure**:
   - Red ❌ check appears in PR
   - Comment added to PR with specific error
   - Developer must fix issue before resubmitting
   - Common fixes: Update commit message, link requirement, add test file

   **When It Runs**: Automatically on every PR (no manual trigger needed)

---

## 🔧 How to Use This Framework

### For Sprint Leads / Scrum Masters

**Sprint Start**:
1. Review this index: "Got it, we follow this governance framework"
2. Copy `Sprint_Planning_Checklist_Template.md` → `Sprint_2026_09_Planning_Checklist.md`
3. Copy `Sprint_Traceability_Matrix_Template.md` → `Sprint_2026_09_Traceability_Matrix.md`
4. Follow Sprint Lifecycle section, Phase 1 (Planning)
5. Get team signed off on checklist

**Execution**:
6. Share Definition of Done + Requirements & Issues Policy with team
7. Ensure team knows commit message format
8. Mid-sprint (Day 3-4): Run verification script
9. Track Traceability Matrix daily/weekly

**Closure**:
10. Copy `Sprint_Closure_Checklist.md` for your sprint
11. Run verification script in audit mode
12. Complete closure checklist
13. Get Technical Lead signature
14. Archive sprint artifacts

---

### For Developers

**Before Starting Work**:
1. Issue created? Does it link to requirement? ✅
2. Understand requirement AC? ✅
3. Know test file path? ✅

**During Development**:
4. Create feature branch: `git checkout -b ISSUE-ID/description`
5. Write code + tests together
6. Commit with issue reference: `git commit -m "Implements HITL-012: ..."`
7. Tests passing locally? ✅
8. Push to remote: `git push origin branch`
9. Create PR on GitHub
10. Wait for CI/CD ✅ green check (automatic)
11. Request code review

**Before Merging**:
12. Code review complete? ✅
13. All CI/CD checks green? ✅
14. Evidence added to issue? ✅

**After Merge**:
15. Update Traceability Matrix (or ask Tech Lead)
16. Mark issue as done

---

### For Code Reviewers

**Before Approving**:
1. [ ] Commit messages reference issue ID
2. [ ] Issue links to requirement
3. [ ] Implementation matches requirement AC
4. [ ] Tests exist and cover AC
5. [ ] All CI/CD checks passing
6. [ ] Evidence present in issue

**Comment Template**:
```markdown
✅ Traceability verified:
- Commits reference D-S08-020
- Issue links to HITL-012
- Tests in Tests/unit/test_hitl_*.py
- Implementation matches AC
- CI/CD checks passing

Code review: [approve/request changes/comment]
```

---

### For Technical Leads

**Mid-Sprint**:
1. Run verification script: `python scripts/verify_sprint_traceability.py --sprint 2026-09`
2. Review output; address any RED ❌ items immediately
3. Update team on traceability health in standup

**Sprint Closure**:
4. Run audit script: `python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit`
5. Complete closure checklist
6. Verify 0 orphans, all tests ✅
7. Sign off on traceability matrix
8. Mark sprint CLOSED
9. Archive all artifacts

---

## 📊 Metrics & Reporting

Track these metrics to measure traceability health:

| Metric | Target | Check How | Sprint 2026-08 | Sprint 2026-09 |
|--------|--------|-----------|---|---|
| Requirement → Issue Coverage | 100% | `verify_sprint_traceability.py` output | 100% (4/4) | See current sprint traceability matrix |
| Issue → Requirement Coverage | 100% | Same | 100% (4/4) | See current sprint traceability matrix |
| Issue → Test File Coverage | 100% | Same | Sprint-era example | See current sprint traceability matrix |
| Orphan Requirements | 0 | Same | 0 | See current sprint traceability matrix |
| Orphan Issues | 0 | Same | 0 | See current sprint traceability matrix |
| Test Pass Rate | ≥95% | `pytest Tests/ -v` | 310/310 (100%) | See latest sprint test summary |
| CI/CD Green Gate Rate | 100% | PR merge success | 100% | See latest sprint governance evidence |
| DoD Compliance | 100% | Closure checklist | 100% | See latest sprint closure checklist |

---

## 🔄 Continuous Improvement

After each sprint, update this framework:

**Sprint Retrospective Questions**:
1. Did traceability governance help or hinder?
2. What was difficult about the process?
3. What worked well?
4. Should we update Definition of Done?
5. Should we update Requirements & Issues Policy?
6. Should we improve automation?

**Update Process**:
- [ ] Update policy documents if rules changed
- [ ] Update templates if structure improved
- [ ] Update verification script if checks changed
- [ ] Update CI/CD workflow if new checks needed
- [ ] Document changes in `planning/Sprint_YYYY_MM_Retrospective.md`

**Version Control**:
- All governance documents in `docs/process/`
- All templates in `planning/`
- All automation in `scripts/` and `.github/workflows/`
- Updates committed with message: `Update governance docs based on Sprint 2026-XX retrospective`

---

## ✅ Quick Start Checklist (For New Sprint)

Use this to bootstrap any future sprint:

- [ ] 1. Read this index (30 sec)
- [ ] 2. Copy planning templates to new sprint folder (2 min)
- [ ] 3. Review Definition of Done with team (10 min)
- [ ] 4. Review Requirements & Issues Policy with team (10 min)
- [ ] 5. Demo CI/CD workflow showing example PR (5 min)
- [ ] 6. Groom backlog and create requirements (varies)
- [ ] 7. Create issues (1 per requirement)
- [ ] 8. Populate Traceability Matrix (10 min)
- [ ] 9. Get team sign-off on checklist (5 min)
- [ ] 10. Start sprint execution → follow Sprint Lifecycle Phase 2

**Total Setup Time**: ~45 min

---

## 📞 Questions or Issues?

**Process Questions**: See [Requirements & Issues Policy](../docs/process/Requirements_and_Issues_Policy.md) - "FAQ" section

**Automation Broken**: Check `.github/workflows/sprint-traceability.yml` or run verification script locally

**Update Needed**: Start sprint retrospective discussion; submit feedback to Tech Lead

---

**This framework ensures every piece of sprint work is traceable from requirement → issue → code → tests → verification evidence.**

**Last Updated**: May 8, 2026
**Maintained By**: Technical Leadership
**Review Frequency**: Every sprint (retrospective)

