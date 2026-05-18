# Sprint 2026-11 GitHub Issue Drafts

Date: 2026-05-14
Use: Copy each section into GitHub issue creation form.

## S11-001 Authoritative Execution Mode Governance

Title:
Sprint 2026-11 S11-001: Authoritative execution-mode governance and runtime enforcement

Body:

- Problem: LangGraph path is implemented but effective runtime behavior depends on execution_mode. Governance requires explicit and testable policy.
- Scope:
  - Finalize policy for linear vs langgraph-compatible modes.
  - Ensure config/runtime defaults and release evidence path are consistent.
  - Update docs and requirements where needed.
- Acceptance criteria:
  - Policy documented in requirements and user docs.
  - Runtime defaults and fallback behavior align with policy.
  - Evidence of governed release profile uses execution_mode=langgraph-compatible.
- Files:
  - src/threat_modeler/config.py
  - src/threat_modeler/backend/runtime_state.py
  - src/threat_modeler/orchestrator.py
  - Requirements/01_Project_Requirements.md
  - Requirements/Components/C01_Orchestrator_State_Requirements.md

## S11-002 Delegation Path Coverage

Title:
Sprint 2026-11 S11-002: Add delegation-path test coverage for run manager and orchestrator mode branching

Body:

- Problem: Existing tests emphasize direct orchestrator calls; delegation path coverage needs to be explicit.
- Scope:
  - Add integration tests for run_manager and run_planned_stages delegation.
  - Assert behavior for linear and langgraph-compatible mode selection.
- Acceptance criteria:
  - Tests fail if delegation path is bypassed/regressed.
  - Test evidence attached in sprint summary.
- Files:
  - src/threat_modeler/backend/run_manager.py
  - Tests/integration/test_agent_pipeline_completeness.py
  - Tests/integration/test_validation_gates.py

## S11-003 Orchestrator Unit Test Refactor

Title:
Sprint 2026-11 S11-003: Replace legacy-only orchestrator unit coverage with LangGraph-native coverage

Body:

- Problem: Current unit coverage relies on compatibility wrapper APIs.
- Scope:
  - Refactor unit tests to focus on FrameworkOrchestrator and LangGraph-native execution behavior.
  - Keep or remove legacy tests based on dead-code disposition decision.
- Acceptance criteria:
  - FrameworkOrchestrator core paths covered.
  - Validation halt and checkpoint resume behavior covered.
- Files:
  - Tests/unit/test_orchestrator.py
  - src/threat_modeler/orchestrator.py

## S11-004 Traceability Matrix Reconciliation

Title:
Sprint 2026-11 S11-004: Reconcile PRJ-023 and C01-ORCH-003 traceability mappings

Body:

- Problem: Requirement updates are not fully reflected in traceability matrix mappings.
- Scope:
  - Update requirement-to-component and requirement-to-test mappings.
  - Ensure updated governance entries are represented.
- Acceptance criteria:
  - Traceability matrix references C01-ORCH-003 where relevant.
  - Test linkage for LangGraph governance is current.
- Files:
  - Requirements/04_Traceability_Matrix.md

## S11-005 Traceability Delta Appendix Maintenance

Title:
Sprint 2026-11 S11-005: Maintain traceability delta appendix for all changed requirement/doc lines

Body:

- Problem: Sprint changes need a single auditable mapping artifact.
- Scope:
  - Keep appendix updated for every requirement/doc line change.
  - Map each line to runtime and test files.
- Acceptance criteria:
  - No changed requirement/doc line missing from appendix.
  - Verification status resolved by sprint close.
- Files:
  - planning/Traceability_Delta_Appendix_Sprint_2026_11.md

## S11-006 Scoped Lint Normalization Gate

Title:
Sprint 2026-11 S11-006: Execute scoped lint normalization for touched sprint files

Body:

- Problem: Documentation quality gate must pass for touched files without broad repo churn.
- Scope:
  - Run markdownlint on touched files only.
  - Record command output and timestamp in sprint evidence.
- Acceptance criteria:
  - Scoped lint pass with no unresolved findings or approved waivers.
- Files:
  - planning/Lint_Normalization_Sprint_2026_11.md
  - touched markdown files listed in runbook

## S11-007 Lane Policy Operationalization

Title:
Sprint 2026-11 S11-007: Operationalize Lane A and Lane B testing policy in release workflow

Body:

- Problem: Lane policy is documented but needs explicit operational enforcement.
- Scope:
  - Ensure Lane A required for PR/main.
  - Ensure Lane B evidence or waiver is mandatory for relevant release claims.
- Acceptance criteria:
  - Lane outcomes visible in sprint execution summary.
  - Waiver path defined and evidenced when used.
- Files:
  - Tests/README.md
  - Tests/Test_Plan.md
  - planning/Test_Execution_Summary_Sprint_2026_11.md

## S11-008 Controlled-Live Browser Reliability

Title:
Sprint 2026-11 S11-008: Stabilize controlled-live browser validation and evidence capture

Body:

- Problem: Browser-live flows are opt-in and can hang or fail without deterministic handling.
- Scope:
  - Define timeout/retry handling and fail-fast criteria.
  - Define mandatory artifacts for pass/fail diagnosis.
- Acceptance criteria:
  - Controlled-live runbook yields repeatable outcomes and diagnostics.
- Files:
  - Tests/e2e/test_browser_run_validation.py
  - Tests/e2e/test_browser_cav_markdown_upload.py
  - Tests/e2e/LIVE_LLM_VALIDATION_GUIDE.md

## S11-009 Dead Code Disposition Execution

Title:
Sprint 2026-11 S11-009: Execute dead-code deprecation and removal plan for LangGraph migration residuals

Body:

- Problem: Legacy compatibility symbols remain and need governed disposition.
- Scope:
  - Follow inventory decisions to deprecate/remove symbols once replacement coverage exists.
- Acceptance criteria:
  - Dead-code inventory items moved to resolved with evidence.
  - No regression in orchestration/hitl/export paths.
- Files:
  - src/threat_modeler/orchestrator.py
  - planning/Dead_Code_Inventory_Sprint_2026_11.md

## S11-010 User Manual Drift Prevention

Title:
Sprint 2026-11 S11-010: Prevent markdown-html user manual drift

Body:

- Problem: Manual markdown and generated html can diverge after changes.
- Scope:
  - Define and apply regeneration/check process.
  - Verify key config defaults and policy text remain aligned.
- Acceptance criteria:
  - Manual markdown and html consistency checks pass for touched sections.
- Files:
  - docs/User_Manual.md
  - docs/user_manual/index.html

## S11-011 Sprint Test Execution Evidence Package

Title:
Sprint 2026-11 S11-011: Produce sprint test execution summary with lane and manual evidence

Body:

- Problem: Sprint closure needs a single authoritative evidence package.
- Scope:
  - Record Lane A results.
  - Record Lane B results or waivers.
  - Record manual validation evidence index.
- Acceptance criteria:
  - Summary file complete and linked from sprint tracker.
- Files:
  - planning/Test_Execution_Summary_Sprint_2026_11.md

## S11-012 GitHub Issue Lifecycle Compliance

Title:
Sprint 2026-11 S11-012: Enforce GitHub issue lifecycle compliance for sprint closure

Body:

- Problem: Sprint governance requires issue-level traceability and closure evidence.
- Scope:
  - Ensure each in-repo issue has GitHub issue counterpart.
  - Ensure closure notes include PR/commit and verification evidence.
- Acceptance criteria:
  - No sprint issue remains without GitHub mapping.
  - Closed issues include evidence references.
- Files:
  - planning/issues/Sprint_2026_11_Issue_Tracker.md

## S11-013 Backend Heartbeat and Stall Watchdog

Title:
Sprint 2026-11 S11-013: Add backend heartbeat ticker and stall watchdog to run_manager

Body:

- Problem: Long-running LLM calls (e.g., rate-limited or hung requests) could leave the run silently stalled with no observable failure signal until the UI-level timeout fires. Operators had no way to distinguish a slow-but-active call from a completely stalled one.
- Scope:
  - Add `_run_heartbeat_ticker(run_id, stop_event)` daemon thread that writes a timestamp to the run registry every `THREAT_MODELER_HEARTBEAT_INTERVAL_SECONDS` (default 3s) while the run is active.
  - Add `_run_heartbeat_watchdog(run_id, stop_event)` daemon thread that monitors heartbeat age and transitions the run to FAILED if it exceeds `THREAT_MODELER_HEARTBEAT_TIMEOUT_SECONDS` (default 35s).
  - Both threads started in `submit_run()` and `resume_run()`; stopped via shared `stop_event` in the finally block.
  - Registry entries include `last_heartbeat_time` and `heartbeat_timeout_seconds`.
  - Status-write guards added so watchdog FAILED transition does not overwrite a legitimate completion status.
