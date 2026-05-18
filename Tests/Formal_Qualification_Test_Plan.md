# Formal Qualification Test Plan

## 1. Purpose

Define the formal end-to-end qualification workflow for the Multi Agent Threat Modeler using the existing RC-style step-by-step execution format, with explicit requirement traceability and evidence capture for every executed step.

This plan is intended to qualify the full analyst workflow, including configuration, input entry, automatic run start, all 9 stages, all HITL gates, reject/edit/resume recovery paths, results export, viewers, snapshots, token telemetry, and documentation consistency.

## 2. Qualification Scope

In scope:

- environment readiness and evidence packaging
- application launch and provider configuration
- input entry and automatic pipeline start
- all 9 pipeline stages
- all mandatory HITL gates (HITL-001 through HITL-009)
- conditional HITL gates when triggered (HITL-010 and HITL-011)
- approve, reject, save draft, edit, and resume behaviors
- results export, stage viewers, token usage, snapshots, and prompt tools
- runtime-state projection and cross-screen state coherence
- documentation and traceability validation

Out of scope:

- model scoring quality benchmarking against external reference data
- performance tuning beyond qualification evidence capture

## 3. Execution Rules

- Every test case SHALL record `PASS`, `FAIL`, or `BLOCK` for each step.
- Every test case SHALL record requirement IDs covered by that case.
- Evidence SHALL be collected while executing the step, not after the fact.
- Rejected HITL decisions SHALL be followed by a recorded recovery path before the run is allowed to continue.
- Use a fresh run for each gate-rejection scenario when the rejected action would otherwise prevent later steps from being exercised.
- If a conditional gate does not trigger naturally, record it as `BLOCK` unless a controlled trigger fixture or test dataset is available.

## 4. Artifact Collection Standard

Collect artifacts for every test case:

- screenshots for each major screen and each gate state
- terminal log or browser run log
- exported JSON, STIX, Mermaid, Markdown, and snapshot artifacts
- evidence notes listing the observed requirement IDs and final verdict

Minimum naming convention:

- `FQT-<ID>_STEP-<N>_<short-description>.<ext>`

Suggested storage locations:

- `planning/` for the execution record
- `Releases/` for release bundles
- `docs/user_manual/screenshots/` or sprint evidence folders for screenshots

## 5. Formal Qualification Test Cases

### FQT-001: Environment and Evidence Readiness

Purpose: Confirm the test environment, artifacts, and evidence folders are ready before qualification execution.

Requirements covered:

- PRJ-016
- GUI-003
- GUI-003B
- GUI-003C
- GUI-016

Preconditions:

- RC artifact bundle is available.
- Credentials for the selected provider are available.
- Evidence storage location is writable.

Steps:

1. Verify Python and test-runtime prerequisites.
Expected: Virtual environment activates and the required test commands are available.
1. Verify release artifacts and source fixtures are present.
Expected: Input fixtures, docs, and release bundle files are present.
1. Confirm the evidence folder exists and is writable.
Expected: Screenshots and logs can be saved.
1. Open the traceability matrix and qualification plan.
Expected: Requirement IDs are available for later step logging.

Collect artifacts:

- terminal output showing environment checks
- screenshot or file listing proving evidence directory availability

### FQT-002: Application Launch, Provider Selection, and Connection Validation

Purpose: Verify the GUI launch path, provider selection controls, and connection validation workflow.

Requirements covered:

- PRJ-008
- PRJ-016
- GUI-012
- GUI-012A
- GUI-013
- GUI-014
- GUI-016
- GUI-017
- HITL-007

Preconditions:

- FQT-001 is `PASS`.

Steps:

1. Launch the application and open the configuration screen.
Expected: Configuration controls render without startup errors.
1. Select the provider and open provider-specific configuration fields.
Expected: Provider controls and connection fields are visible.
1. Enter valid provider settings and click connection validation.
Expected: Validation succeeds and the UI shows a success message.
1. Change to an invalid provider value or invalid credential and run validation again.
Expected: Validation fails with a clear error and the run start remains blocked.
1. Confirm stage-selection controls are visible and persistent.
Expected: All 9 stage checkboxes are visible and state persists after apply.

