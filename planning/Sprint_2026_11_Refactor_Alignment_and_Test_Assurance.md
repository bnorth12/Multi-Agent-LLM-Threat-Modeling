# Sprint 2026-11 Refactor Alignment and Test Assurance Plan

Date: 2026-05-14
Status: In Progress (Closeout Focus)
Sprint Length: 2 weeks
Primary Goal: Align implementation, requirements, tests, and user/deployment documentation after LangGraph refactor using a phase-first validation sequence before dead-code removal.

## 0. Sprint 2026-11 Scope Boundary and Deferrals

This sprint remains a closeout sprint for alignment, testing evidence, and governance completion.

In-scope for Sprint 2026-11:

- Close all open or validated S11 tracker issues by adding missing evidence, links, and closure notes.
- Complete sprint-close documentation alignment from top-level README through sprint artifacts.
- Finish Lane A and Lane B evidence handling, manual validation evidence indexing, and closeout updates in test summary artifacts.

Out-of-scope for Sprint 2026-11 (defer to next sprint planning):

- Full Streamlit replacement for release UI and delivery of a standalone production frontend.
- Large-scale repository information architecture redesign beyond targeted cleanup required for sprint close.

Deferred planning item:

- D-S11-001 "Custom HTML Frontend for Non-Streamlit Release" is tracked as a next-sprint architecture initiative and should be pulled into the Sprint 2026-12 issue tracker during kickoff planning.

## 1. Evidence Baseline

This sprint proposal is based on current repository state after pull to main and targeted validation checks.

Confirmed baseline facts:

- Repository updated to latest main (fast-forward to a8495b2).
- Orchestrator now contains LangGraph-native execution path and a legacy compatibility wrapper.
- Default pipeline execution mode is still linear in code.
- User-facing docs currently state langgraph-compatible as the default execution mode.
- Requirements claim LangGraph-native routing as a SHALL requirement.
- Live LLM and visible-browser suites are opt-in via pytest markers and environment controls.
- A targeted orchestration regression slice passed after installing LangGraph:
  - pytest Tests/unit/test_orchestrator.py Tests/integration/test_validation_gates.py -q
  - Result: 14 passed

## 2. Key Misalignments to Resolve

### 2.1 Code vs Documentation

- src/threat_modeler/config.py defaults execution_mode to linear.
- docs/User_Manual.md and docs/user_manual/index.html show default execution_mode as langgraph-compatible.

### 2.2 Code vs Requirements

- Requirements/01_Project_Requirements.md (PRJ-023) and Requirements/Components/C01_Orchestrator_State_Requirements.md describe LangGraph-native routing expectations.
- Effective default runtime path does not enforce LangGraph unless configuration is changed.

### 2.3 Requirements/Docs Path Drift

- Requirements/HITL-012-014_Conditional_Gate_State_Reporting.md references stale path src/threat_modeler/orchestration/orchestrator.py.

### 2.4 Test Strategy Drift

- Tests/unit/test_orchestrator.py validates legacy StateGraph compatibility wrapper only.
- Tests/integration/test_validation_gates.py primarily exercises run_langgraph_compatible directly, not delegation behavior in run_planned_stages.
- Browser and live LLM tests are intentionally non-default and must be integrated into explicit release-gate policy.

## 3. Phase-Ordered Sprint Execution

The sprint is intentionally sequenced so test evidence drives implementation decisions and dead-code removal happens only after test-backed confidence is established.

### Phase 1: Offline Automated Regression and Coverage Stabilization (Start Here)

Objective:

- Establish a reliable CI-safe baseline by hardening unit and integration coverage before live-system testing.

Mapped issues:

- S11-001, S11-002, S11-003, S11-004, S11-006, S11-007

Execution requirements:

- Run unit and integration suites in CI-safe mode only.
- Document all failures with defect records and expected-vs-observed behavior.
- Fix test defects and production defects discovered by tests.
- Re-run suites until stable pass baseline is demonstrated.
- Record coverage impact and unresolved gaps.

