# Sprint 2026-11: Dead Code Remediation Process (Multi-Step Approach)

**Date**: 2026-05-17
**Sprint**: 2026-11
**Related Tracker Items**: S11-009, DCI-001 through DCI-005
**Purpose**: Systematic removal of dead/unreachable code with continuous test validation at each phase.

---

## Overview

This document defines a rigorous multi-step process to identify, comment, validate, and remove dead code without introducing regressions.

**Approach**: Convert dead code to comments → Test → Review coverage → Delete → Test again.

---

## Phase 0: Dead Code Inventory (Completed)

**Status**: ✅ Complete (see `planning/Dead_Code_Inventory_Sprint_2026_11.md`)

Identified items:

| ID | File | Symbol | Decision | Status |
|---|---|---|---|---|
| DCI-001 | src/threat_modeler/orchestrator.py | StateGraph compatibility wrapper | Deprecate | Ready for Phase 1 |
| DCI-002 | src/threat_modeler/orchestrator.py | build_default_state_graph() | Deprecate | Ready for Phase 1 |
| DCI-003 | src/threat_modeler/orchestrator.py | agent_01_input_normalizer stub | Remove | Ready for Phase 1 |
| DCI-004 | src/threat_modeler/orchestrator.py | agent_02_context_builder stub | Remove | Ready for Phase 1 |
| DCI-005 | src/threat_modeler/orchestrator.py | linear branch | Deprecate | Keep (config gate still uses) |

---

## Phase 1: Code-to-Comment Conversion (Proposed)

**Goal**: Convert identified dead/unreachable code to block comments so test suites run unchanged but code is clearly marked for removal.

**Approach for each DCI item**:

1. Wrap function/class definition with `# DEAD CODE MARKER: <ID> <reason>` and `# END DEAD CODE MARKER: <ID>` comments.
2. Add a deprecation notice explaining when/why this will be removed.
3. Ensure the code still runs (wrapped code is not deleted, only commented).
4. Commit this change with message: `docs(dead-code): mark DCI-001 through DCI-004 with deprecation notices`.

### Example Transformation

```python
# OLD
def build_default_state_graph():
    """Build legacy state graph."""
    # ...function body...

# NEW
# DEAD CODE MARKER: DCI-002
# Reason: Only referenced by Tests/unit/test_orchestrator.py (legacy compatibility tests)
# Deprecation: Will be removed after legacy test suite is replaced with LangGraph-native tests
# Status: Scheduled for Phase 3 after Phase 2 (test migration) completes
# DO NOT ADD NEW CALLERS; use FrameworkOrchestrator.run_planned_stages() instead
def build_default_state_graph():
    """Build legacy state graph. [DEPRECATED - see DEAD CODE MARKER above]."""
    # ...function body...
# END DEAD CODE MARKER: DCI-002
```

### Files to Modify in Phase 1

- `src/threat_modeler/orchestrator.py` — Add markers around DCI-001, DCI-002, DCI-003, DCI-004.

### Testing After Phase 1

```bash
# Run Lane A (all unit + integration tests)
pytest Tests/unit/ Tests/integration/ -v --tb=short

# Run CI-safe e2e smoke tests
pytest Tests/e2e/test_browser_run_validation.py -v -m "not live_llm"

# Expected result: All tests pass (code is unchanged, only comments added)
```

### Validation Checklist

- [ ] All tests pass after Phase 1 (no code behavior changed).
- [ ] Code-to-comment transformation complete for all DCI items.
- [ ] Deprecation notices are clear and reference GitHub issues.
- [ ] Commit recorded with evidence in Sprint 2026-11 execution summary.

---

## Phase 2: Test Coverage Replacement (Prerequisite to Removal)

**Goal**: Ensure all removed code paths have replacement tests using FrameworkOrchestrator and LangGraph-native architecture.

**Current state**:
- Legacy orchestrator tests in `Tests/unit/test_orchestrator.py` only cover StateGraph compatibility wrapper.
- New FrameworkOrchestrator tests exist but are incomplete.

**Work required**:

| Test File | Current Coverage | Replacement Needed | Status |
|---|---|---|---|
| Tests/unit/test_orchestrator.py | StateGraph wrapper only (legacy) | Migrate to FrameworkOrchestrator + LangGraph native | In progress (S11-003) |
| Tests/integration/test_agent_pipeline_completeness.py | Execution paths | Ensure all 9-stage paths covered | In progress (S11-002) |
| Tests/integration/test_validation_gates.py | HITL gate logic | Ensure HITL bypass logic tested | In progress (S11-002) |

**Exit criteria for Phase 2**:

- [ ] New FrameworkOrchestrator unit tests have parity with or exceed legacy wrapper coverage.
- [ ] Integration tests cover all execution modes (linear, conditional, with/without gates).
- [ ] Lane A tests all pass (unit + integration baseline).
- [ ] Lane C autonomous e2e tests pass (9-stage end-to-end).

---

## Phase 3: Dead Code Deletion

**Goal**: Remove marked dead code after Phase 2 test coverage is complete and validated.

**Approach**:

1. Delete code between `# DEAD CODE MARKER` and `# END DEAD CODE MARKER` comments.
2. Remove the marker comments themselves.
3. Run full test suite to confirm no regressions.

### Deletion Targets (in order)

