# Sprint 2026-11 Master Closeout Execution Plan

**Date**: 2026-05-17
**Sprint**: 2026-11 (Closeout Focus)
**Owner**: Autonomous Execution
**Status**: Ready for Execution
**Total Estimated Effort**: 12–14 points
**Timeline**: 5 working days

---

## 🎯 Mission

Close Sprint 2026-11 with:
1. **Two critical architectural defects fixed** (S11-017, S11-018 — prompt persistence blockers)
2. **Dead code systematically remediated** (Phases 1–4, DCI-001 through DCI-004)
3. **All evidence collected** and recorded in test summary
4. **All S11 issues closed** with closure notes and verification links
5. **Sprint sign-off gate** completed with final documentation

---

## 📋 Master Execution Sequence

### **STAGE 1: Critical Architectural Defects (S11-017 + S11-018)**
*Days 1–2 | Estimated: 3–4 points | BLOCKER: Must complete before Stage 2*

These two defects must be fixed together to establish reliable prompt persistence. **No other work proceeds until both pass Lane A + integration tests.**

---

#### **TASK 1.1: Implement S11-017 (UI → Backend Bridge)**

**Objective**: Wire UI prompt edits to backend persistent storage.

**Files to Modify**:
- `src/threat_modeler/ui/prompt_store.py` — Add backend delegation to `set_prompt()`

**Implementation Steps**:

1. **Step 1.1.1**: Modify `ui/prompt_store.py` `set_prompt()` function
   - Keep existing session state update
   - Add delegation to `backend.prompt_store._default_store.set_prompt()`
   - Wrap in try-except for graceful fallback if backend unavailable

   ```python
   # EXISTING: Update session state
   st.session_state[_KEY_PROMPTS][agent_id] = text
   history: list[VersionEntry] = st.session_state[_KEY_HISTORIES][agent_id]
   next_version = history[-1].version + 1 if history else 1
   history.append(VersionEntry(version=next_version, text=text, actor=actor, timestamp=_utc_now()))

   # ADD: Persist to backend
   try:
       from threat_modeler.backend.prompt_store import _default_store
       _default_store.set_prompt(agent_id, text, actor=actor)
   except Exception:
       pass  # Graceful fallback: UI session-only if backend unavailable
   ```

2. **Step 1.1.2**: Create unit test `Tests/unit/test_ui_backend_prompt_sync.py`
   - Test: UI edit persists to backend file
   - Test: Backend file survives UI session end
   - Test: New agent execution loads edited prompt from file

3. **Step 1.1.3**: Create integration test `Tests/integration/test_prompt_edit_to_execution.py`
   - Test: Edit prompt in UI → backend saves it
   - Test: Execute agent → agent loads edited prompt
   - Test: Agent's LLM call contains edited prompt (not default)

4. **Step 1.1.4**: Run tests
   ```bash
   pytest Tests/unit/test_ui_backend_prompt_sync.py -v
   pytest Tests/integration/test_prompt_edit_to_execution.py -v
   ```

   **Acceptance**: Both test suites pass

5. **Step 1.1.5**: Run Lane A baseline
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass (no regressions)

6. **Step 1.1.6**: Commit and record evidence
   - Commit message: `fix(S11-017): wire UI prompt edits to backend persistent storage`
   - Record: Commit hash, test output summary
   - Update: `planning/issues/Sprint_2026_11_Issue_Tracker.md` S11-017 row with commit link

**Acceptance Criteria**:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Lane A baseline passes
- [ ] Commit recorded and evidence linked

**Evidence Location**:
- Test output: `planning/Test_Execution_Summary_Sprint_2026_11.md` → "S11-017 Evidence" section
- Commit: GitHub (will be added to tracker)

---

#### **TASK 1.2: Implement S11-018 (Exception Handler + Logging)**

**Objective**: Replace blanket exception handlers with specific exceptions + logging.

**Files to Modify**:
- `src/threat_modeler/agents/base.py` — Lines 45–56 (prompt loading methods)

**Implementation Steps**:

1. **Step 1.2.1**: Add logging import and update exception handlers in `base.py`

   ```python
   import logging
   logger = logging.getLogger(__name__)

   def _load_system_prompt(self) -> str:
       try:
           from ..backend.prompt_store import get_prompt
           return get_prompt(self.stage_id)
       except ImportError as e:
           logger.error(
               f"Agent {self.stage_id}: failed to import backend.prompt_store; "
               f"falling back to file-based prompt. Error: {e}"
           )
           return self._load_system_prompt_from_file()
       except KeyError as e:
           logger.warning(
               f"Agent {self.stage_id}: prompt not found in backend store; "
               f"falling back to file-based prompt. Error: {e}"
           )
           return self._load_system_prompt_from_file()
       except Exception as e:
           logger.critical(
               f"Agent {self.stage_id}: unexpected error loading system prompt; "
               f"falling back to file-based prompt. Error type: {type(e).__name__}, Message: {e}"
           )
           return self._load_system_prompt_from_file()

   def _load_expected_output(self) -> str:
       try:
           from ..backend.prompt_store import get_expected_output
           return get_expected_output(self.stage_id)
       except (ImportError, KeyError) as e:
           logger.debug(
               f"Agent {self.stage_id}: expected output not found in backend store; "
               f"returning empty. Error: {e}"
           )
           return ""
       except Exception as e:
           logger.warning(
               f"Agent {self.stage_id}: unexpected error loading expected output; "
               f"returning empty. Error type: {type(e).__name__}, Message: {e}"
           )
           return ""
   ```

2. **Step 1.2.2**: Create unit test `Tests/unit/test_agent_base_prompt_loading.py`
   - Test: ImportError is caught and logged (agent uses file fallback)
   - Test: KeyError is caught and logged (agent uses file fallback)
   - Test: Unexpected exception is caught and logged CRITICAL (agent uses file fallback)
   - Test: Normal case (backend available) returns edited prompt

3. **Step 1.2.3**: Create integration test verifying S11-017 + S11-018 together
   - Test: UI edits prompt → backend persists it
   - Test: Agent executes → loads edited prompt from backend
   - Test: No fallbacks occur (logging shows "success" level, not "error")

4. **Step 1.2.4**: Run tests
   ```bash
   pytest Tests/unit/test_agent_base_prompt_loading.py -v
   pytest Tests/integration/test_prompt_edit_to_execution.py -v  # (re-run from 1.1)
   ```

   **Acceptance**: All tests pass

5. **Step 1.2.5**: Run Lane A baseline
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass (no regressions)

6. **Step 1.2.6**: Commit and record evidence
   - Commit message: `fix(S11-018): add explicit exception handling and logging to agent prompt loading`
   - Record: Commit hash, test output summary
   - Update: `planning/issues/Sprint_2026_11_Issue_Tracker.md` S11-018 row with commit link

**Acceptance Criteria**:
- [ ] Unit tests pass (all exception scenarios covered)
- [ ] Integration tests pass (S11-017 + S11-018 work together)
- [ ] Lane A baseline passes (no regressions)
- [ ] Commit recorded and evidence linked
- [ ] Logging verified in test output or local test run

**Evidence Location**:
- Test output: `planning/Test_Execution_Summary_Sprint_2026_11.md` → "S11-018 Evidence" section
- Commit: GitHub (will be added to tracker)

---

#### **GATE: S11-017 + S11-018 Verification**

**Before proceeding to Stage 2 (dead code), verify**:
- [ ] S11-017 commit merged
- [ ] S11-018 commit merged
- [ ] Lane A full baseline passes
- [ ] Both tracker issues updated with evidence links
- [ ] Integration test confirms edited prompts reach agents without fallback

**If any gate fails**: Debug and re-test before proceeding.

---

### **STAGE 2: Dead Code Remediation (Phases 1–4)**
*Days 2–4 | Estimated: 8–9 points | GATE: S11-017 + S11-018 must pass*

Systematic multi-phase approach: comment → test → review → delete → test again.

---

#### **PHASE 1: Code-to-Comment Conversion**

**Objective**: Mark dead code with deprecation notices; code still runs, no behavior change.

**TASK 2.1: Mark DCI-003, DCI-004 (Agent Stubs)**

1. **Step 2.1.1**: Open `src/threat_modeler/orchestrator.py`

2. **Step 2.1.2**: Locate `agent_01_input_normalizer` and `agent_02_context_builder` stub functions (around lines 95–115)

