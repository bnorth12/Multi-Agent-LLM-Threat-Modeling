# Test Plan

## 1. Objective

Define the release-candidate manual validation procedure and supporting automated coverage strategy for the multi-agent threat modeling workflow.

This plan is the execution authority for manual RC testing after a clean automated pass across all RC-included S09 features.

## 2. Scope

In scope:

- full manual end-to-end RC validation
- precondition checks and environment readiness
- GUI workflow validation with explicit click/input procedures
- artifact export and evidence verification
- user manual, product documentation, and deployment guide validation
- outcome recording with pass/fail/block states

Out of scope:

- model quality benchmarking across external providers
- visual design/aesthetic review not tied to functional behavior

## 3. Test Levels

### 3.1 Automated (Manual-RC Entry Gate)

- Unit: parser, schema, utility, agent contract checks
- Integration: stage transitions, recovery, HITL pause/resume
- E2E: fixture and live validation suites

### 3.2 Manual (Release-Gating for RC, Starts After Automated Clean Pass)

- full run workflow with 9 stages and 7 HITL gates
- results export and viewer validation
- documentation validation and deployment dry-run

## 4. Outcome Codes and Execution Rules

### 4.1 Outcome Codes

- `PASS`: step completed and expected result observed
- `FAIL`: step completed but expected result not met
- `BLOCK`: step cannot proceed due to environment, defect, dependency, or access problem

### 4.2 Iteration Rule

- Target completion in 1 to 2 defect-fix validation loops.
- If loop 3 is required, escalate to release readiness review before publication.

### 4.3 Required Execution Record Fields

For each test case:

- Test Case ID
- Tester
- Date/Time
- Environment
- Preconditions status
- Step-by-step outcomes (`PASS`/`FAIL`/`BLOCK`)
- Defect IDs opened
- Artifact links
- Final case verdict

## 5. Artifact Collection Standard

Testers SHALL collect artifacts while executing each case, not afterward.

### 5.1 Artifact Types

- screenshots (UI state, errors, successful outputs)
- exported files (STIX, canonical graph, Mermaid, report, STRIDE, token usage)
- logs (terminal, app logs, validation notes)
- documentation review notes (manual and deployment guide checks)

### 5.2 Minimum Naming Convention

- `TC-<ID>_STEP-<N>_<short-description>.<ext>`
- Example: `TC-RC-004_STEP-07_gate-resume-pass.png`

### 5.3 Storage Locations

- Screenshots: `docs/user_manual/screenshots/` or sprint evidence folder
- Execution summary: `planning/Test_Execution_Summary_Sprint_2026_09.md`
- Release artifacts/evidence: `Releases/` bundle for RC

## 6. Manual RC Test Cases

Each test case includes: purpose, preconditions, detailed steps, expected result, and required evidence.

### TC-RC-001: Environment and Preconditions Validation

Purpose: Confirm tester environment is ready before functional execution.

Preconditions:

- RC package artifacts are available.
- Access credentials for selected LLM mode exist.
- Tester has write access to evidence folders.

Steps:

1. Open terminal and verify Python/runtime prerequisites.
Expected: Prerequisite versions match deployment guide.
2. Verify RC artifact files exist and checksums validate.
Expected: All required files present and checksum verification passes.
3. Open deployment guide and confirm applicable environment profile.
Expected: Target environment profile selected and logged.

Record:

- Mark each step `PASS`/`FAIL`/`BLOCK`.

Collect artifacts:

- Checksum verification output log.
- Screenshot of artifact directory with required files.

### TC-RC-002: Application Launch and Configuration

Purpose: Verify operational runtime starts without Streamlit and browser-validation harness remains available for GUI test execution.

Preconditions:

- TC-RC-001 is `PASS`.

Steps:

1. Launch operational runtime (`python -m threat_modeler`).
Expected: API server starts without startup exceptions and responds on configured host/port.
2. Install browser-test dependencies and launch Streamlit harness (`pip install -r Tests/requirements_e2e.txt` then `streamlit run src/threat_modeler/ui/app.py`).
Expected: Streamlit harness starts for browser automation workflows.
3. Navigate to configuration screen.
Expected: Configuration controls render correctly.
4. Enter provider settings and click connection validation button.
Expected: Successful connection message for valid settings.
5. Enter invalid credentials and click validation again.
Expected: Clear error message; run start remains blocked for invalid settings.

Collect artifacts:

- Screenshot: successful validation state.
- Screenshot: invalid credentials error state.

### TC-RC-003: Input Entry and Run Start

Purpose: Verify operator can enter data and start pipeline.

Preconditions:

- TC-RC-002 is `PASS` for valid configuration.

Steps:

1. Navigate to input entry screen.
Expected: Input form fields are visible and editable.
2. Enter required system description and interface data.
Expected: Inputs accepted; no schema errors for valid data.
3. Click run start/submit action.
Expected: Run is created; status transitions from queued to running.

Collect artifacts:

- Screenshot: populated input form before submission.
- Screenshot: run started status with run ID.

### TC-RC-004: HITL Gate Workflow (All Mandatory Gates)

Purpose: Validate pause, review, approve/reject, and resume behavior.

Preconditions:

- TC-RC-003 is `PASS` and run is in progress.

Steps:

1. Wait for HITL gate pause.
Expected: Status shows paused with gate identifier.
2. Open threat review/gate screen.
Expected: Gate context and payload summary are visible.
3. Click approve decision control for first gate.
Expected: Decision recorded and visible.
4. Click resume action.
Expected: Run status returns to running; no duplicate-resume behavior.
5. Repeat for all mandatory gates.
Expected: Each gate transitions correctly; run eventually completes.

Collect artifacts:

- One screenshot per gate pause.
- One screenshot per gate decision confirmation.
- One screenshot showing final stage completion.

### TC-RC-005: Results Export Artifact Generation

Purpose: Verify all release artifacts are generated and downloadable.

Preconditions:

- TC-RC-004 is `PASS` and run completed.

Steps:

1. Open results export screen.
Expected: Export controls are enabled for completed run.
2. Download STIX bundle.
Expected: File downloads; content is non-empty JSON.
3. Download canonical graph.
Expected: File downloads; content includes expected graph nodes/edges.
4. Download Mermaid output.
Expected: File downloads with diagram source.
5. Download report and token usage artifacts.
Expected: Files download and contain run data.
6. Download STRIDE standalone export.
Expected: STRIDE export file exists and matches viewer content.

Collect artifacts:

- Screenshot: export controls panel.
- Saved copies of all downloaded artifacts.

### TC-RC-006: Viewer Functionality Validation (S09)

Purpose: Validate STIX, canonical graph, Mermaid, and STRIDE viewers.

Preconditions:

- TC-RC-005 is `PASS`.

Steps:

1. Open STIX viewer section.
Expected: Objects grouped and filter/search controls function.
2. Open canonical graph viewer.
Expected: Hierarchical structures render and are navigable.
3. Open Mermaid viewer and source toggle.
Expected: Diagram renders; source view toggles correctly.
4. Open STRIDE viewer.
Expected: STRIDE rows, scores, and justifications are visible and sortable.

Collect artifacts:

- Screenshot per viewer in successful state.
- Screenshot of any rendering error with context.

### TC-RC-007: Quick Preview Validation

Purpose: Verify quick preview panels are functional and current-run consistent.

Preconditions:

- TC-RC-005 is `PASS`.

Steps:

1. Expand each quick preview panel.
Expected: Correct preview content loads without error.
2. Navigate away and return to results export.
Expected: Previews remain functional and data is current.
3. Refresh browser and re-open preview panels.
Expected: Preview panels still load and are not stale.

### TC-RC-012: Visible Browser CAV Upload Validation

Purpose: Verify analyst-facing UI upload path accepts CAV ICD + markdown narratives in a visible browser automation run.

Preconditions:

- `RUN_VISIBLE_BROWSER_TESTS=1`
- Optional live credential env vars configured for extended live run validation.

Steps:

1. Launch visible-browser automation test:
   `pytest Tests/e2e/test_browser_cav_markdown_upload.py -v -m llm_live_browser -s`
   Expected: Chromium opens (headless disabled).
2. Automation fills Input Entry system name and uploads:
   - `icd_charlie_v1.xlsx`
   - `description_cav.md`
   - `description_avionics.md`
   Expected: all file names appear in the UI selected-files list.

Collect artifacts:

- Screenshot of Input Entry page with all three uploaded file names visible.
- Command output log with PASS result.

Collect artifacts:

- Screenshot for each preview panel open state.
- Screenshot after refresh proving continued function.

### TC-RC-008: Version Manifest and File Inventory Validation

Purpose: Verify release traceability artifacts are present and consistent.

Preconditions:

- RC evidence bundle has been generated.

Steps:

1. Open component semantic version manifest.
Expected: Required components and semantic versions present.
2. Open component-file version inventory.
Expected: Deterministic identifiers listed for component-owned files.
3. Compare mapping between component manifest and file inventory.
Expected: No orphan entries; mapping consistency confirmed.

Collect artifacts:

- Saved manifest and inventory files.
- Comparison notes or screenshot evidence of consistency check.

### TC-RC-009: User Manual Validation (MD and HTML)

Purpose: Verify user manual instructions are accurate against actual product behavior.

Preconditions:

- Manual markdown and HTML versions are available.

Steps:

1. Follow user manual steps for configuration and run initiation.
Expected: Product behavior matches instructions.
2. Follow manual steps for gate review and resume.
Expected: Workflow and labels match documented instructions.
3. Follow manual steps for export and viewer usage.
Expected: Documented outputs match actual outputs.
4. Validate screenshots and links in manual.
Expected: Screenshots are current and links resolve.

Collect artifacts:

- Manual validation checklist with per-section outcome.
- Screenshots of any doc mismatch defects.

### TC-RC-010: Product Documentation Consistency Validation

Purpose: Verify release-critical documentation set is internally consistent.

Preconditions:

- Release notes draft, requirements, process docs, and traceability docs are available.

Steps:

1. Compare release notes claims to implemented features.
Expected: Claims accurately reflect implemented S09 scope.
2. Check requirements and traceability references for S09 entries.
Expected: IDs, issue links, and verification references are consistent.
3. Check RC validation sequencing policy is consistent across release docs.
Expected: Manual RC campaign is documented as starting only after a clean automated pass.

Collect artifacts:

- Documentation review matrix with pass/fail/block by document.
- Defect log entries for inconsistencies.

### TC-RC-011: Deployment Guide Dry Run

Purpose: Validate deployment guide can be executed step by step in clean environment.

Preconditions:

- Clean environment prepared.

Steps:

1. Execute installation steps exactly as written.
Expected: Installation completes successfully.
2. Execute configuration and startup steps.
Expected: Application starts and is reachable.
3. Execute manual validation subset referenced by deployment guide.
Expected: Key operational checks pass.
4. Execute rollback steps as dry run or controlled simulation.
Expected: Rollback procedure is clear and operationally valid.

Collect artifacts:

- Terminal log of deployment steps.
- Screenshot of app running post-deploy.
- Rollback notes/evidence.

## 7. Defect Severity Guidelines

- Critical: release-blocking failure, unsafe behavior, data integrity issues
- Major: core workflow broken, required artifact missing, invalid documentation procedure
- Minor: non-blocking mismatch, formatting issue, minor wording defects

## 8. Traceability

- Each manual RC test case SHALL reference requirement IDs in the execution summary.
- Results SHALL be recorded in `planning/Test_Execution_Summary_Sprint_2026_09.md`.
- Evidence links SHALL be included for every failed or blocked step and every release-gating pass claim.
