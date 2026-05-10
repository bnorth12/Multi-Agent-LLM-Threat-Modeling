# Sprint Governance & Traceability Framework

**Created**: May 8, 2026
**Status**: ✅ **Ready to Deploy**
**Applies To**: All future sprints (2026-09 onwards)

---

## 🎯 What This Framework Does

Enforces **bidirectional traceability** between Requirements, Issues, Code, and Tests:

```
Requirement (HITL-012)
    ↕ (bidirectional link)
Issue (D-S08-020)
    ↕ (linked in commit message)
Code (src/threat_modeler/hitl/models.py)
    ↕ (referenced in issue)
Tests (Tests/unit/test_hitl_gate_trigger_state.py)
    ↕ (test file linked in issue)
Verification Evidence (test pass screenshot, CI/CD run)
```

**Why This Matters**:
- ✅ Every requirement is implemented (nothing forgotten)
- ✅ Every code change is tied to a requirement (no "orphan" code)
- ✅ Every feature is tested (verification evidence collected)
- ✅ Everything is auditable (full trace for compliance/review)

---

## 📋 Files Created

### 1. Core Governance Documents

| File | Purpose | When to Read |
|------|---------|---|
| [docs/process/Definition_of_Done.md](docs/process/Definition_of_Done.md) | DoD checklist; what every work item must satisfy | Sprint start (team review) |
| [docs/process/Requirements_and_Issues_Policy.md](docs/process/Requirements_and_Issues_Policy.md) | Team agreement on traceability rules | Sprint start + policy questions |
| [docs/process/Sprint_Lifecycle_and_Automated_Governance.md](docs/process/Sprint_Lifecycle_and_Automated_Governance.md) | Complete sprint walkthrough with automation points | During sprint execution |
| [docs/process/Governance_and_Traceability_Index.md](docs/process/Governance_and_Traceability_Index.md) | Central index & quick-start guide | Daily reference |

### 2. Sprint Templates & Checklists

| File | Purpose | Usage |
|------|---------|-------|
| [planning/Sprint_Planning_Checklist_Template.md](planning/Sprint_Planning_Checklist_Template.md) | Copy per sprint for Day 0 planning | Copy → `planning/Sprint_2026_09_Planning_Checklist.md` |
| [planning/Sprint_Traceability_Matrix_Template.md](planning/Sprint_Traceability_Matrix_Template.md) | Copy per sprint; single source of truth | Copy → `planning/Sprint_2026_09_Traceability_Matrix.md` |
| [planning/Sprint_2026_09_Closure_Checklist.md](planning/Sprint_2026_09_Closure_Checklist.md) | Example closure checklist (for reference) | Copy per sprint → `planning/Sprint_2026_10_Closure_Checklist.md` |

### 3. Automation & Tooling

| File | Purpose | How It Works |
|------|---------|---|
| [scripts/verify_sprint_traceability.py](scripts/verify_sprint_traceability.py) | Verifies requirements → issues → tests bidirectional traceability | Run manually: `python scripts/verify_sprint_traceability.py --sprint 2026-09` |
| [.github/workflows/sprint-traceability.yml](.github/workflows/sprint-traceability.yml) | GitHub Actions CI/CD; blocks PRs without issue refs | Runs automatically on every PR |
| [scripts/setup_git_hooks.sh](scripts/setup_git_hooks.sh) | Optional pre-commit hook for local verification | Run once: `bash scripts/setup_git_hooks.sh` |

---

## 🚀 Deployment Checklist

Follow this to deploy the framework for your next sprint:

### Pre-Sprint (1-2 Days Before)

- [ ] 1. **Review this README** (you are here!)
- [ ] 2. **Read Governance Index**: [docs/process/Governance_and_Traceability_Index.md](docs/process/Governance_and_Traceability_Index.md)
  - Understand the framework architecture
  - Identify roles (PO, Tech Lead, Dev, Reviewer)
- [ ] 3. **Read Definition of Done**: [docs/process/Definition_of_Done.md](docs/process/Definition_of_Done.md)
  - Understand mandatory completion criteria
  - Identify any waivers upfront
- [ ] 4. **Read Requirements & Issues Policy**: [docs/process/Requirements_and_Issues_Policy.md](docs/process/Requirements_and_Issues_Policy.md)
  - Understand the 5 core rules
  - Understand enforcement points

### Sprint Planning Day (Day 0)

- [ ] 5. **Groom Backlog** (PO)
   - Create requirements with IDs (HITL-012, PRJ-008, etc.)
   - Write to Requirements/ folder
   - Ensure AC are clear and testable