Collect artifacts:

- screenshot of successful provider validation
- screenshot of invalid validation error
- screenshot of all stage-selection controls
- terminal/browser log for the validation result

### FQT-003: Input Entry and Automatic Run Start

Purpose: Verify the analyst can enter input data and launch the pipeline from the GUI.

Requirements covered:

- PRJ-001
- PRJ-002
- PRJ-016
- GUI-001A
- GUI-003
- GUI-003A
- GUI-016

Preconditions:

- FQT-002 is `PASS`.

Steps:

1. Navigate to the input entry screen.
Expected: Input form fields are visible and editable.
1. Enter the required system description and interface data.
Expected: Inputs are accepted and validation messages are clear.
1. Upload the required source files.
Expected: Uploaded files are visible in the selected-files list.
1. Submit the form to start the run.
Expected: The pipeline begins automatically and the dashboard shows queued/running state.
1. Confirm the run ID and current stage are visible.
Expected: Run metadata appears in the dashboard and projection state updates correctly.

Collect artifacts:

- screenshot of populated input form
- screenshot of uploaded file list
- screenshot of running dashboard with run ID and stage
- browser log showing start transition

### FQT-004: Mandatory HITL Gate Acceptance Path

Purpose: Verify the standard accept-and-resume path across the mandatory HITL gates.

Requirements covered:

- HITL-001
- HITL-002
- HITL-003
- HITL-004
- HITL-005
- HITL-006
- HITL-007
- HITL-008
- GUI-002
- GUI-003A
- GUI-004
- GUI-005
- GUI-016

Preconditions:

- FQT-003 is `PASS` and the run reaches gate pauses.

Steps:

1. Wait for Gate 0 input integrity pause.
Expected: Gate context, stage metadata, and decision controls are visible.
1. Review the gate payload and click approve.
Expected: Decision is recorded and the run remains consistent.
1. Wait for the next mandatory gate pause.
Expected: Pause state shows the gate identifier and completed-stage count.
1. Repeat review and approve for each mandatory gate in the run.
Expected: Each gate transitions cleanly from paused to running.
1. Verify rationale capture on any non-default decision path used during qualification.
Expected: Rationale text is required when a reject or override path is exercised.

Collect artifacts:

- one screenshot per gate pause
- one screenshot per gate approval confirmation
- one screenshot showing resume after approval
- one log extract showing all gate decision records

### FQT-005: HITL Gate Rejection and Recovery Path

Purpose: Exercise reject, save-draft, edit, and resume behavior on selected gates before allowing the run to continue.

Requirements covered:

- HITL-001
- HITL-002
- HITL-003
- HITL-004
- HITL-005
- HITL-006
- HITL-007
- HITL-008
- GUI-002
- GUI-003A
- GUI-005
- GUI-017

Preconditions:

- FQT-003 is `PASS` and a new run is available for recovery-path testing.

Steps:

1. Pause at Gate 0 or Gate 1.
Expected: Reject/edit/save controls are visible.
1. Enter a reject decision with rationale.
Expected: The UI accepts the rejection only after rationale is provided.
1. Use the save draft or edit control if available.
Expected: Draft state is preserved or edits are accepted without losing context.
1. Change the decision to accept as is or accept changes.
Expected: The final recorded decision is updated.
1. Resume the run.
Expected: The run continues from the paused gate without duplicate-resume errors.
1. Repeat the reject/recover sequence on at least one later gate.
Expected: Gate-state transitions remain correct across multiple pauses.

Collect artifacts:

- screenshot of rejected gate state
- screenshot showing rationale entry
- screenshot of save draft or edit confirmation
- screenshot of the resumed running state
- run log demonstrating the decision transition history

### FQT-006: Conditional Gate Trigger Validation