3. **Step 2.1.3**: Wrap each with deprecation markers:
   ```python
   # DEAD CODE MARKER: DCI-003
   # Reason: Unused stub; no production callers; only defined for legacy graph builder compatibility
   # Deprecation: Will be removed after FrameworkOrchestrator migration completes and legacy tests migrate
   # Status: Scheduled for deletion in Phase 3 after S11-003 (test migration) is complete
   # DO NOT ADD NEW CALLERS; this function will be removed in Sprint 2026-11 Phase 3
   def agent_01_input_normalizer(state: FrameworkState) -> FrameworkState:
       return state
   # END DEAD CODE MARKER: DCI-003
   ```

   (Repeat for DCI-004)

4. **Step 2.1.4**: Run Lane A tests
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass (no code behavior changed, only comments added)

5. **Step 2.1.5**: Commit
   - Commit message: `docs(dead-code): mark DCI-003, DCI-004 with deprecation notices`
   - Record: Commit hash

**TASK 2.2: Mark DCI-001, DCI-002 (Legacy Compatibility APIs)**

1. **Step 2.2.1**: Locate `StateGraph` class and `build_default_state_graph()` function

2. **Step 2.2.2**: Wrap each with deprecation markers (similar to DCI-003):
   ```python
   # DEAD CODE MARKER: DCI-001
   # Reason: Legacy StateGraph wrapper; only used by Tests/unit/test_orchestrator.py
   # Deprecation: Will be removed after legacy test suite is replaced with LangGraph-native tests
   # Status: Scheduled for deletion in Phase 3 after S11-003 (test migration) is complete
   # DO NOT ADD NEW CALLERS; this class will be removed
   class StateGraph:
       # ... existing class body ...
   # END DEAD CODE MARKER: DCI-001
   ```

   (Repeat for DCI-002)

3. **Step 2.2.3**: Run Lane A tests
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass

4. **Step 2.2.4**: Commit
   - Commit message: `docs(dead-code): mark DCI-001, DCI-002 with deprecation notices`
   - Record: Commit hash

**TASK 2.3: Verify Phase 1 Completion**

- [ ] All 4 dead code items (DCI-001 through DCI-004) are wrapped with deprecation markers
- [ ] Lane A tests pass
- [ ] Both commits recorded
- [ ] Update `planning/Test_Execution_Summary_Sprint_2026_11.md` → "Phase 1 (Code-to-Comment)" section with test evidence

---

#### **PHASE 2: Test Coverage Replacement (S11-003)**

**Objective**: Complete replacement of legacy orchestrator tests with LangGraph-native tests before deleting dead code.

**Prerequisite**: S11-003 issue work (test migration) must be completed in this phase.

**TASK 2.4: Migrate Unit Tests (Tests/unit/test_orchestrator.py)**

**Current state**: Legacy tests only cover StateGraph wrapper (DCI-001, DCI-002)

**Required**: Replace with FrameworkOrchestrator + LangGraph-native tests

1. **Step 2.4.1**: Review current test file
   ```bash
   head -50 Tests/unit/test_orchestrator.py
   ```

2. **Step 2.4.2**: Create new test suite for FrameworkOrchestrator (or enhance existing)
   - Test: Basic 9-stage pipeline execution
   - Test: Linear execution mode
   - Test: Conditional (langgraph-compatible) execution mode
   - Test: Stage skip functionality
   - Test: Error handling and recovery

3. **Step 2.4.3**: Add integration tests to `Tests/integration/` if not already present
   - Test: End-to-end agent delegation
   - Test: Execution modes switch correctly
   - Test: HITL gate behavior with conditional modes

4. **Step 2.4.4**: Run Lane A with coverage
   ```bash
   pytest Tests/unit/ Tests/integration/ --cov=src/threat_modeler --cov-report=term-missing -v
   ```

   **Acceptance Criteria**:
   - All tests pass
   - Coverage for orchestration code >= baseline (ideally improved)
   - LangGraph-native paths have explicit coverage

5. **Step 2.4.5**: Run Lane C e2e smoke tests
   ```bash
   pytest Tests/e2e/test_browser_run_validation.py -v -m "not live_llm"
   ```

   **Acceptance**: Tests pass (end-to-end behavior unchanged)

6. **Step 2.4.6**: Record evidence
   - Coverage report saved
   - Test output summary recorded
   - Commit test changes
   - Update `planning/Test_Execution_Summary_Sprint_2026_11.md` → "Phase 2 (Test Coverage Replacement)" section

