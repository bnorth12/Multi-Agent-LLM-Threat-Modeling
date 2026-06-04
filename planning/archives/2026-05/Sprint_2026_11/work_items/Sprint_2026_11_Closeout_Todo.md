# Sprint 2026-11 Local Closeout Todo

Date: 2026-05-17
Owner: BN
Status: Active
Purpose: Local managed execution checklist to close Sprint 2026-11 cleanly before Sprint 2026-12 planning.

---

## 🔴 CRITICAL BLOCKERS (Discovered 2026-05-17)

### S11-017 — Prompt Editor Not Persisted To Execution Path

User edits to agent prompts in the UI (GUI-009) are saved to Streamlit session state only and are never persisted to the backend execution path (`backend/prompt_store.py`). Result: Agents execute with hardcoded defaults, not user edits. Single/multi-shot examples are lost.

**Fix**: Bridge `ui/prompt_store.set_prompt()` to call `backend/prompt_store.set_prompt()`.
**Estimated**: 1–2 points (straightforward backend bridge).
**Blocker Reason**: Feature integrity and user trust.
**Status**: Issue created at `planning/issues/issue_2026_11_S11_017_Prompt_Editor_Not_Persisted.md`.

#### Subtasks

- [ ] Implement bridge in `src/threat_modeler/ui/prompt_store.py`.
- [ ] Add unit test in `Tests/unit/test_ui_backend_prompt_sync.py`.
- [ ] Add integration test verifying agent execution uses edited prompts.
- [ ] Verify test passing and commit.
- [ ] Update S11 tracker with evidence link and close issue.

---

### S11-018 — Agent Prompt Loading Silent Fallback Exception Handlers

Agent prompt loading (`_load_system_prompt()` and `_load_expected_output()`) silently falls back to hardcoded/file-based defaults on **any exception** without logging. If backend store is inaccessible, agents execute with defaults and failure is invisible.

**Impact**: Even with S11-017 fixed, if backend store has any issue, S11-018 ensures users never know their prompts weren't used.

**Fix**: Replace blanket `except Exception` handlers with specific exception types and explicit logging.
**Estimated**: 1–2 points (refactor exception handling, add logging).
**Blocker Reason**: **S11-017 + S11-018 together required for reliable prompt persistence.**
**Status**: Issue created at `planning/issues/issue_2026_11_S11_018_Agent_Prompt_Fallback_Exception_Handlers.md`.

#### Subtasks

- [ ] Implement specific exception handling in `src/threat_modeler/agents/base.py` (lines 45–56).
- [ ] Add logging for all fallback paths (ImportError, KeyError, other).
- [ ] Add unit tests for exception scenarios.
- [ ] Add integration test verifying edited prompts are used when backend is available.
- [ ] Verify test passing and commit.
- [ ] Update S11 tracker with evidence link and close issue.

---

### **CRITICAL PATH**: S11-017 + S11-018 Must Be Done Together

1. Implement S11-017 (UI → backend bridge).
1. Implement S11-018 (exception handling + logging).
1. Run full integration test suite to verify both work together.
1. **Only then** continue to dead code remediation and other S11 work.

---

## Dead Code Remediation (Multi-Step Process)

**Status**: Not started (Phase 1 ready to begin)
**Related**: S11-009, DCI-001 through DCI-005
**Process**: Code-to-comment → Test → Review → Delete → Test again
**Timeline**: Phases 1–4, approximately 8–9 points total effort

**Comprehensive process documented in**: `planning/Dead_Code_Remediation_Process_Sprint_2026_11.md`

### Quick Summary of Phases

| Phase | Activity | Effort | Gate |
|---|---|---|---|
| Phase 1 | Convert dead code to comments with deprecation notices | 1.5 points | Lane A tests must pass |
| Phase 2 | Complete replacement test coverage (S11-003) | 2–3 points | Lane A + C tests must pass |
| Phase 3 | Delete marked dead code (steps 3.1, 3.2, 3.3) | 1 point | Full Lane A + e2e pass after each deletion |
| Phase 4 | Final validation and regression testing | 1 point | Coverage >= baseline; all tests pass |