Purpose: Verify the conditional Merge Conflict Resolution and Export Consistency gates when their trigger conditions are met.

Requirements covered:

- HITL-010
- HITL-011
- HITL-012
- GUI-003A
- GUI-003C
- GUI-006
- GUI-007
- GUI-008

Preconditions:

- A controlled dataset or fixture is available that can trigger one or both conditional gates.

Steps:

1. Run the workflow with the controlled conflict-inducing input.
Expected: Merge Conflict Resolution gate triggers when the condition is met.
1. Review the conflict details and make a decision.
Expected: The gate logs the triggered state and records the analyst choice.
1. Run the workflow with an output-consistency trigger condition.
Expected: Export Consistency gate triggers before publication.
1. Review the consistency findings and decide whether to accept or reject.
Expected: Publication is blocked until an accept decision is recorded.
1. Confirm trigger state is persisted in the run record.
Expected: Triggered or bypassed state is visible in the stored result data.

Collect artifacts:

- screenshot of each conditional gate when triggered
- evidence showing triggered=true or bypassed=false in the run record
- screenshot of publication blocked or resumed state

### FQT-007: Stage Results, Threat Review, and Viewer Validation

Purpose: Verify the stage output viewers and analyst review screens render current data.

Requirements covered:

- PRJ-016
- GUI-003B
- GUI-003C
- GUI-004
- GUI-005
- GUI-016

Preconditions:

- A completed run is available from FQT-004 or FQT-005.

Steps:

1. Open the Stage Results screen.
Expected: Stage outputs render with current run data.
1. Open the threat and mitigation review screen.
Expected: Threats, scores, and mitigations are visible and current.
1. Open the viewer screens used for release inspection.
Expected: Content is not stale and matches the completed run.
1. Refresh or navigate across screens.
Expected: State remains coherent and projections remain synchronized.

Collect artifacts:

- screenshot per viewer/screen
- screenshot after refresh proving coherent state
- log excerpt showing state synchronization

### FQT-008: Results Export, Snapshot, and Token Telemetry

Purpose: Verify export controls, snapshots, and token usage telemetry are available and correct.

Requirements covered:

- GUI-006
- GUI-007
- GUI-008
- GUI-015
- GUI-016
- PRJ-016

Preconditions:

- FQT-004 or FQT-005 is `PASS` and the run has completed.

Steps:

1. Open the results export panel.
Expected: Export controls are enabled.
1. Download canonical JSON, STIX, Mermaid, and Markdown artifacts.
Expected: Each download succeeds and the files are non-empty.
1. Open the token usage screen.
Expected: Per-stage and aggregate token telemetry is shown.
1. Export the token usage artifact.
Expected: Export artifact contains the current run data.
1. Save a snapshot of the completed run.
Expected: Snapshot contains inputs, stage results, gates, and metadata.

Collect artifacts:

- downloaded export files
- token usage screenshot and export artifact
- snapshot file and screenshot of saved snapshot state

### FQT-009: Prompt Editor and Prompt History Validation

Purpose: Verify prompt editing and version history controls for authorized users.

Requirements covered:

- GUI-009
- GUI-010
- PRJ-016

Preconditions:

- Authorized access is available.

Steps:

1. Open the prompt editor.
Expected: Current prompts are visible.
1. Edit and save a prompt.
Expected: The saved prompt becomes the current version.
1. Open version history.
Expected: Saved versions are listed.
1. Revert to a prior version.
Expected: The selected version is restored and visible.

Collect artifacts:

- screenshot of prompt editor before and after edit
- screenshot of version history
- log or screenshot proving revert completed

### FQT-010: Documentation and Traceability Validation

Purpose: Verify the manuals, deployment guide, and traceability references match the implemented workflow.

Requirements covered:

- PRJ-016
- GUI-003
- GUI-006
- HITL-008
- HITL-009
- HITL-010
- HITL-011
- all applicable GUI/HITL requirement references in the traceability matrix