- Acceptance criteria:
  - A stalled run (no agent progress) is marked FAILED within the configured timeout window.
  - Heartbeat timestamps are queryable from the registry while the run is active.
  - Heartbeat timeout threshold is configurable via environment variable.
- Files:
  - src/threat_modeler/backend/run_manager.py

## S11-014 UI Sidebar Heartbeat Age Visibility

Title:
Sprint 2026-11 S11-014: Expose heartbeat age and timeout in sidebar execution status badge

Body:

- Problem: Operators watching the sidebar had no visibility into backend liveness. The execution badge showed status and elapsed time but not whether the backend was still making progress.
- Scope:
  - Add `get_heartbeat_age_seconds()` to `execution.py` using `last_heartbeat_time` from session state.
  - `sync_execution_state_to_session()` now syncs `last_heartbeat_time` and `heartbeat_timeout_seconds` from the run registry.
  - `render_execution_status_badge()` now shows a `"Heartbeat age: Xs / timeout Ys"` caption while run is RUNNING or QUEUED.
  - Session state defaults include `last_heartbeat_time: None` and `heartbeat_timeout_seconds: None`.
- Acceptance criteria:
  - Sidebar caption "Heartbeat age:" is visible in the browser within one poll cycle (≤3s) after a run starts.
  - E2E smoke test asserts the caption is present in the sidebar DOM during active pipeline execution.
- Files:
  - src/threat_modeler/ui/execution.py

## S11-015 Run Diagnostics Panel on Home Dashboard

Title:
Sprint 2026-11 S11-015: Add Run Diagnostics panel to Home Run Dashboard screen

Body:

- Problem: Operators had to cross-reference multiple dashboard sections and log files to understand run health at a glance. Status, elapsed time, provider, heartbeat, current stage, and gate state were scattered across the page.
- Scope:
  - Add `_render_run_diagnostics_panel()` function called from `_render_live_dashboard()` in `home.py`.
  - Panel renders as `st.subheader("Run Diagnostics")` followed by a `st.container(border=True)` with two rows of four `st.metric` widgets each: Execution Status, Elapsed, Provider, Provider State (row 1) and Run ID, Current Stage, Paused Gate, Heartbeat Age (row 2).
  - Also shows heartbeat timeout threshold caption, current step caption, detected provider HTTP error code (e.g., 429), and error context when a failure is present.
  - Panel uses internal try/except to show a degraded error message rather than silently disappearing if any data-fetch call throws.
- Acceptance criteria:
  - "Run Diagnostics" subheader is visible in the browser DOM within 20s of run start.
  - "Heartbeat Age" metric label is visible within the panel while run is active.
  - E2E smoke test asserts both strings are present.
- Files:
  - src/threat_modeler/ui/screens/home.py

## S11-016 Enhanced Error Display with Decoded HTML and HTTP Code Extraction

Title:
Sprint 2026-11 S11-016: Improve execution error rendering with decoded HTML entities and HTTP status extraction

Body:

- Problem: Provider error messages (especially from xAI/Grok) arrived as HTML-encoded strings, making them unreadable in the UI. HTTP status codes (e.g., 429 rate limit) were buried in escaped text and required log inspection to identify.
- Scope:
  - Add `_render_execution_error_details(error_text)` in `home.py`: decodes HTML entities via `html.unescape()`, shows decoded text in a `st.code` block, shows raw original in a `st.expander` for copy-paste.
  - Add `_extract_provider_http_status(error_text)` in `home.py`: extracts HTTP status codes from common patterns (status=NNN, HTTP NNN, Error NNN) using regex.
  - `_render_live_dashboard()` and `_render_run_diagnostics_panel()` call these helpers when `primary_error` is set.
  - Same decoded display applied to the Stage Results screen via `stage_results.py`.
- Acceptance criteria:
  - A 429 response from xAI produces a visible "Detected provider HTTP error code: 429" warning on the Home screen.
  - Error text displays in human-readable form without HTML entity escaping.
  - Raw original is available via expander for debugging.
- Files:
  - src/threat_modeler/ui/screens/home.py
  - src/threat_modeler/ui/screens/stage_results.py