1. **Step 3.1**: Remove stubs (DCI-003, DCI-004)
   - Files: `src/threat_modeler/orchestrator.py`
   - Functions: `agent_01_input_normalizer`, `agent_02_context_builder`
   - Test after: Full Lane A pass required

2. **Step 3.2**: Remove build_default_state_graph (DCI-002)
   - File: `src/threat_modeler/orchestrator.py`
   - Function: `build_default_state_graph()`
   - Dependency: Must verify no other production code calls it
   - Test after: Full Lane A pass required

3. **Step 3.3**: Remove StateGraph compatibility wrapper (DCI-001)
   - File: `src/threat_modeler/orchestrator.py`
   - Class: `StateGraph`
   - Dependency: Update/remove legacy orchestrator tests that reference it
   - Test after: Full Lane A pass + Lane C e2e validation required

### Example Deletion Transformation

```python
# BEFORE (Phase 1, after code-to-comment)
# DEAD CODE MARKER: DCI-003
# Reason: Unused stub, no production callers
# Deprecation: Will be removed after FrameworkOrchestrator migration
def agent_01_input_normalizer(state: FrameworkState) -> FrameworkState:
    return state
# END DEAD CODE MARKER: DCI-003

# AFTER (Phase 3, after deletion)
# [function removed entirely]
```

### Testing After Each Deletion Step

```bash
# After each deletion, run full Lane A
pytest Tests/unit/ Tests/integration/ -v --tb=short

# Expected: All tests pass; no "undefined function/class" errors

# Run e2e smoke to confirm end-to-end behavior unchanged
pytest Tests/e2e/ -v -m "not live_llm" --tb=short

# Expected: All tests pass; threat modeling pipeline still works
```

---

## Phase 4: Post-Deletion Test Re-Run

**Goal**: Final validation that dead code removal didn't introduce subtle regressions.

**Activities**:

1. Full Lane A re-run with coverage metrics.
2. Full Lane C autonomous e2e re-run.
3. Manual spot-check of critical paths (input normalization, agent execution, report generation).

### Commands

```bash
# Full Lane A with coverage
pytest Tests/unit/ Tests/integration/ --cov=src/threat_modeler --cov-report=term-missing -v

# Lane C e2e
pytest Tests/e2e/test_browser_run_validation.py -v

# Expected: Coverage >= 75% for src/threat_modeler; all tests pass
```

### Validation Checklist

- [ ] All unit tests pass.
- [ ] All integration tests pass.
- [ ] E2E smoke tests pass.
- [ ] Code coverage >= baseline (should increase or stay same).
- [ ] No regressions in threat modeling output quality.

---

## Timeline and Sequencing

| Phase | Activity | Effort | Timeline | Blockers |
|---|---|---|---|---|
| Phase 1 | Code-to-comment conversion | 1 point | Day 1 (1–2 hrs) | None |
| Phase 1 | Lane A test validation | 0.5 points | Day 1 | None |
| Phase 2 | Replace test coverage (S11-003) | 2–3 points | Days 2–3 | S11-001, S11-002 must land first |
| Phase 2 | Lane A + C validation | 1 point | Day 3 | Phase 1 + replacement tests must pass |
| Phase 3 | Step 3.1–3.3 deletions | 1 point | Day 4 | Phase 2 must be complete |
| Phase 3 | Lane A testing after each deletion | 1 point | Day 4 | Phase 3 step completion |
| Phase 4 | Final validation (coverage, regression) | 1 point | Day 5 | All Phase 3 deletions complete |

**Total Sprint 2026-11 effort**: ~8–9 points
**Critical path**: Phases 1 → 2 → 3 → 4 (sequential)

---

## Success Criteria

- [ ] Phase 1: All deprecation-marked code runs; no test failures.
- [ ] Phase 2: Replacement test coverage complete; Lane A + C pass.
- [ ] Phase 3: Dead code deleted; Lane A + C pass; no regressions.
- [ ] Phase 4: Code coverage maintained/improved; all tests pass; no functional regressions.
- [ ] Sprint execution summary records all evidence (commits, test outputs, coverage reports).
- [ ] GitHub issues S11-009 (dead code), S11-003 (test migration) closed with evidence links.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| Deletion breaks legacy test that we missed | Medium | High | **Phase 2**: Replace tests BEFORE deletion; Phase 3: incremental deletions with full test re-run after each. |
| Coverage drops after deletion | Low | Medium | **Phase 4**: Enforce coverage >= baseline before sign-off. |
| Subtle regression in threat modeling output | Low | Critical | **Phase 2 + 4**: Run Lane C e2e tests; manual spot-check output quality. |

---

## Rollback Plan

If issues are discovered during Phase 3 or 4:

1. Revert deletion commit(s).
2. Re-run Phase 1 code-to-comment conversion on the reverted code.
3. Investigate root cause in Phase 2 coverage (missing test scenario).
4. Fix test coverage gap.
5. Retry Phase 3 deletion after re-validation.

---

## Documentation Artifacts

All phases produce evidence for Sprint 2026-11 closeout:

1. **Phase 1 Commit**: Deprecation markers added.
2. **Phase 2 Test Results**: Lane A + C pass logs; coverage report.
3. **Phase 3 Deletion Commits**: Deletion steps 3.1, 3.2, 3.3 with test pass evidence after each.
4. **Phase 4 Report**: Final coverage report, Lane A + C test results, regression assessment.

Record all in `planning/Test_Execution_Summary_Sprint_2026_11.md` under "Dead Code Remediation Evidence" section.
