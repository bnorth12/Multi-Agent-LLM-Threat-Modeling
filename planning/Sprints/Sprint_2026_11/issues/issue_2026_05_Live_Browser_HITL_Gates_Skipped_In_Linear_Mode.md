# D-S09-017: Live Browser Smoke Skips Mandatory HITL Gates in Linear Execution Mode

## Issue Summary

The visible-browser FQT smoke run for the UAS Weapon System completes stages 01 through 09 without pausing at the mandatory HITL gate after stage 02. The orchestrator contains mandatory post-stage gate logic, but the live browser path is starting runs in the linear execution branch, which never opens those gates.

This causes the dashboard to move from stage 02 directly to stage 03 with no human-in-the-loop pause, so the Threat Review screen shows no gate approval opportunity when the run should stop for review.

## Related Requirements

- HITL-001
- HITL-002
- HITL-003
- HITL-004
- HITL-005
- GUI-002
- GUI-002A

## Severity

**Critical** - mandatory review checkpoints are bypassed during live validation, so the smoke run cannot prove the HITL workflow.

## Reproduction

- Launch the visible-browser smoke runner with the UAS Weapon System fixture bundle and a live LLM provider.
- Enable HITL gates in Pipeline Configuration.
- Upload the UAS top-level description plus the Alpha, Bravo, Charlie, Ground Maintenance, and Avionics component fixtures.
- Start the run and watch the dashboard progress past stage 02.
- Observe that the run transitions directly into stage 03 with no pause at the mandatory HITL checkpoint.
- Open Threat Review and observe that no gate approval is recorded at the expected boundary.

## Expected Behavior

When HITL gates are required, the pipeline SHALL pause after the mandatory stages and open the corresponding review gate before proceeding to the next stage.

## Current Behavior

The live browser smoke run proceeds through the linear pipeline path, which completes the planned stages without invoking the mandatory post-stage HITL gate openings.

## Scope

- Default runtime settings should use the HITL-capable execution branch for live runs.
- The live-browser smoke should continue to assert the mandatory gate pause after stage 02.
- Add or update regression coverage for the stage 02 to stage 03 gate transition.

## Acceptance Criteria

- [ ] Live browser smoke pauses at the mandatory HITL gate after stage 02.
- [ ] Threat Review shows the paused gate and allows approval or rejection.
- [ ] The run resumes only after a gate decision is submitted.
- [ ] Regression coverage prevents future bypass of mandatory HITL gates in live runs.

## Status

In Progress

## Notes

- Root cause identified in the live execution path: the linear branch does not open mandatory post-stage gates.
- Fix applied by switching default runtime settings to `langgraph-compatible` execution mode so the HITL gate logic is exercised.
