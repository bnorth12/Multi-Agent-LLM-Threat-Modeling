# D-S08-022: Last Prompt dark-theme readability

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Last Prompt dark-theme readability
- Severity: Medium
- Sprint: 2026-08

## Related Requirements

- SCR-015
- GUI-003
- PRJ-016

## Reproduction

Open Last Prompt screen with Appearance=Dark; disabled System Prompt and User Message text has low contrast against dark background.

## Fix Reference

- src/threat_modeler/ui/screens/last_prompt.py
- Tests/unit/test_last_prompt_runtime.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit/test_last_prompt_runtime.py -q --tb=short
```

### Result

Added dark-theme scoped CSS override for disabled textarea text (`color` and `-webkit-text-fill-color`) to improve readability while keeping fields read-only. Verified in live Streamlit session with dark appearance.

### Tracker Disposition

2026-05-08 BN: SCR-015 usability fix for troubleshooting workflows.

## Resolution

- Status: Resolved
- Source of truth: `planning/issues/Sprint_2026_08_Issue_Tracker.md`
- Closure type: Tracker-to-issue backfill

## Metadata

- Issue ID: D-S08-022
- Sprint: 2026-08
- Status: Resolved
