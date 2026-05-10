# Definition of Done (DoD) Checklist

Every sprint task and code change must satisfy **ALL criteria** before marking complete.

## Pre-Implementation

- [ ] **Requirement Identified**: Issue or epic links to requirement ID (e.g., HITL-012, D-S08-020)
  - If new requirement needed, create in `Requirements/` folder first
  - If existing requirement, link by ID in issue title or description
- [ ] **Issue Created**: GitHub/issue tracker item exists with:
  - Title format: `[SPRINT] <REQ_ID>: <work_title>` (e.g., `[SPRINT] HITL-012: Implement Conditional Gate State Reporting`)
  - Clear Acceptance Criteria linked to requirement
  - Related Requirement section populated
- [ ] **Traceability Matrix Updated**: Issue added to `planning/Sprint_YYYY_MM_Traceability_Matrix.md`

## Implementation

- [ ] **Code Changes Complete**: All functionality implemented per acceptance criteria
- [ ] **Issue Referenced in Commits**: All commits reference issue ID
  - Format: `Fix D-S08-020: Add trigger_reason field to HitlGateRecord`
  - Format: `Implements HITL-012: Track conditional gate trigger state`
- [ ] **Code Review**: PR/branch approved with traceability verified

## Testing & Verification

- [ ] **Tests Written**: Unit/integration tests added for new functionality
  - New test file or substantial additions to existing test
  - Tests cover both happy path and error cases
- [ ] **Tests Pass**:
  - All new tests passing
  - No regressions (full test suite passes)
  - Coverage reported in commit message or PR
- [ ] **Verification Evidence Attached**:
  - Test output showing pass count
  - Screenshot or artifact proving feature works
  - Link to test results or CI/CD run

## Closure & Documentation

- [ ] **Issue Closed**: Issue marked as Resolved/Completed with:
  - Summary of implementation
  - Link to merged commit/PR
  - Verification evidence referenced
- [ ] **Traceability Matrix Updated**:
  - Issue marked as "Completed"
  - Test file linked
  - Verification status = ✅ PASS
- [ ] **Requirement Updated** (if applicable):
  - Requirement file updated with implementation issue link
  - Verification method documented
  - Mark as "Implemented"

---

## Waiver Process

If a criterion cannot be satisfied:

1. Document **why** in issue description
2. Add **label** `dod-waiver:<criterion>` (e.g., `dod-waiver:requirement-identified`)
3. Get **Technical Lead approval** before merge
4. Add **waiver note** to Traceability Matrix in "Notes" column

Example: "⚠️ No new test (existing suite covers case); Technical Lead approved D-S08-019"

---

## Automated Enforcement

- CI/CD pipeline runs `scripts/verify-sprint-traceability.py` on PR
- Rejects PR if:
  - Issue ID missing from commit message
  - Requirement link missing from issue
  - Test file not referenced in code
  - Traceability Matrix not updated

- Pre-commit hook runs locally (optional but recommended):
  - Warns if commit message lacks issue reference
  - Blocks if branch has no issue tracking