Phase exit criteria:

- CI-safe test lane passes consistently.
- Delegation behavior and orchestration core paths are covered.
- Evidence and defects are logged in sprint artifacts.

### Phase 2: Ordered Automated Workflow Validation (Browser + Live LLM)

Objective:

- Validate end-to-end workflow in operational order where each step output is used as input to the next step.

Mapped issues:

- S11-007, S11-008, S11-011

Execution requirements:

- Execute automated browser/live tests in strict workflow sequence.
- Preserve artifacts from each step for the following step inputs.
- Capture timeout, retry, and failure diagnostics.
- Repair unstable steps and re-run from the start of the workflow.

Phase exit criteria:

- Ordered live workflow passes with reproducible evidence.
- Live lane policy, commands, and troubleshooting are documented.
- Evidence package is complete for release review.

### Phase 3: Dead and Unreachable Code Disposition

Objective:

- Evaluate dead/unreachable candidates only after Phases 1-2 prove what is truly unused.

Mapped issues:

- S11-009

Execution requirements:

- Reconcile dead-code inventory against observed runtime and test usage.
- Classify each candidate as remove, deprecate, or retain.
- Implement removals/deprecations only when replacement coverage exists.
- Re-run regression suites after each disposition change.

Phase exit criteria:

- Disposition decisions are documented with evidence.
- No regression introduced by removals/deprecations.

### Phase 4: Manual Workflow Validation and Governance Closeout

Objective:

- Confirm operator-observed workflow behavior and close all governance evidence requirements.

Mapped issues:

- S11-005, S11-010, S11-011, S11-012

Execution requirements:

- Run a manual user walkthrough of the full workflow in order.
- Validate outputs, exports, and documentation consistency.
- Complete traceability delta updates and closeout package.
- Ensure each issue has closure evidence and linked implementation records.

Phase exit criteria:

- Manual workflow validation completed with artifacts.
- Governance package complete and linked.
- Sprint issues ready for closure with verifiable evidence.

## 4. Managed Sprint Todo List

Use this list as the sprint control board in execution order.

1. Phase 1 start: establish CI-safe baseline commands and expected outputs.
1. Run offline regression suites and log all failures with defect IDs.
1. Fix failing tests and runtime defects discovered in offline lanes.
1. Re-run offline suites to green; record coverage and remaining gaps.
1. Phase 2 start: prepare ordered browser/live workflow test data and environment.
1. Execute ordered browser/live workflow tests; archive per-step artifacts.
1. Fix live/browser failures and re-run full ordered workflow to green.
1. Phase 3 start: reconcile dead-code candidates against real usage evidence.
1. Apply approved deprecations/removals with regression reruns after each change set.
1. Phase 4 start: execute manual user workflow walkthrough and artifact verification.
1. Complete traceability, lint, and sprint test execution summary updates.
1. Close sprint issues with PR/commit/evidence links and finalize sprint sign-off.

## 5. Sprint Backlog (Suggested)

| ID | Title | Points | Owner Role | Priority |
|---|---|---:|---|---|
| S11-001 | Authoritative execution mode decision and implementation | 3 | Technical Lead + Orchestrator Engineer | P0 |
| S11-002 | Runtime fallback consistency update | 2 | Orchestrator Engineer | P0 |
| S11-003 | Entry-path mode regression test | 3 | Test Lead | P0 |
| S11-004 | Orchestrator unit test refactor to LangGraph-first | 5 | Test Lead | P0 |
| S11-005 | Integration delegation coverage expansion | 5 | Test Lead | P0 |
| S11-006 | E2E lane split and marker policy hardening | 5 | Test Lead + DevOps | P1 |
| S11-007 | Live/browser evidence policy in test docs | 2 | Documentation Owner + Test Lead | P1 |
| S11-008 | Requirements refresh for LangGraph and gate behavior | 3 | Documentation Owner | P0 |
| S11-009 | User manual + architecture alignment update | 3 | Documentation Owner | P0 |
| S11-010 | Planning/release artifact synchronization | 3 | Product Owner + Documentation Owner | P1 |
| S11-011 | Dead-code inventory and classification report | 3 | Technical Lead | P1 |
| S11-012 | Dead-code disposition decision record | 2 | Product Owner + Technical Lead | P1 |
| S11-013 | Dead/shim code cleanup implementation | 3 | Orchestrator Engineer | P2 |
| S11-014 | Manual RC campaign checklist and runbook | 2 | QA Lead | P1 |
| S11-015 | Controlled live/browser validation execution | 3 | QA Lead | P1 |
| S11-016 | Sprint test execution summary and sign-off package | 2 | QA Lead + Product Owner | P0 |

