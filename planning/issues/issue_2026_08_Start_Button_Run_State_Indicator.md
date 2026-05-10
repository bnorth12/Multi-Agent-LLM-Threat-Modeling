# Issue: Start Button Run-State Indicator

**Issue ID**: S08-UI-001
**Tracker Defect ID**: D-S08-008
**Tracker Workstream ID**: S08-4
**Sprint**: 2026-08
**Status**: IN PROGRESS
**Created**: 2026-05-06

## Overview

After the user clicks **â–¶ Start Threat Model Run**, the button label and appearance do not change. The only indication that the pipeline is running is the Streamlit spinner in the top-right banner, which is easy to miss. The button should visibly reflect the in-progress state so users have immediate, unambiguous feedback that the run has started.

## Problem Statement

The current **â–¶ Start Threat Model Run** button:

- Remains fully clickable and unchanged after being pressed.
- Gives no inline indication that work is in progress.
- Could be double-clicked, potentially spawning a second run if session state allows it.

Observed during S08 browser walkthrough (2026-05-06): after clicking Start, the UI was silent for several seconds with only the top-bar spinner as feedback.

## Acceptance Criteria

1. Within one Streamlit render cycle of the run starting, the button area in `input_entry.py` changes to a disabled state with a label such as `â³ Running â€” see Run Dashboard` (or equivalent).
2. The button remains disabled and shows the in-progress label for the entire duration of an active run (`run_id` present in session state and pipeline not yet completed or halted).
3. When the run completes or is halted, the button reverts to the normal `â–¶ Start Threat Model Run` label and becomes enabled again (assuming a new run can be started).
4. No second run can be triggered by a second click while a run is in progress.

## Implementation Notes

- The run state is tracked in `st.session_state["run_id"]` and `st.session_state["pipeline_state"]`.
- Check `st.session_state.get("run_id")` in `input_entry.py` before rendering the start button; if truthy, render the button as `disabled=True` with the in-progress label.
- The pipeline completion/halt state may be represented by an error flag or by checking stage statuses in `pipeline_state`; identify the correct sentinel and use it to re-enable the button.
- Consider also greying out the form inputs (system name, file uploader) while a run is active to further prevent accidental modification.

## Files Affected

- `src/threat_modeler/ui/screens/input_entry.py` â€” button render logic (around the `start_clicked` block)

## Requirement Links

- SCR-004 (Input Entry run submission)
- SCR-001 (Run Dashboard feedback)

## Priority

Low â€” UX polish; does not block pipeline correctness.

## Disposition Notes

- 2026-05-07 BN: **Partial fix implemented** in [src/threat_modeler/ui/screens/input_entry.py](../../src/threat_modeler/ui/screens/input_entry.py).
	- Start action is disabled while a run is active (`is_execution_active()` gate).
	- Active-run warning banner is shown with run identifier prefix.
	- Second-run trigger during active execution is blocked.
- 2026-05-07 BN: **Remaining closure item**: add explicit in-button running label text (for example, `â³ Running â€” see Run Dashboard`) and re-verify all acceptance criteria.

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

- Start button disables while active execution is detected.
- Active-run warning and duplicate-start prevention behavior verified in Sprint 2026-08 browser validation.

## Closure Evidence Template

Use this block for future closure updates.

- Resolution date:
- Implementation commit or PR:
- Verification command(s):
- Verification result summary (include pass counts):
- Evidence artifact path(s):
- Reviewer or approver initials:

