# Sprint [YYYY-MM] Traceability Matrix

**Sprint**: [YYYY-MM] (e.g., 2026-09)
**Start Date**: [Start Date]
**End Date**: [End Date]
**Status**: 🔄 Active | Sprint Planning [Date] → Sprint Closure [Date]

---

## Overview

This matrix tracks bidirectional traceability between Requirements, Issues, Code, and Tests.

**Completion Target**: 100% (all requirements have issues, all issues have tests, all tests pass)

**Current Status**: [X/Y requirements implemented] - [% complete]

---

## Traceability Matrix

| # | Requirement ID | Requirement Name | Issue ID | Issue Status | Assigned To | Test File | Verification Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | HITL-012 | Conditional Gate Trigger State Tracking | D-S08-020 | Open | [Dev Name] | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation | Track triggered (bool) and trigger_reason (str) fields |
| 2 | HITL-013 | Conditional Gate State Enumeration | D-S08-020 | Open | [Dev Name] | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation | Add AUTO_BYPASSED to GateStatus enum |
| 3 | HITL-014 | Dashboard Conditional Gate Status Display | D-S08-020 | Open | [Dev Name] | Tests/integration/test_hitl_dashboard_conditional_gates.py | ⏳ Pending Implementation | Render 🟢 Auto-Bypassed emoji for non-triggered gates |
| 4 | HITL-015 | Conditional Gate Trigger Metadata | D-S08-020 | Open | [Dev Name] | Tests/unit/test_hitl_gate_trigger_state.py | ⏳ Pending Implementation | Add trigger_condition_met and trigger_reason audit fields |
| | | | | | | | | |

---

## Status Legend

### Issue Status
- **Open**: Not started
- **In Progress**: Development underway
- **In Review**: PR created, awaiting approval
- **Merged**: PR merged, code committed
- **Completed**: Issue closed with verification evidence

### Verification Status
- **⏳ Pending Implementation**: Requirement not yet started
- **🔄 In Development**: Code being written, tests being added
- **🧪 Testing**: Tests written, running local validation
- **📝 Verification**: Awaiting evidence (screenshot, test output, CI/CD run)
- **✅ PASS**: Tests passing, evidence collected, requirement verified
- **❌ FAIL**: Tests failing, blocker identified, see notes
- **⚠️ Manual Test**: Manual verification required, evidence needed

---

## Sprint Workstreams

### Workstream 1: [Feature Name]
**Related Requirements**: [REQ IDs]

| Requirement ID | Status | Owner | Notes |
|---|---|---|---|
| | | | |

### Workstream 2: [Feature Name]
**Related Requirements**: [REQ IDs]

| Requirement ID | Status | Owner | Notes |
|---|---|---|---|
| | | | |

---

## Test Coverage Summary