Total suggested points: 49
Recommended committed points for sprint: 28 to 34 (defer P2 and overflow P1 as needed).

## 6. Test Strategy for Sprint 2026-11

### 5.1 Automated Lanes

Lane A: Fast CI Required

- Unit tests
- Integration tests
- E2E fixture-safe tests only
- No external credentials
- No visible browser requirement

Lane B: Controlled Live Validation (Ordered Workflow Required)

- Markers: llm_live, llm_live_browser
- Triggered on schedule or manual approval
- Requires explicit environment variables and credentials
- Must publish token and prompt evidence summaries
- Must preserve workflow ordering and step-to-step artifact chaining

### 5.2 Manual Validation

Mandatory manual checks before RC sign-off:

- Browser upload path with CAV fixture set
- HITL pause, decision, and resume flow
- Export artifact integrity (STIX, canonical graph, Mermaid, report, STRIDE)
- Documentation walkthrough against observed UI/runtime behavior

## 7. Governance Deliverables Required at Sprint Close

- Updated requirements artifacts:
  - Requirements/01_Project_Requirements.md
  - Requirements/Components/C01_Orchestrator_State_Requirements.md
  - Requirements/04_Traceability_Matrix.md
  - Requirements/05_Verification_Strategy.md
- Updated technical/user documentation:
  - docs/User_Manual.md
  - docs/user_manual/index.html
  - docs/architecture/framework_overview.md
  - README.md
- Updated test governance artifacts:
  - Tests/Test_Plan.md
  - Tests/README.md
  - planning/Test_Execution_Summary_Sprint_2026_11.md
- Sprint-close governance controls:
  - planning/Lint_Normalization_Sprint_2026_11.md
  - planning/Traceability_Delta_Appendix_Sprint_2026_11.md

## 8. Entry and Exit Gates

Sprint entry gate:

- Repo synced to main
- Dependency baseline installed successfully
- Smoke subset passing for orchestration path

Sprint exit gate:

- Code, docs, requirements, and traceability are mutually consistent.
- CI-safe automated lanes pass.
- Manual and controlled live validation evidence attached.
- Dead-code disposition completed and documented.
- Lint normalization pass completed for files touched in this sprint (and prior alignment update files), with zero unresolved markdownlint findings in scoped files.
- Traceability delta appendix completed, mapping each changed requirement and documentation line to runtime and test files.

## 9. Risks and Mitigations

- Risk: Default mode decision causes unexpected runtime regressions.
  - Mitigation: Introduce mode-delegation tests before changing defaults.
- Risk: Live/browser tests remain flaky and block release confidence.
  - Mitigation: Separate CI-safe and controlled-live lanes with explicit policy.
- Risk: Dead-code candidates may still be needed by edge workflows.
  - Mitigation: Dead-code changes are phase-gated after ordered automated validation evidence.
- Risk: Documentation drift reappears after sprint.
  - Mitigation: Add sprint close checklist item requiring traceability and doc consistency review.

## 10. Proposed Sprint Ceremony Artifacts

- Sprint kickoff alignment table: requirement -> code path -> test path -> document owner.
- Mid-sprint governance checkpoint: unresolved drifts and blocker review.
- Sprint closeout package: test summary, evidence index, requirement coverage delta report.