- [ ] 6. **Accept Sprint Items** (Team)
   - Commit to backlog items for this sprint
   - Determine capacity/velocity

- [ ] 7. **Create Issues** (Team)
   - For each requirement: Create GitHub issue
   - Issue title format: `[SPRINT] <REQ_ID>: <description>`
   - Link requirement in issue description

- [ ] 8. **Set Up Traceability Matrix** (Scrum Master / Tech Lead)
   ```bash
   cp planning/Sprint_Traceability_Matrix_Template.md \
      planning/Sprint_2026_09_Traceability_Matrix.md
   ```
   - Update header (sprint dates)
   - Add all requirement rows
   - Add to version control

- [ ] 9. **Create Planning Checklist** (Scrum Master / Tech Lead)
   ```bash
   cp planning/Sprint_Planning_Checklist_Template.md \
      planning/Sprint_2026_09_Planning_Checklist.md
   ```
   - Update sprint number
   - Complete all sections
   - Get team signatures

- [ ] 10. **Create Closure Checklist** (Scrum Master / Tech Lead)
   ```bash
   cp planning/Sprint_2026_09_Closure_Checklist.md \
      planning/Sprint_2026_09_Closure_Checklist.md
   ```
   - For use on Day 10 (keep on hand)

- [ ] 11. **Team Onboarding** (Tech Lead)
   - Review Definition of Done with team (10 min)
   - Demo commit message format: `git commit -m "Implements HITL-012: ..."`
   - Demo CI/CD workflow (show example PR)
   - Answer questions

- [ ] 12. **Optional: Setup Git Hooks** (Each Developer)
   ```bash
   bash scripts/setup_git_hooks.sh
   ```
   - Provides local pre-commit warning (optional)
   - Helps catch issue refs before push

### During Sprint (Days 1-9)

- [ ] 13. **Developer Workflow** (Every developer, on each task)
   - Create branch: `git checkout -b HITL-012/trigger-tracking`
   - Write code + tests together
   - Commit with issue ref: `git commit -m "Implements HITL-012: ..."`
   - Tests pass locally: `pytest Tests/ -v`
   - Push & create PR
   - **CI/CD runs automatically** ✅ (no manual action)
   - Wait for green ✅ check
   - Request code review

- [ ] 14. **Code Review** (Every reviewer)
   - Verify commit messages reference issue IDs
   - Verify issue links to requirement
   - Verify tests exist and cover AC
   - Verify CI/CD checks passing
   - Approve or request changes

- [ ] 15. **Mid-Sprint Verification** (Tech Lead, Day 3-4)
   ```bash
   python scripts/verify_sprint_traceability.py --sprint 2026-09
   ```
   - Run verification script
   - Review output for any ❌ FAIL items
   - Address gaps immediately
   - Report status in standup

- [ ] 16. **Daily Standup** (Everyone, every day)
   - Update issue status
   - Mention traceability status (CI/CD green? tests passing?)
   - Call out blockers

### Sprint Closure Day (Day 10)

- [ ] 17. **Final Verification** (Tech Lead, morning)
   ```bash
   python scripts/verify_sprint_traceability.py --sprint 2026-09 --audit
   ```
   - Run audit mode
   - Verify 0 orphans, all tests ✅
   - Verify all issues closed or deferred

- [ ] 18. **Evidence Collection** (Tech Lead, morning-afternoon)
   - Collect test results (screenshot/log)
   - Collect UI change screenshots (if applicable)
   - Collect deployment evidence (if applicable)
   - Archive to: `planning/archives/sprint_2026_09_evidence/`

- [ ] 19. **Complete Closure Checklist** (Tech Lead, afternoon)
   - Complete `planning/Sprint_2026_09_Closure_Checklist.md`
   - All sections: ✅
   - Technical Lead signature: ✅

- [ ] 20. **Archive Sprint Artifacts** (Scrum Master)
   ```bash
   mv planning/Sprint_2026_09_Traceability_Matrix.md \
      planning/archives/Sprint_2026_09_Traceability_Matrix_FINAL.md
   git add planning/archives/
   git commit -m "Archive Sprint 2026-09 artifacts"
   ```

- [ ] 21. **Retrospective** (Team, post-standup)
   - What worked? What didn't?
   - Update governance docs if needed
   - Lessons captured in: `planning/Sprint_2026_09_Retrospective.md`

- [ ] 22. **Handoff to Next Sprint** (Scrum Master)
   - Prepare templates for Sprint 2026-10
   - Archive Sprint 2026-09 docs
   - Commit & push

---

