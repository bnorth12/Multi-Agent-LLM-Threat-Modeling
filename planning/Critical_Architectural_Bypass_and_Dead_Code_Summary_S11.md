# Sprint 2026-11: Critical Architectural Bypass Items & Dead Code Remediation Summary

**Date**: 2026-05-17
**Sprint**: 2026-11 Closeout
**Status**: Discovery and Planning Complete
**Owner**: Development Team

---

## Executive Summary

Discovery phase identified **three critical categories of work** required before Sprint 2026-11 sign-off:

1. **Two critical architectural bypass defects** (S11-017, S11-018) that block prompt persistence reliability — **must fix both together**.
2. **Dead code remediation** with systematic multi-step approach (code-to-comment → test → delete → test again).

**Combined effort**: ~12–14 points
**Critical path**: S11-017 + S11-018 → Dead code Phases 1–4
**Must complete before RC1 sign-off**

---

## Category 1: Critical Architectural Bypass Defects

### S11-017 — Prompt Editor Modifications Not Persisted

**Issue**: User edits to agent prompts in the UI are saved to Streamlit session state only; they are never written to the backend persistence layer.

**Evidence**:
- `src/threat_modeler/ui/prompt_store.py` has `set_prompt()` that updates `st.session_state[...]` only.
- `set_prompt()` does NOT call `backend.prompt_store.PromptStore.set_prompt()`.
- No file-backed persistence mechanism wired.

**Impact**:
- Users edit prompts (including single/multi-shot examples) expecting them to be saved.
- Edits are lost when UI session ends.
- Agents always execute with hardcoded defaults.
- Feature (GUI-009) appears functional but is non-operational.

**Fix**:
```python
# In ui/prompt_store.py set_prompt():
# Update session state (existing)
st.session_state[_KEY_PROMPTS][agent_id] = text

# ADD: Bridge to backend persistence
try:
    from threat_modeler.backend.prompt_store import _default_store
    _default_store.set_prompt(agent_id, text, actor=actor)
except Exception:
    pass  # Graceful fallback if backend unavailable
```

**Effort**: 1–2 points
**Tests needed**:
- Unit: Verify backend file contains edited prompt
- Integration: Execute agent after UI edit, confirm agent uses edited prompt

---

### S11-018 — Agent Prompt Loading Silent Fallback

**Issue**: Agent prompt loading has blanket exception handlers that silently fall back to hardcoded/file-based prompts on **any exception** without logging or observability.

**Evidence**:
```python
# agents/base.py lines 45–56

def _load_system_prompt(self) -> str:
    try:
        from ..backend.prompt_store import get_prompt
        return get_prompt(self.stage_id)
    except Exception:  # <-- SWALLOWS ALL EXCEPTIONS SILENTLY
        return self._load_system_prompt_from_file()

def _load_expected_output(self) -> str:
    try:
        from ..backend.prompt_store import get_expected_output
        return get_expected_output(self.stage_id)
    except Exception:  # <-- RETURNS "" SILENTLY
        return ""
```

**Impact**:
- If backend prompt store is inaccessible (missing file, IO error, import error, etc.), agents execute with defaults.
- No logging, no error state, no user visibility.
- **Combined with S11-017**: Even if UI edits are saved to backend (after S11-017 fix), if backend is ever inaccessible, the failure is invisible.
- **Result**: Unreliable feature where prompt persistence can fail silently.

**Fix**:
Replace blanket handlers with specific exception types and explicit logging:

```python
import logging
logger = logging.getLogger(__name__)

def _load_system_prompt(self) -> str:
    try:
        from ..backend.prompt_store import get_prompt
        return get_prompt(self.stage_id)
    except ImportError as e:
        logger.error(f"Agent {self.stage_id}: backend import failed; falling back to file. {e}")
        return self._load_system_prompt_from_file()
    except KeyError as e:
        logger.warning(f"Agent {self.stage_id}: prompt not in backend store; fallback. {e}")
        return self._load_system_prompt_from_file()
    except Exception as e:
        logger.critical(f"Agent {self.stage_id}: unexpected error; fallback. {type(e).__name__}: {e}")
        return self._load_system_prompt_from_file()
```

**Effort**: 1–2 points
**Tests needed**:
- Unit: Verify logging on each exception type
- Unit: Verify file fallback is used only when backend fails
- Integration: Verify edited prompts reach agents when backend is available

---

### Why S11-017 + S11-018 Must Be Done Together

| Scenario | S11-017 Only | S11-018 Only | Both Fixed |
|---|---|---|---|
| User edits prompt in UI | ❌ Edit lost (not saved to backend) | N/A | ✅ Edit saved and used |
| Backend prompt store available | N/A | ✅ Agent uses default (because UI didn't save) | ✅ Agent uses edited prompt |
| Backend store inaccessible | N/A | ❌ Silent fallback, user unaware | ✅ Error logged; visible failure |

**S11-017 + S11-018 together = Reliable prompt persistence with full observability.**

---

## Category 2: Dead Code Remediation (Multi-Step Process)

### Overview

Dead code identified in LangGraph migration (DCI-001 through DCI-005) must be systematically removed with continuous test validation at each phase.

**Approach**: Convert to comments → Test → Review → Delete → Test again (not delete-first)

**Process documented fully**: `planning/Dead_Code_Remediation_Process_Sprint_2026_11.md`

---

### Identified Dead Code Items

| ID | File | Symbol | Decision | Notes |
|---|---|---|---|---|
| DCI-001 | orchestrator.py | StateGraph wrapper class | Deprecate | Only used by legacy tests; remove after test migration (S11-003) |
| DCI-002 | orchestrator.py | build_default_state_graph() | Deprecate | Only used by legacy tests; remove after test migration |
| DCI-003 | orchestrator.py | agent_01_input_normalizer stub | Remove | Not used in production; no ongoing dependency |
| DCI-004 | orchestrator.py | agent_02_context_builder stub | Remove | Not used in production; no ongoing dependency |
| DCI-005 | orchestrator.py | linear execution branch | Keep | Still used when config selects linear mode; don't remove |

---

### Four-Phase Remediation Process

**Phase 1: Code-to-Comment Conversion** (1.5 points)
- Wrap dead code with `# DEAD CODE MARKER: <ID>` comments and deprecation notices.
- Code still runs; no behavior change.
- Test: Lane A full pass (unit + integration).
- Commit: `docs(dead-code): mark DCI-001 through DCI-004 with deprecation notices`.

**Phase 2: Test Coverage Replacement** (2–3 points) — *Prerequisite to deletion*
- Replace legacy orchestrator tests with LangGraph-native tests (S11-003).
- Verify test parity or improvement.
- Test: Lane A + Lane C e2e.
- Gate: Must pass before Phase 3 deletion.

**Phase 3: Dead Code Deletion** (1 point)
- Step 3.1: Delete DCI-003, DCI-004 (stubs) → Lane A test.
- Step 3.2: Delete DCI-002 (build_default_state_graph) → Lane A test.
- Step 3.3: Delete DCI-001 (StateGraph wrapper) + legacy tests → Lane A + Lane C test.
- Each step has full test re-run to catch regressions.

**Phase 4: Final Validation** (1 point)
- Full Lane A with coverage metrics (coverage >= baseline).
- Full Lane C e2e test.
- Manual regression spot-check (threat modeling output quality).
- Record evidence for sprint closeout.

---

### Timeline and Dependencies

```
Day 1: Phase 1 (code-to-comment)
       ↓ Lane A tests must pass
Day 2: Phase 2 (test replacement) — blocks Phase 3
       ↓ Lane A + C tests must pass
Day 3-4: Phase 3 (deletion in 3 steps)
         ↓ Full Lane A + e2e pass after each step
Day 5: Phase 4 (final validation)
       ↓ Coverage >= baseline; all tests pass
Sprint Close: All evidence recorded in test summary
```

**Critical path**: S11-017 + S11-018 **must complete before Phase 1 starts** (to avoid mixing blockers with dead code work).

---

## Implementation Sequence (Recommended)

### Week 1 (Sprint 2026-11 remainder)

1. **Mon–Tue**: Implement S11-017 (UI → backend bridge) — 2 points
   - Modify `ui/prompt_store.py`
   - Add unit tests
   - Add integration tests
   - Lane A pass required

2. **Tue–Wed**: Implement S11-018 (exception handling + logging) — 2 points
   - Modify `agents/base.py`
   - Add unit tests for exception scenarios
   - Add integration test for combined S11-017 + S11-018
   - Lane A pass required

3. **Wed–Thu**: Phase 1 + Phase 2 of dead code remediation — 3.5 points
   - Phase 1: Code-to-comment conversion
   - Phase 1: Lane A validation
   - Phase 2: Complete test migration (S11-003)
   - Phase 2: Lane A + C validation

4. **Thu–Fri**: Phase 3 + Phase 4 of dead code remediation — 2 points
   - Phase 3: Delete dead code in 3 steps (full test after each)
   - Phase 4: Final validation + coverage check
   - Record all evidence

5. **Fri**: Sprint closeout activities — 1 point
   - Update test execution summary with all evidence
   - Update GitHub issues (S11-017, S11-018, S11-009) with closure notes
   - Finalize traceability delta appendix
   - Sprint sign-off

**Total effort**: ~12–14 points (fits within typical sprint velocity for closeout focused sprint)

---

## Success Criteria

### S11-017 Success
- [ ] UI prompt edits are persisted to `~/.multi_agent_threat_modeler_prompts.json`.
- [ ] Agent execution loads edited prompts (not hardcoded defaults).
- [ ] Unit test confirms backend file contains edited text.
- [ ] Integration test confirms agent uses edited prompt.
- [ ] Issue closed with evidence link.

### S11-018 Success
- [ ] `_load_system_prompt()` and `_load_expected_output()` have specific exception handlers.
- [ ] All fallback paths log at appropriate level (ERROR, WARNING, DEBUG).
- [ ] Unit tests verify each exception type is handled and logged.
- [ ] Integration test verifies no unexpected fallbacks when backend is available.
- [ ] Issue closed with evidence link.

### Dead Code Remediation Success
- [ ] Phase 1: Deprecation markers added; Lane A tests pass.
- [ ] Phase 2: Replacement tests complete; Lane A + C tests pass; coverage parity achieved.
- [ ] Phase 3: All dead code deleted; Lane A + C tests pass; no regressions.
- [ ] Phase 4: Final coverage >= baseline; manual regression check passed.
- [ ] S11-009 issue closed with evidence.
- [ ] All evidence recorded in test execution summary.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| S11-017 + S11-018 not done together → prompt persistence still broken | Medium | Critical | Explicitly plan both in same sprint; add to blockers checklist |
| Dead code deletion breaks unforeseen test | Medium | High | Phase 2 must complete before Phase 3; incremental deletions with full test rerun after each |
| Coverage drops after dead code removal | Low | Medium | Phase 4: enforce coverage >= baseline before sign-off |
| Subtle regression in threat modeling output | Low | Critical | Phase 4: Lane C e2e tests + manual spot-check output quality |

---

## File References

| Document | Purpose |
|---|---|
| [planning/issues/issue_2026_11_S11_017_Prompt_Editor_Not_Persisted.md](planning/issues/issue_2026_11_S11_017_Prompt_Editor_Not_Persisted.md) | S11-017 issue with root cause, solution, test plan |
| [planning/issues/issue_2026_11_S11_018_Agent_Prompt_Fallback_Exception_Handlers.md](planning/issues/issue_2026_11_S11_018_Agent_Prompt_Fallback_Exception_Handlers.md) | S11-018 issue with architectural analysis |
| [planning/Dead_Code_Remediation_Process_Sprint_2026_11.md](planning/Dead_Code_Remediation_Process_Sprint_2026_11.md) | Full 4-phase process, timeline, checklists |
| [planning/Dead_Code_Inventory_Sprint_2026_11.md](planning/Dead_Code_Inventory_Sprint_2026_11.md) | Original dead code inventory (DCI-001 through DCI-005) |
| [planning/issues/Sprint_2026_11_Issue_Tracker.md](planning/issues/Sprint_2026_11_Issue_Tracker.md) | Updated issue tracker (S11-017, S11-018 added) |
| [planning/work_items/Sprint_2026_11_Closeout_Todo.md](planning/work_items/Sprint_2026_11_Closeout_Todo.md) | Updated closeout todo with critical blockers and dead code phases |

---

## Conclusion

**S11-017 + S11-018 are mandatory blockers for RC1 release.** They represent architectural shortcuts that undermine feature reliability. Fixing them establishes a foundation for trustworthy prompt persistence.

**Dead code remediation (Phases 1–4) completes the S11 closeout scope** by eliminating legacy compatibility code and establishing a clean codebase for Sprint 2026-12 forward work.

Together, these three work streams position Sprint 2026-11 as a quality gate and architectural cleanup sprint, not just a test-fixes sprint.
