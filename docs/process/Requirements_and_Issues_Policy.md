# Requirements & Issues Policy

Team agreement for maintaining strict traceability between requirements, issues, and code.

## Core Rules

### Rule 1: No Code Without Issue
- **All code changes** must reference a GitHub/issue tracker item
- Issue must exist **before** development starts (created during sprint planning)
- Commit message must include issue reference
  - **Format**: `Fix D-S08-020: Add trigger_reason field` or `Implements HITL-012: Track conditional gate trigger state`
  - **Tool**: `git commit -m "Fix D-S08-020: ..."`
  - **Verification**: CI/CD script scans commit message; rejects if no issue ID found

**Exception**: Trivial changes (typos in comments, formatting) may skip if commit is <10 lines AND only in non-source files (docs/README)

### Rule 2: No Issue Without Requirement
- **Every sprint issue** must link to at least one requirement
- Requirement ID must appear in issue title, description, or "Related Requirement" section
- Requirement must be traceable to a business/technical need

**Exception**: Infrastructure/tech-debt issues may use label `no-requirement` with TL approval (rare)

### Rule 3: No Requirement Without Issue (For Sprint Work)
- **Sprint requirements** (assigned to active sprint) must have linked issue
- Future/backlog requirements may exist without issue (queued for future sprint)
- When requirement moves from backlog → sprint, issue **must** be created simultaneously

### Rule 4: Sprint Closure Gate
- **Before sprint ends**, traceability matrix must be 100% complete:
  - Every issue → requirement ✅
  - Every requirement → issue ✅
  - Every issue → test file ✅
  - Every test → passing ✅

- Technical Lead **signs off** on matrix completeness
- Missing traceability = sprint **cannot close** until resolved

### Rule 5: Verification Evidence Required
- **Every resolved issue** must have verification evidence:
  - Test output (screenshot/log showing PASS)
  - Screenshot of feature working
  - Link to CI/CD test run
  - Video walkthrough (for complex UI changes)

---

## Enforcement Points

### Sprint Planning
- **Backlog refinement**: Reject story/task that lacks clear requirement
- **Sprint commitment**: Reject assignment of issue without traceability matrix entry
- **Checklist**: Use "Sprint Planning Checklist" to ensure all accepted items have req+issue

### Code Review (Pull Request)
- **Pre-merge check**: PR fails CI if:
  - Commit message lacks issue ID
  - Linked issue has no requirement
  - Issue has no test file referenced
- **Manual review**: Code reviewer verifies:
  - Issue title references requirement ID
  - Implementation matches requirement AC
  - Tests are comprehensive

### Issue Closure
- **PR merge requirement**: Cannot close issue without merged PR
- **Evidence requirement**: Cannot close without verification evidence attached
- **Traceability requirement**: Closing issue must update Traceability Matrix

### Sprint Review
- **Closure gate**: Cannot mark sprint complete without TL sign-off on matrix
- **Audit**: Spot-check 3-5 issues to verify:
  - Requirement exists and is implemented
  - Tests are passing
  - Evidence is present

---

## Workflow Example

```
1. Requirements Sprint Planning
   - PO selects backlog items and grooms requirements
   - Creates/updates requirement files in Requirements/
   - Each requirement gets clear ID (e.g., HITL-012)

2. Sprint Planning
   - Team picks accepted requirements
   - For EACH requirement: Create issue
   - Issue title: "[SPRINT] HITL-012: Implement Conditional Gate State Reporting"
   - Issue desc: "Related Requirement: HITL-012"
   - Add to Traceability Matrix

3. Sprint Execution
   - Dev branches from issue ID: `git checkout -b HITL-012/trigger-state-tracking`
   - Commits reference issue: `git commit -m "Implements HITL-012: Add triggered field"`
   - CI/CD enforces commit message format
   - Tests written alongside code

4. Code Review
   - Reviewer checks:
     ✅ Issue ID in commit message
     ✅ Issue has requirement link
     ✅ Tests passing
     ✅ Verification evidence attached
   - Approves PR

5. Issue Closure
   - PR merged → issue auto-closes (or manual close with checklist)
   - Update Traceability Matrix: status = "Completed"
   - Requirement marked as "Implemented"

6. Sprint Review
   - TL audits Traceability Matrix
   - Verifies 100% of issues closed with evidence
   - Signs off on sprint
   - All traceability artifacts archived
```

---

## Tools & Automation

### CI/CD Enforcement (GitHub Actions)
- **Workflow**: `.github/workflows/sprint-traceability.yml`
- **Trigger**: On pull request, on push to main
- **Check**: Runs `scripts/verify-sprint-traceability.py`
- **Action**:
  - ✅ PASS: Green check, PR allowed to merge
  - ❌ FAIL: Red check, PR blocked with detailed error message
  - ⚠️ WARN: Yellow, advice but not blocking

### Pre-Commit Hook (Optional)
- **Hook**: `scripts/git-hooks/pre-commit-traceability.sh`
- **Trigger**: Before local commit
- **Check**:
  - Warns if commit message lacks issue ID
  - Suggests issue format
  - Can skip with `--no-verify` if needed
- **Setup**: Run `scripts/setup-git-hooks.sh` to install

### Sprint Verification Script
- **Script**: `scripts/verify-sprint-traceability.py`
- **Run**: `python scripts/verify-sprint-traceability.py --sprint 2026-08`
- **Output**:
  - Requirement → Issue mapping report
  - Orphan issues (no requirement)
  - Orphan requirements (no issue)
  - Missing tests
  - Failing tests
- **Audit mode**: `--sprint 2026-08 --audit` runs full closure checklist

---

## Roles & Responsibilities

| Role | Responsibility |
|------|---|
| **Product Owner** | Groom and create requirements with clear IDs |
| **Technical Lead** | Enforce DoD, review traceability matrix, sign off sprint closure |
| **Developer** | Write code with issue references, create tests, provide evidence |
| **Code Reviewer** | Verify traceability in PR, check tests, review evidence |
| **QA/Tester** | Validate verification evidence, run regression suite |

---

## Exceptions & Waivers

Not every task fits perfectly:

- **Infrastructure work**: May lack direct requirement; use `no-requirement` label + TL approval
- **Bug fixes**: May reference issue that's NOT a requirement; link to root cause analysis instead
- **Documentation**: May be requirement-driven OR issue-driven; document which

**Process for waiver**:
1. Document reason in issue
2. Add label `dod-waiver:<criterion>`
3. Get Technical Lead approval
4. Note in Traceability Matrix "Notes" column
5. Add to sprint retrospective for future process improvement

---

## Updates & Continuous Improvement

This policy is reviewed at **end of each sprint** (Sprint Retrospective):

- What worked? What didn't?
- Do we need tighter enforcement?
- Do rules make sense?
- Update policy if needed
- Update automation/scripts based on feedback

**Last Updated**: May 8, 2026 (Initial creation)