## 📊 Metrics & Success Criteria

Track these to ensure framework is working:

| Metric | Target | How to Measure |
|--------|--------|---|
| Requirement → Issue Coverage | 100% | `verify_sprint_traceability.py` output |
| Issue → Requirement Coverage | 100% | Same |
| Issue → Test File Coverage | 100% | Same |
| Orphan Requirements | 0 | Same |
| Orphan Issues | 0 | Same |
| Test Pass Rate | >95% | `pytest Tests/ -v` |
| CI/CD Green Gate Rate | 100% | PR merge success rate |
| DoD Compliance | 100% | Closure checklist completion |
| Commit Message Compliance | 100% | Commits with issue IDs |

**Success = all metrics ✅**

---

## 🔄 Automation Flow Diagram

```
Developer Commits Code
    ↓
"git commit -m 'Implements HITL-012: ...'"
    ↓
[Optional] Pre-commit hook warns if issue ID missing
    ↓
"git push origin branch"
    ↓
PR Created on GitHub
    ↓
GitHub Actions CI/CD (AUTOMATIC) ⚙️
├─ Verify commit message has issue ID ✅
├─ Verify issue links to requirement ✅
├─ Verify test file referenced ✅
└─ Result: GREEN ✅ or RED ❌
    ↓
If ❌ FAIL:
├─ PR blocked
├─ Error message shown
└─ Developer fixes + repushes
    ↓
If ✅ PASS:
├─ PR approved for code review
├─ Developer requests review
└─ Reviewer checks traceability too
    ↓
If code review ✅ APPROVED:
    ↓
Merge PR
    ↓
Issue auto-closes (if configured)
    ↓
Update Traceability Matrix
    ↓
On Sprint Day 10:
├─ Run "verify_sprint_traceability.py --audit"
├─ Complete Closure Checklist
├─ Tech Lead signs off
└─ Sprint CLOSED ✅
```

---

## 🎓 Examples

### Example 1: Good Workflow (Requirement → Issue → Code → Test)

```
Step 1: Requirement Created
  File: Requirements/HITL-012_Conditional_Gate_State_Tracking.md
  Content: ID=HITL-012, Name="Conditional Gate State Tracking", AC=[...], Related Issue: D-S08-020

Step 2: Issue Created
  Title: "[SPRINT] HITL-012: Implement Conditional Gate State Tracking"
  Description: "Requirement: HITL-012\n\nTest File: Tests/unit/test_hitl_gate_trigger_state.py"

Step 3: Matrix Entry Added
  | 1 | HITL-012 | Conditional Gate State Tracking | D-S08-020 | Open | Jane | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending |

Step 4: Development
  Jane: git checkout -b HITL-012/trigger-state-tracking
  Jane: Write code in src/threat_modeler/hitl/models.py
  Jane: Write tests in Tests/unit/test_hitl_gate_trigger_state.py
  Jane: Tests pass locally ✅

Step 5: Commit
  Jane: git commit -m "Implements HITL-012: Add triggered and trigger_reason fields
                        - Add triggered: bool = False field
                        - Add trigger_reason: str | None = None field
                        - All tests passing"
  ✅ Commit has "HITL-012" → Good

Step 6: Push & PR
  Jane: git push origin HITL-012/trigger-state-tracking
  Jane: Create PR (title: "[SPRINT] HITL-012: Implement Conditional Gate State Tracking")

Step 7: CI/CD Verification (AUTOMATIC)
  GitHub Actions runs:
  ✅ Commit message has "HITL-012" → PASS
  ✅ Issue title has "HITL-012" → PASS
  ✅ Issue description has "Tests/unit/" → PASS
  Result: 🟢 GREEN ✅

Step 8: Code Review
  Bob: Checks PR
  ✅ Commit message good
  ✅ Issue links to requirement
  ✅ Implementation matches AC
  ✅ Tests comprehensive
  Bob: APPROVE

Step 9: Merge
  Jane: Merge PR
  Issue: Auto-closes (with evidence)

Step 10: Matrix Update
  Tech Lead: Updates matrix
  Status: ✅ PASS
  Evidence: Link to PR #123, test output screenshot

Result: HITL-012 ✅ Fully Traceable → Requirement → Issue → Code → Tests → Verified
```

### Example 2: What Gets Blocked (Bad Workflow)