**TASK 2.5: Verify Phase 2 Completion**

- [ ] Legacy orchestrator tests have been migrated or replaced with LangGraph-native equivalents
- [ ] New test coverage for FrameworkOrchestrator is in place
- [ ] Lane A tests pass with >= baseline coverage
- [ ] Lane C e2e tests pass
- [ ] S11-003 issue can be closed with evidence

---

#### **GATE: Phase 2 Validation**

**Before proceeding to Phase 3 (deletion), verify**:
- [ ] S11-003 tests merged
- [ ] Lane A full pass with coverage >= baseline
- [ ] Lane C e2e pass
- [ ] Evidence recorded

**If gate fails**: Improve test coverage before proceeding to deletion.

---

#### **PHASE 3: Dead Code Deletion (3 Steps)**

**Objective**: Remove dead code one step at a time, testing after each step.

**TASK 2.6: Step 3.1 — Delete DCI-003, DCI-004 (Stubs)**

1. **Step 2.6.1**: Open `src/threat_modeler/orchestrator.py`

2. **Step 2.6.2**: Delete the wrapped stub functions:
   ```python
   # REMOVE: agent_01_input_normalizer() entire function + markers
   # REMOVE: agent_02_context_builder() entire function + markers
   ```

3. **Step 2.6.3**: Check if any production code calls these stubs
   ```bash
   grep -r "agent_01_input_normalizer\|agent_02_context_builder" src/
   ```

   **Expected**: No matches (they're stubs only)

4. **Step 2.6.4**: Run Lane A tests
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass

5. **Step 2.6.5**: Record and commit
   - Commit message: `refactor(S11-009): remove dead stubs DCI-003, DCI-004`
   - Record: Commit hash, test output

---

**TASK 2.7: Step 3.2 — Delete DCI-002 (build_default_state_graph)**

1. **Step 2.7.1**: Delete the function and marker comments from orchestrator.py

2. **Step 2.7.2**: Search for callers
   ```bash
   grep -r "build_default_state_graph" .
   ```

   **Expected**: Only in tests (which have been migrated in Phase 2)

3. **Step 2.7.3**: Update any test files that reference it (should already be migrated)

4. **Step 2.7.4**: Run Lane A tests
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass

5. **Step 2.7.5**: Record and commit
   - Commit message: `refactor(S11-009): remove dead function DCI-002 (build_default_state_graph)`
   - Record: Commit hash, test output

---

**TASK 2.8: Step 3.3 — Delete DCI-001 (StateGraph Wrapper) + Legacy Tests**

1. **Step 2.8.1**: Delete the StateGraph class from orchestrator.py

2. **Step 2.8.2**: Search for remaining references
   ```bash
   grep -r "StateGraph" .
   ```

   **Expected**: Only in test files (which should now use FrameworkOrchestrator)

3. **Step 2.8.3**: Update/remove legacy test file references
   - Verify `Tests/unit/test_orchestrator.py` uses only FrameworkOrchestrator tests
   - Remove any remaining StateGraph references

4. **Step 2.8.4**: Run Lane A tests
   ```bash
   pytest Tests/unit/ Tests/integration/ -v --tb=short
   ```

   **Acceptance**: All tests pass

5. **Step 2.8.5**: Run Lane C e2e
   ```bash
   pytest Tests/e2e/test_browser_run_validation.py -v -m "not live_llm"
   ```

   **Acceptance**: Tests pass

6. **Step 2.8.6**: Record and commit
   - Commit message: `refactor(S11-009): remove dead class DCI-001 (StateGraph compatibility wrapper) and legacy test suite`
   - Record: Commit hash, test output

**TASK 2.9: Verify Phase 3 Completion**

- [ ] Step 3.1 deletion: All tests pass
- [ ] Step 3.2 deletion: All tests pass
- [ ] Step 3.3 deletion: Lane A + Lane C tests pass
- [ ] All commits recorded
- [ ] Update `planning/Test_Execution_Summary_Sprint_2026_11.md` → "Phase 3 (Dead Code Deletion)" section with evidence

---

#### **PHASE 4: Final Validation**

**Objective**: Comprehensive final testing and regression verification.

**TASK 2.10: Coverage and Regression Verification**

1. **Step 2.10.1**: Run full Lane A with coverage metrics
   ```bash
   pytest Tests/unit/ Tests/integration/ --cov=src/threat_modeler --cov-report=term-missing -v
   ```

   **Acceptance Criteria**:
   - All tests pass
   - Coverage >= baseline (preferably improved)
   - No coverage decreases in orchestration/agent paths

2. **Step 2.10.2**: Run Lane C e2e tests
   ```bash
   pytest Tests/e2e/test_browser_run_validation.py -v -m "not live_llm"
   ```

   **Acceptance**: All tests pass

3. **Step 2.10.3**: Manual regression spot-check
   - Run threat modeling pipeline locally with sample input
   - Verify output quality and completeness
   - Verify no unexpected errors in logs
   - Verify agent execution completes successfully

4. **Step 2.10.4**: Record final evidence
   - Coverage report
   - Test output summary
   - Manual spot-check notes
   - Update `planning/Test_Execution_Summary_Sprint_2026_11.md` → "Phase 4 (Final Validation)" section

**TASK 2.11: Verify Dead Code Remediation Completion**

- [ ] Phase 4 testing complete
- [ ] Coverage >= baseline
- [ ] Lane C e2e pass
- [ ] Manual regression check pass
- [ ] S11-009 issue ready to close
- [ ] All evidence recorded in test summary

---

### **STAGE 3: Sprint Closeout Activities**
*Day 5 | Estimated: 2–3 points*

---

#### **TASK 3.1: Close All S11 Issues with Evidence**

1. **Step 3.1.1**: Review `planning/issues/Sprint_2026_11_Issue_Tracker.md`

2. **Step 3.1.2**: For each S11 issue (S11-001 through S11-018), add closure note:
   - If closed: Add commit hash, test output link, verification summary
   - If open: Record blocker reason or next-sprint deferral

3. **Step 3.1.3**: Update tracker row:
   - Set Status = "Closed" or "Open"
   - Add evidence note with file paths and commit links

4. **Step 3.1.4**: Example closure note for S11-017:
   ```
   **Closure Note (2026-05-17)**:
   - Implemented UI → backend bridge in src/threat_modeler/ui/prompt_store.py
   - Added explicit exception handling in src/threat_modeler/agents/base.py (S11-018 paired fix)
   - Unit tests: Tests/unit/test_ui_backend_prompt_sync.py (PASS)
   - Integration tests: Tests/integration/test_prompt_edit_to_execution.py (PASS)
   - Lane A baseline: All tests pass (14 commits: a1b2c3d through e5f6g7h)
   - Evidence: planning/Test_Execution_Summary_Sprint_2026_11.md → "S11-017 Evidence" section
   - Verified: Edited prompts persist to backend file; agents use edited prompts on execution
   ```

5. **Step 3.1.5**: Commit tracker update
   - Commit message: `docs(S11): close tracker issues S11-017, S11-018, S11-009 with evidence`
   - Record: Commit hash

---

#### **TASK 3.2: Finalize Test Execution Summary**

1. **Step 3.2.1**: Open `planning/Test_Execution_Summary_Sprint_2026_11.md`

2. **Step 3.2.2**: Complete sections (if not already done):
   - Phase 1 evidence (S11-017 + S11-018 implementation)
   - Phase 2 evidence (dead code comment markers + Lane A pass)
   - Phase 3 evidence (dead code deletion steps + Lane A/C passes)
   - Phase 4 evidence (final validation + coverage report)

3. **Step 3.2.3**: Add summary table:
   ```markdown
   | Phase | Activity | Result | Evidence |
   |---|---|---|---|
   | Phase 1 (S11-017, S11-018) | Implement prompt persistence & exception handling | PASS | Commit hashes: ... |
   | Phase 2 (Dead Code Comments) | Mark DCI-001-004 with deprecation notices | PASS | Commit hash: ... |
   | Phase 3 (Dead Code Deletion) | Remove DCI-003, DCI-004, DCI-002, DCI-001 in 3 steps | PASS | Commit hashes: ... |
   | Phase 4 (Final Validation) | Coverage check, Lane A/C e2e, regression spot-check | PASS | Coverage >= baseline, all tests pass |
   ```

4. **Step 3.2.4**: Record known risks (if any):
   - List any unresolved issues with severity and owner
   - Record waivers or deferrals with rationale

5. **Step 3.2.5**: Commit test summary update
   - Commit message: `docs(S11): finalize test execution summary with all phase evidence`
   - Record: Commit hash

---

#### **TASK 3.3: Update Top-Level Documentation**

1. **Step 3.3.1**: Open `README.md`

2. **Step 3.3.2**: Update "Current Sprint Status" section:
   - Status: "Sprint 2026-11 Closeout Complete (2026-05-17)"
   - Highlights: Prompt persistence fixed, dead code removed, architecture cleaned
   - Next: "Sprint 2026-12 kickoff will address non-Streamlit production frontend (D-S11-001)"

3. **Step 3.3.3**: Verify no other top-level docs have stale S11 references

4. **Step 3.3.4**: Commit README update
   - Commit message: `docs(README): update sprint status to S11 closeout complete`
   - Record: Commit hash

---

#### **TASK 3.4: Verify Traceability Delta Appendix**

1. **Step 3.4.1**: Open `planning/Traceability_Delta_Appendix_Sprint_2026_11.md`

2. **Step 3.4.2**: For each S11 issue, add row:
   ```markdown
   | S11-017 | Prompt Editor Not Persisted | Critical | Fixed | src/threat_modeler/ui/prompt_store.py, src/threat_modeler/agents/base.py | Commit: a1b2c3d; Tests: Tests/unit/test_ui_backend_prompt_sync.py |
   ```

3. **Step 3.4.3**: Record any traceability gaps or deferred items

4. **Step 3.4.4**: Commit traceability appendix
   - Commit message: `docs(S11): finalize traceability delta appendix with all issue resolutions`
   - Record: Commit hash

---

#### **TASK 3.5: Final Sprint Sign-Off Gate**

**Verification Checklist**:

- [ ] S11-017 (Prompt Editor) closed with evidence ✓
- [ ] S11-018 (Exception Handlers) closed with evidence ✓
- [ ] S11-009 (Dead Code Removal) closed with evidence ✓
- [ ] Dead code fully removed (DCI-001 through DCI-004) ✓
- [ ] Lane A baseline passes (all unit + integration tests) ✓
- [ ] Lane C e2e passes (9-stage end-to-end) ✓
- [ ] Coverage >= baseline ✓
- [ ] Test execution summary complete with all phases ✓
- [ ] All S11 issues in tracker closed with closure notes ✓
- [ ] Traceability delta appendix complete ✓
- [ ] README and docs updated to S11 closeout status ✓
- [ ] No open blockers or unresolved dependencies ✓

**If all checkboxes pass**:
- [ ] Record final sign-off note in `planning/Test_Execution_Summary_Sprint_2026_11.md`
- [ ] Create final commit: `chore(S11): sprint 2026-11 closeout complete - all evidence recorded`
- [ ] Record commit hash

**If any checkbox fails**:
- Investigate failure
- Create defect task (e.g., "Phase 4 coverage shortfall")
- Add to blockers list
- Escalate for resolution before final sign-off

---

## 📊 Autonomous Execution Todo List

Below is the **managed todo list** for autonomous execution. Update this list as work progresses.

---

## EXECUTION TODO LIST (Managed)

**Status**: Not Started
**Last Updated**: 2026-05-17
**Executor**: Autonomous Agent

### Stage 1: Critical Architectural Defects (S11-017 + S11-018)

- [ ] **1.1.1** Modify `ui/prompt_store.py` to add backend delegation in `set_prompt()`
- [ ] **1.1.2** Create unit test file `Tests/unit/test_ui_backend_prompt_sync.py`
- [ ] **1.1.3** Create integration test file `Tests/integration/test_prompt_edit_to_execution.py`
- [ ] **1.1.4** Run S11-017 tests → verify PASS
- [ ] **1.1.5** Run Lane A baseline → verify PASS
- [ ] **1.1.6** Commit S11-017 and record evidence
- [ ] **1.2.1** Modify `agents/base.py` to add specific exception handlers + logging (lines 45–56)
- [ ] **1.2.2** Create unit test file `Tests/unit/test_agent_base_prompt_loading.py`
- [ ] **1.2.3** Verify integration test from 1.1 works with S11-018
- [ ] **1.2.4** Run S11-018 tests → verify PASS
- [ ] **1.2.5** Run Lane A baseline → verify PASS
- [ ] **1.2.6** Commit S11-018 and record evidence
- [ ] **GATE 1** Verify both S11-017 + S11-018 pass and are committed

### Stage 2: Dead Code Remediation — Phase 1 (Code-to-Comment)

- [ ] **2.1.1** Mark DCI-003, DCI-004 with deprecation comments in `orchestrator.py`
- [ ] **2.1.2** Run Lane A tests → verify PASS
- [ ] **2.1.3** Commit Phase 1 (DCI-003, DCI-004) and record evidence
- [ ] **2.2.1** Mark DCI-001, DCI-002 with deprecation comments in `orchestrator.py`
- [ ] **2.2.2** Run Lane A tests → verify PASS
- [ ] **2.2.3** Commit Phase 1 (DCI-001, DCI-002) and record evidence
- [ ] **2.3** Update test summary with Phase 1 evidence

### Stage 2: Dead Code Remediation — Phase 2 (Test Coverage Replacement)

- [ ] **2.4.1** Review current tests in `Tests/unit/test_orchestrator.py`
- [ ] **2.4.2** Create/enhance FrameworkOrchestrator unit tests
- [ ] **2.4.3** Ensure integration test coverage for execution modes
- [ ] **2.4.4** Run Lane A with coverage → verify PASS and coverage >= baseline
- [ ] **2.4.5** Run Lane C e2e → verify PASS
- [ ] **2.4.6** Record Phase 2 evidence (coverage report, test output)
- [ ] **2.5** Update test summary with Phase 2 evidence
- [ ] **GATE 2** Verify Phase 2 tests complete and Lane A/C pass

### Stage 2: Dead Code Remediation — Phase 3 (Deletion: 3 Steps)

- [ ] **2.6.1** Delete DCI-003, DCI-004 stubs from `orchestrator.py`
- [ ] **2.6.2** Verify no production callers to stubs (grep check)
- [ ] **2.6.3** Run Lane A tests → verify PASS
- [ ] **2.6.4** Commit Step 3.1 deletion and record evidence
- [ ] **2.7.1** Delete DCI-002 (`build_default_state_graph`) from `orchestrator.py`
- [ ] **2.7.2** Verify no remaining callers (grep check)
- [ ] **2.7.3** Run Lane A tests → verify PASS
- [ ] **2.7.4** Commit Step 3.2 deletion and record evidence
- [ ] **2.8.1** Delete DCI-001 (StateGraph class) from `orchestrator.py`
- [ ] **2.8.2** Verify no remaining references (grep check)
- [ ] **2.8.3** Update/remove legacy test file references
- [ ] **2.8.4** Run Lane A tests → verify PASS
- [ ] **2.8.5** Run Lane C e2e tests → verify PASS
- [ ] **2.8.6** Commit Step 3.3 deletion and record evidence
- [ ] **2.9** Update test summary with Phase 3 evidence

### Stage 2: Dead Code Remediation — Phase 4 (Final Validation)

- [ ] **2.10.1** Run Lane A with coverage metrics → verify PASS and coverage >= baseline
- [ ] **2.10.2** Run Lane C e2e tests → verify PASS
- [ ] **2.10.3** Manual threat modeling pipeline spot-check
- [ ] **2.10.4** Record Phase 4 evidence (coverage report, test output, manual notes)
- [ ] **2.11** Update test summary with Phase 4 evidence

### Stage 3: Sprint Closeout Activities

- [ ] **3.1.1** Review `Sprint_2026_11_Issue_Tracker.md`
- [ ] **3.1.2** Add closure notes to S11-017, S11-018, S11-009 (and any others)
- [ ] **3.1.3** Update tracker with evidence links
- [ ] **3.1.4** Commit tracker update
- [ ] **3.2.1** Open `Test_Execution_Summary_Sprint_2026_11.md`
- [ ] **3.2.2** Complete all phase evidence sections
- [ ] **3.2.3** Add summary table
- [ ] **3.2.4** Record known risks (if any)
- [ ] **3.2.5** Commit test summary update
- [ ] **3.3.1** Update `README.md` sprint status
- [ ] **3.3.2** Verify no stale S11 references in other docs
- [ ] **3.3.3** Commit README update
- [ ] **3.4.1** Review `Traceability_Delta_Appendix_Sprint_2026_11.md`
- [ ] **3.4.2** Add issue resolution rows to appendix
- [ ] **3.4.3** Record traceability gaps
- [ ] **3.4.4** Commit traceability appendix update
- [ ] **3.5** Final sprint sign-off gate verification
- [ ] **3.5.1** Create final closeout commit

---

## 🎓 Progress Tracking

**How to use this list during autonomous execution**:

1. **Before starting each task**: Mark it with a note → "Starting at [timestamp]"
2. **After completing each task**: Mark with checkmark + evidence reference
3. **At end of each stage**: Record stage completion time and summary
4. **If blocker encountered**: Record blocker detail and escalation path

**Example progress update**:
```
2026-05-17 10:30 — Starting Task 1.1.1 (UI prompt_store.py modification)
2026-05-17 11:15 — ✅ Task 1.1.1 complete. File modified. Running tests now.
2026-05-17 11:45 — ✅ Task 1.1.2–1.1.5 complete. S11-017 tests PASS. Lane A PASS.
2026-05-17 12:00 — ✅ Stage 1 (S11-017 + S11-018) COMPLETE. Evidence recorded.
2026-05-17 12:15 — Starting Stage 2 Phase 1 (dead code comments)...
```

---

## 📁 Key Files Reference

| File | Purpose |
|---|---|
| [planning/issues/Sprint_2026_11_Issue_Tracker.md](planning/issues/Sprint_2026_11_Issue_Tracker.md) | S11 issue tracker; update closure notes and evidence links |
| [planning/Test_Execution_Summary_Sprint_2026_11.md](planning/Test_Execution_Summary_Sprint_2026_11.md) | Test evidence repository; record all test outputs and phase results here |
| [planning/issues/issue_2026_11_S11_017_Prompt_Editor_Not_Persisted.md](planning/issues/issue_2026_11_S11_017_Prompt_Editor_Not_Persisted.md) | S11-017 detailed spec (reference during implementation) |
| [planning/issues/issue_2026_11_S11_018_Agent_Prompt_Fallback_Exception_Handlers.md](planning/issues/issue_2026_11_S11_018_Agent_Prompt_Fallback_Exception_Handlers.md) | S11-018 detailed spec (reference during implementation) |
| [planning/Dead_Code_Remediation_Process_Sprint_2026_11.md](planning/Dead_Code_Remediation_Process_Sprint_2026_11.md) | Dead code remediation process details |
| [planning/Traceability_Delta_Appendix_Sprint_2026_11.md](planning/Traceability_Delta_Appendix_Sprint_2026_11.md) | Traceability delta; update with issue resolutions |
| [README.md](README.md) | Top-level docs; update sprint status at closeout |
| [src/threat_modeler/ui/prompt_store.py](src/threat_modeler/ui/prompt_store.py) | Task 1.1: Add backend delegation |
| [src/threat_modeler/agents/base.py](src/threat_modeler/agents/base.py) | Task 1.2: Add exception handling + logging |
| [src/threat_modeler/orchestrator.py](src/threat_modeler/orchestrator.py) | Tasks 2.1–2.8: Mark and delete dead code |

---

## ✅ Final Acceptance Criteria (Sprint Sign-Off)

**All of these must be true to sign off**:

1. **S11-017**: Implemented, tested (unit + integration), Lane A pass, merged, tracker closed with evidence ✓
2. **S11-018**: Implemented, tested (unit + integration), Lane A pass, merged, tracker closed with evidence ✓
3. **Dead Code (DCI-001 through DCI-004)**: Marked with comments → Tested → Deleted → Final validation PASS ✓
4. **Lane A**: Full unit + integration test suite passes with no regressions ✓
5. **Lane C**: E2E smoke tests pass; 9-stage pipeline works end-to-end ✓
6. **Coverage**: >= baseline (preferably improved) ✓
7. **Test Summary**: Complete with all phase evidence recorded ✓
8. **Issue Tracker**: All S11 issues closed with closure notes and evidence links ✓
9. **Traceability**: Delta appendix complete ✓
10. **Documentation**: README and docs updated to reflect S11 closeout status ✓

---

## 🚀 Ready to Execute

This plan is ready for autonomous execution. All tasks are clearly defined, acceptance criteria are explicit, and the todo list can be updated as work progresses.

**Start with Stage 1, Task 1.1.1** and proceed through the list sequentially. Record progress and evidence as you go.