| Test Type | Count | Status | Notes |
|---|---|---|---|
| Unit Tests | [#] | ✅ | Tests/unit/ directory |
| Integration Tests | [#] | ✅ | Tests/integration/ directory |
| E2E Tests | [#] | ⏳ | Tests/e2e/ directory |
| **Total** | **[#]** | | |

**Test Command**: `pytest Tests/ -v --tb=short`

**Coverage Target**: >80% for new code

---

## Blocking Issues

Any requirement with ❌ FAIL status or ⚠️ Manual Test blocker:

| Requirement | Issue | Blocker | Owner | Target Resolution |
|---|---|---|---|---|
| | | | | |

*No blockers currently* ✅

---

## Deferred Requirements

Requirements moved from this sprint to backlog:

| Requirement ID | Reason | Target Sprint |
|---|---|---|
| | | |

*No deferrals currently*

---

## Requirement Details

### [HITL-012] Conditional Gate Trigger State Tracking

**Issue**: D-S08-020
**Owner**: [Dev Name]
**Status**: Open → [In Progress] → Completed

**Acceptance Criteria**:
- [ ] HitlGateRecord has triggered (bool=False) field
- [ ] HitlGateRecord has trigger_reason (str|None=None) field
- [ ] to_dict() and from_dict() methods updated
- [ ] All unit tests passing
- [ ] No regression in existing tests

**Test File**: Tests/unit/test_hitl_gate_trigger_state.py

**Verification Evidence**:
- [ ] Screenshot: Test output showing all tests PASS
- [ ] CI/CD run: Link to GitHub Actions workflow
- [ ] Manual test: Dashboard update reflected (if UI change)

---

### [HITL-013] Conditional Gate State Enumeration

**Issue**: D-S08-020
**Owner**: [Dev Name]
**Status**: Open → [In Progress] → Completed

**Acceptance Criteria**:
- [ ] GateStatus enum has AUTO_BYPASSED value
- [ ] Gate state logic correctly assigns status per gate type
- [ ] Unit tests verify all gate states
- [ ] Dashboard can query gate state

**Test File**: Tests/unit/test_hitl_gate_trigger_state.py

**Verification Evidence**:
- [ ] Test output showing GateStatus enum tests PASS
- [ ] Code review approval

---

### [HITL-014] Dashboard Conditional Gate Status Display

**Issue**: D-S08-020
**Owner**: [Dev Name]
**Status**: Open → [In Progress] → Completed

**Acceptance Criteria**:
- [ ] Dashboard renders 🟢 Auto-Bypassed for status==AUTO_BYPASSED
- [ ] Distinguishes from ❓ Open (awaiting review) and ✅ Accepted
- [ ] Integration test verifies rendering
- [ ] Live E2E test confirms visual appearance

**Test File**: Tests/integration/test_hitl_dashboard_conditional_gates.py

**Verification Evidence**:
- [ ] Screenshot: Dashboard showing auto-bypassed gates with emoji
- [ ] Integration test log: All tests PASS
- [ ] E2E test video or screenshot

---

### [HITL-015] Conditional Gate Trigger Metadata

**Issue**: D-S08-020
**Owner**: [Dev Name]
**Status**: Open → [In Progress] → Completed

**Acceptance Criteria**:
- [ ] trigger_condition_met field added to HitlGateRecord
- [ ] trigger_reason field populated with condition description
- [ ] Audit trail captures why gate was bypassed or opened
- [ ] Archived with gate record for traceability

**Test File**: Tests/unit/test_hitl_gate_trigger_state.py

**Verification Evidence**:
- [ ] Unit test confirms fields populated correctly
- [ ] Audit log sample showing trigger_reason captured

---

## Sign-Off

### Sprint Planning Sign-Off

**Date**: ________________
**Sprint Lead**: ________________

- [ ] All accepted requirements have issues
- [ ] All issues in matrix
- [ ] Test files identified
- [ ] Team ready to execute

### Mid-Sprint Verification (Day 3-4)

**Date**: ________________
**Verified By**: ________________

- [ ] Run: `python scripts/verify_sprint_traceability.py --sprint [YYYY-MM]`
- [ ] 0 orphan requirements
- [ ] 0 orphan issues
- [ ] All issues have test file reference
- [ ] No changes to matrix needed

### Sprint Closure Sign-Off

**Date**: ________________
**Technical Lead**: ________________

- [ ] Traceability matrix 100% complete
- [ ] All tests passing (✅ PASS status)
- [ ] All verification evidence collected
- [ ] No blocking issues or waivers
- [ ] Sprint ready to close

**Final Status**: 🟢 **CLOSED** | Archived: `planning/archives/Sprint_[YYYY-MM]_Traceability_Matrix_FINAL.md`

---

## Automation & CI/CD Integration

**GitHub Actions Workflow**: `.github/workflows/sprint-traceability.yml`

- ✅ Verifies commit messages reference issue IDs
- ✅ Verifies issues link to requirements
- ✅ Blocks PR if traceability incomplete
- ✅ Generates daily audit report

**Verification Script**: `python scripts/verify_sprint_traceability.py --sprint [YYYY-MM]`

Run this anytime to check compliance:
- Mid-sprint: Identify gaps early
- Pre-closure: Ensure 100% traceability before sign-off

---

**This matrix is the single source of truth for sprint requirements-to-tests traceability.**

