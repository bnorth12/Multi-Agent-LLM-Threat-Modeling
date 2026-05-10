# D-S08-023: Token Usage table horizontal overflow discoverability

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Token Usage table horizontal overflow discoverability
- Severity: Low
- Sprint: 2026-08

## Related Requirements

- SCR-014
- GUI-015
- PRJ-016

## Reproduction

On Token Usage screen, Usage by Stage columns can be clipped on narrower viewport without obvious horizontal scrolling affordance.

## Fix Reference

- src/threat_modeler/ui/screens/token_usage.py
- Tests/unit/test_token_usage_runtime.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit/test_token_usage_runtime.py -q --tb=short
```

### Result

Usage by Stage dataframe now renders with fixed width (`width=1400`, `use_container_width=False`) so Streamlit shows a bottom horizontal scrollbar when viewport is narrower than table width.

### Tracker Disposition

2026-05-08 BN: SCR-014 usability fix.

## Resolution

- Status: Resolved
- Source of truth: `planning/issues/Sprint_2026_08_Issue_Tracker.md`
- Closure type: Tracker-to-issue backfill

## Metadata

- Issue ID: D-S08-023
- Sprint: 2026-08
- Status: Resolved