### Identified Dead Code Items

- **DCI-001**: StateGraph compatibility wrapper class → Deprecate
- **DCI-002**: build_default_state_graph() function → Deprecate
- **DCI-003**: agent_01_input_normalizer stub → Remove
- **DCI-004**: agent_02_context_builder stub → Remove
- **DCI-005**: linear branch in run_planned_stages → Keep (still used by config)

### Phase 1 Checklist (Code-to-Comment)

- [ ] Wrap DCI-001 through DCI-004 with deprecation notices in `src/threat_modeler/orchestrator.py`.
- [ ] Run Lane A tests → verify all pass (no code behavior changed).
- [ ] Commit: `docs(dead-code): mark DCI-001 through DCI-004 with deprecation notices`.
- [ ] Record evidence in test summary.

### Phase 2 Checklist (Test Coverage Replacement)

- [ ] Complete S11-003: Replace legacy orchestrator tests with FrameworkOrchestrator + LangGraph-native tests.
- [ ] Verify test coverage parity or improvement.
- [ ] Run Lane A + Lane C e2e → all pass.
- [ ] Record evidence.

### Phase 3 Checklist (Deletion)

- [ ] Step 3.1: Delete DCI-003, DCI-004 (stubs) → Run Lane A.
- [ ] Step 3.2: Delete DCI-002 (build_default_state_graph) → Run Lane A.
- [ ] Step 3.3: Delete DCI-001 (StateGraph wrapper) + legacy tests → Run Lane A + Lane C.
- [ ] Record evidence after each step.

### Phase 4 Checklist (Final Validation)

- [ ] Run full Lane A with coverage report → coverage >= baseline.
- [ ] Run Lane C e2e tests → all pass.
- [ ] Manual regression spot-check (threat modeling output quality).
- [ ] Record final coverage and test results.

---

## 1. Scope Control

- [ ] Keep all active work tied to S11 tracker issues and test-summary evidence.
- [ ] **PRIORITY**: Resolve S11-017 + S11-018 (prompt persistence blockers) before other testing — these are feature integrity gates.
- [ ] **PRIORITY**: Execute dead code remediation (Phases 1–4) with explicit test validation at each phase.
- [ ] Defer D-S11-001 (non-Streamlit production frontend replacement) to Sprint 2026-12 kickoff planning package.
- [ ] Avoid new architecture epics during closeout unless required to resolve S11 blockers.

## 2. Issue Hygiene

- [ ] Reconcile S11 statuses: move validated items to closed only after evidence links are posted.
- [ ] Add missing PR/commit links for each S11 issue row.
- [ ] Ensure each S11 issue closure note references verification evidence and file paths.

## 3. Testing and Evidence Completion

- [ ] Re-run Lane A baseline and record command + pass totals in S11 test summary.
- [ ] Re-run/complete Lane B controlled-live workflow or add explicit waiver rationale.
- [ ] Confirm manual validation evidence index is complete and paths are valid.
- [ ] Confirm known residual risks are explicitly listed with severity and owner.

## 4. Documentation Cleanup

- [ ] Update top-level README current status to Sprint 2026-11 closeout context.
- [ ] Confirm docs/User_Manual.md and docs/user_manual/index.html remain aligned for current behavior.
- [ ] Update planning docs where headers still imply "ready to start" when sprint is active/in progress.
- [ ] Record any intentional document drift with owner and due date.

## 5. Repository Organization Cleanup (Targeted)

- [ ] Classify current untracked/generated artifacts vs source-of-record docs.
- [ ] Move or index sprint evidence artifacts to canonical folders used by planning/test reports.
- [ ] Propose follow-up backlog item for broader docs information architecture cleanup (next sprint).

## 6. Sprint Close Gate

- [ ] Lint normalization evidence captured for scoped files.
- [ ] Traceability delta appendix finalized.
- [ ] Test execution summary finalized with phase outcomes and sign-off placeholders completed.
- [ ] Sprint issue tracker updated with final Open/Closed counts.
- [ ] Next sprint planning seed includes deferred D-S11-001 and any carryover S11 items.
