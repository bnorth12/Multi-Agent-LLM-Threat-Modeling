# Release Candidate Merge Verification Report Template

**Version**: [vX.Y.Z-rcN]
**Merge Date**: [YYYY-MM-DD]
**Branch/PR**: [link or ID]
**Prepared By**: [name]
**Decision**: PASS | CONDITIONAL | FAIL

---

## 1. Scope

- Candidate version and merge target
- Included requirement sets
- Included traceability artifacts

---

## 2. Requirement Coverage and Artifact Backing

| Requirement ID | Requirement Type | Primary Verification Artifact | Supporting Artifacts | Status | Notes |
|---|---|---|---|---|---|
| [REQ-ID] | [Functional/Nonfunctional/Policy/Design constraint/Interface requirement/Capability-derived requirement] | [path] | [path1; path2] | PASS/WAIVED/DEFERRED/FAIL | [notes] |

Rules:

- Every in-scope requirement must appear in this table.
- Policy requirements may use governance policy + enforcement evidence instead of executable tests.
- Design constraints should point to design detail plus implementation or analysis evidence.

---

## 3. Traceability Matrices Included

| Artifact | Path | Coverage Note |
|---|---|---|
| Sprint Traceability Matrix | [path] | [note] |
| Requirement-to-Implementation Matrix | [path] | [note] |
| Requirement-to-Verification Matrix | [path] | [note] |

---

## 4. Verification Execution Summary

- Test runs executed (if applicable)
- Analysis packages reviewed
- Governance policy checks executed
- Design-constraint conformance checks executed

---

## 5. Gaps, Waivers, and Deferrals

| Requirement ID | Gap Type | Disposition | Approval | Follow-up |
|---|---|---|---|---|
| [REQ-ID] | [evidence missing/type mismatch/deferred] | [waived/deferred/fail] | [approver] | [issue or sprint target] |

---

## 6. SVD Reference Record

Record the exact reference that will be used in the SVD (or equivalent verification authority document):

- SVD document path: [path]
- SVD section: [section]
- Verification report path: [this file path]
- Commit SHA / tag context: [sha or tag]
- Reference statement:
  - "Release-candidate merge verification evidence is retained in-repo at [path] and was used as the approval basis for [version]."

---

## 7. Retention and Publication Confirmation

- [ ] Report is committed and retained in-repo.
- [ ] Report is not included in release-published artifact bundle.
- [ ] Release notes reference report path only (if needed).