Preconditions:

- Current documentation set is available.

Steps:

1. Compare user manual steps to actual GUI behavior.
Expected: Steps and labels match the live workflow.
1. Compare deployment guide steps to the test execution process.
Expected: Deployment steps are executable and consistent.
1. Verify requirement-to-test links in the traceability matrix.
Expected: Each executed case is traceable to requirement IDs.
1. Record any gaps or mismatches as defects.
Expected: Defects are opened with evidence and severity.

Collect artifacts:

- documentation review notes
- traceability matrix excerpt
- evidence links for any mismatches

## 6. Qualification Evidence Report Fields

Each executed case SHALL record:

- Test Case ID
- Tester
- Date/Time
- Environment
- Preconditions status
- Requirement IDs covered
- Step-by-step outcome with `PASS` / `FAIL` / `BLOCK`
- Evidence artifact links
- Defect IDs opened
- Final verdict

## 7. Qualification Result Rules

- `PASS`: all steps and required evidence satisfied
- `FAIL`: one or more required behaviors or artifacts did not meet expectation
- `BLOCK`: execution could not continue because of environment, dependency, or application defect

## 8. Traceability Notes

- Every qualification case SHALL map back to one or more requirement IDs.
- Every failed or blocked step SHALL include an evidence artifact and defect note.
- The qualification execution summary SHALL cite this plan and list the final pass/fail/block state for each case.

## 9. Requirement Coverage Matrix

This matrix is the minimum requirement linkage for the formal qualification execution. Individual execution logs SHOULD list the exact requirement IDs exercised at each step.

| Test Case | Primary Requirement Coverage | Key Controls / Steps Exercised |
|---|---|---|
| FQT-001 | PRJ-016, PRJ-019, PRJ-021, PRJ-023, GUI-003B, GUI-003C | environment readiness, evidence folder, traceability review |
| FQT-002 | PRJ-008, PRJ-016, PRJ-021, PRJ-023, GUI-012, GUI-012A, GUI-013, GUI-014, GUI-016, GUI-017 | provider select, stage checkboxes, valid/invalid connection validation |
| FQT-003 | PRJ-001, PRJ-002, PRJ-003, PRJ-016, GUI-001A, GUI-003, GUI-003A, GUI-016 | input entry, file upload, automatic run start |
| FQT-004 | PRJ-006, PRJ-007, PRJ-016, HITL-001 through HITL-009, GUI-002, GUI-003A, GUI-004, GUI-005, GUI-016 | gate pause, approve, rationale capture, resume |
| FQT-005 | PRJ-006, PRJ-007, HITL-001 through HITL-009, GUI-002, GUI-003A, GUI-005, GUI-017 | reject, save draft, edit, accept, resume |
| FQT-006 | PRJ-013, PRJ-015, HITL-010, HITL-011, HITL-012, GUI-003A, GUI-003C, GUI-006, GUI-007, GUI-008 | conditional trigger, conditional gate decision, publication block/resume |
| FQT-007 | PRJ-016, PRJ-019, GUI-003B, GUI-003C, GUI-004, GUI-005, GUI-016 | stage results, threat review, coherent projections |
| FQT-008 | PRJ-011, PRJ-016, PRJ-017, PRJ-021, GUI-006, GUI-007, GUI-008, GUI-015, GUI-016 | exports, token telemetry, snapshot capture |
| FQT-009 | PRJ-018, PRJ-016 | prompt edit, save, version history, revert |
| FQT-010 | PRJ-016, PRJ-021, PRJ-023, PRJ-026, PRJ-027, PRJ-028, GUI-003, GUI-006, HITL-008, HITL-009, HITL-010, HITL-011 | manual documentation and traceability review |

## 10. Closure Rule

This plan is complete only when every executed qualification case has a recorded verdict, evidence artifacts, and requirement traceability entries in the qualification execution summary.
Document control: keep execution records aligned to this plan and the traceability matrix for every qualification run.

