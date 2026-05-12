# D-S09-011: Pipeline Configuration Stage Selection UI

## Issue Summary

The Pipeline Configuration screen's stage selection widget is not functioning properly. Currently, only 2 stages are visible in the selector, and users cannot modify the enabled stages list. This blocks legitimate pipeline configuration changes and prevents manual RC validation.

## Related Requirements

- GUI-012 (Model Provider Selection Screen / Pipeline Configuration)
- PRJ-021, PRJ-022 (Release Governance)

## Severity

Critical - Blocks manual RC validation (D-S09-008) and prevents users from configuring which pipeline stages to execute.

## Scope

1. Replace current multiselect dropdown with checkbox-based UI component.
2. Display all 9 pipeline stages (agent_01 through agent_09) with human-readable labels.
3. Each stage shall have a checkbox to enable/disable it.
4. Persist stage selection changes to RuntimeSettings.pipeline.enabled_stage_ids.
5. Require at least 1 stage to remain enabled (validation).

## Root Cause

The current multiselect widget uses `st.multiselect()` which has rendering issues or incomplete options binding in the form context, resulting in only 2 stages displaying and no ability to modify the selection.

## Acceptance Criteria

- [x] All 9 stages (agent_01 through agent_09) are visible in the Configuration form.
- [x] Each stage has a checkbox showing current enabled state.
- [x] User can enable/disable stages by checking/unchecking boxes.
- [x] Stage selection persists after "Apply Settings" is clicked.
- [x] Validation requires at least 1 stage to be enabled.
- [x] Stage selection survives screen reloads and settings recovery.

## Verification Evidence

### User Interaction Test

1. Open Pipeline Configuration screen
2. Verify all 9 stages visible with checkboxes and human-readable labels
3. Disable a stage by unchecking its box
4. Enable an additional stage
5. Click "Apply Settings"
6. Reload the page / navigate away and back
7. Verify stage selection is persisted correctly

### Manual Testing Complete

- [x] All 9 stages now visible with checkbox controls
- [x] Stage selection persists across Apply Settings
- [x] Configuration screen correctly reflects persisted state on reload

## Status

Resolved

## Implementation Notes (2026-05-10)

### Changes Made

1. **File: `src/threat_modeler/ui/screens/config.py`**
   - Replaced `st.multiselect()` with checkbox-based form area
   - Added individual `st.checkbox()` for each of the 9 stages
   - Stages arranged in 3 columns for better layout
   - Each checkbox labeled with human-readable stage description
   - Validation ensures at least 1 stage remains enabled
   - Stage selections properly mapped to `RuntimeSettings.pipeline.enabled_stage_ids`

2. **File: `Requirements/10_GUI_Requirements.md`**
   - Clarified GUI-012 acceptance criteria to explicitly include "pipeline stage selection via checkboxes"
   - Added new requirement GUI-012A for explicit stage selection functionality

### Test Results

- Pipeline Configuration screen now displays all 9 stages with working checkbox controls
- Stage selection changes persist after Apply Settings
- Form validation prevents saving with no stages enabled
- Configuration survives page reloads

### Deployment

- Feature branch: `feature/sprint-2026-09-kickoff`
- Commit: `b7466d0` (Fixes D-S09-011: Replace pipeline stage selection multiselect with checkbox-based UI)
- Pushed to origin: 2026-05-10
- Manual RC validation (D-S09-008) can now proceed safely

### User Verification Complete

- ✅ Pipeline Configuration screen accessed and verified
- ✅ All 9 stages visible with checkbox controls and human-readable labels
- ✅ 3-column layout renders cleanly and accessibly
- ✅ Stage selection controls are interactive and ready for manual testing