```
Bad Commit Message
  Jane: git commit -m "Fix bug in models.py"
  ❌ No issue reference
  CI/CD blocks PR: RED ❌
  Error: "Commit message must reference issue ID (e.g., D-S08-020)"

  Fix: git commit --amend -m "Implements HITL-012: Fix bug in models.py"
  Repush: git push --force
  CI/CD: ✅ GREEN (now passes)

Issue Has No Requirement
  Jane: Creates issue without linking requirement
  CI/CD: Runs verification script
  Output: "❌ FAIL: Issue D-S08-020 has no requirement link"
  PR blocked: RED ❌

  Fix: Edit issue, add "Requirement: HITL-012" to description
  CI/CD re-runs: ✅ GREEN (now passes)

Missing Test File
  Jane: Writes code but no test file
  Issue: No test file mentioned
  CI/CD: Warns ⚠️ WARN (non-blocking)
  Reviewer: Sees warning, asks for tests
  Jane: Creates test file, commits: "Add tests for HITL-012"
  PR: ✅ PASS
```

---

## ❓ FAQ

### Q: Is this framework mandatory?
**A**: Yes, for all sprints starting with 2026-09. It ensures every requirement is implemented, tested, and traceable.

### Q: What if I forget the issue ID in my commit message?
**A**:
- Pre-commit hook (optional): Warns locally (non-blocking)
- CI/CD (automatic): Blocks PR merge until fixed
- Fix: `git commit --amend -m "Implements HITL-012: ..."` then `git push --force`

### Q: Can I bypass the traceability checks?
**A**: Yes, with Technical Lead approval:
- Add `dod-waiver:commit-message` label to issue
- Document reason in issue description
- TL approves waiver
- Note in Traceability Matrix
- Usually not needed; DO NOT make a habit of it

### Q: How often should I run the verification script?
**A**:
- Mid-sprint (Day 3-4): Catch gaps early
- Pre-closure (Day 10): Ensure 100% before sign-off
- Optional: Anytime during sprint to spot-check

### Q: What if a requirement doesn't need an issue?
**A**: It still needs one if it's in the active sprint. Backlog requirements can exist without issues. Once moved to sprint → must create issue.

### Q: Can CI/CD ever be bypassed?
**A**: No. CI/CD checks are non-waivable gates. If commit message lacks issue ID, PR cannot merge. This is by design to enforce traceability.

### Q: What happens at sprint closure?
**A**:
- Run audit script: `verify_sprint_traceability.py --sprint 2026-09 --audit`
- Complete Closure Checklist
- Get TL signature (non-waivable)
- Archive all artifacts
- Mark sprint CLOSED

---

## 🔗 Quick Links

- 📄 **Governance Index** (start here): [docs/process/Governance_and_Traceability_Index.md](docs/process/Governance_and_Traceability_Index.md)
- 📋 **Definition of Done**: [docs/process/Definition_of_Done.md](docs/process/Definition_of_Done.md)
- 📋 **Requirements & Issues Policy**: [docs/process/Requirements_and_Issues_Policy.md](docs/process/Requirements_and_Issues_Policy.md)
- 📋 **Sprint Lifecycle**: [docs/process/Sprint_Lifecycle_and_Automated_Governance.md](docs/process/Sprint_Lifecycle_and_Automated_Governance.md)
- 🐍 **Verification Script**: [scripts/verify_sprint_traceability.py](scripts/verify_sprint_traceability.py)
- ⚙️ **CI/CD Workflow**: [.github/workflows/sprint-traceability.yml](.github/workflows/sprint-traceability.yml)

---

## 📞 Support

**Questions?**
- Read: [docs/process/Requirements_and_Issues_Policy.md](docs/process/Requirements_and_Issues_Policy.md) → Exceptions & Waivers section
- Ask: Technical Lead

**CI/CD Failing?**
- Check: Commit message has issue ID
- Check: Issue links to requirement
- Check: Issue mentions test file
- Run locally: `python scripts/verify_sprint_traceability.py --sprint 2026-09`

**Process Improvements?**
- Suggest in Sprint Retrospective
- Update docs + templates as needed
- Commit changes with: `git commit -m "Update governance docs based on retrospective feedback"`

---

## ✅ Deployment Status

- [x] Definition of Done created
- [x] Requirements & Issues Policy created
- [x] Sprint Lifecycle guide created
- [x] Governance Index created
- [x] Planning Checklist template created
- [x] Traceability Matrix template created
- [x] Closure Checklist template created
- [x] Verification script created
- [x] CI/CD workflow created
- [x] Git hooks setup script created
- [x] This README created

**Status**: 🟢 **READY TO DEPLOY FOR SPRINT 2026-09**

---

**Created**: May 8, 2026
**Author**: Technical Leadership
**Version**: 1.0
**Next Review**: After Sprint 2026-09 Retrospective

