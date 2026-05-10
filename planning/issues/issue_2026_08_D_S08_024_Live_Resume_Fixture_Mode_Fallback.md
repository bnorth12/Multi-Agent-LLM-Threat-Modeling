# D-S08-024: Live run resumes in fixture mode after session/run restore

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Live run resumes in fixture mode after session/run restore
- Severity: High
- Sprint: 2026-08

## Related Requirements

- GUI-016
- PRJ-016
- PRJ-019

## Reproduction

Start run with xAI live provider, pause at gate, restore or navigate with run_id where `settings_override` is absent, then resume; later stages execute with fixture defaults and token usage only reflects early live stages.

## Fix Reference

- src/threat_modeler/ui/execution.py
- Tests/unit/test_token_usage_runtime.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit/test_token_usage_runtime.py -q --tb=short
```

### Result

Run recovery now restores persisted runtime settings into session override, preventing silent live-to-fixture fallback during pause/resume across reload or navigation.

### Tracker Disposition

2026-05-08 BN: Prevents silent live-to-fixture fallback across reload and HITL resume.

## Resolution

- Status: Resolved
- Source of truth: `planning/issues/Sprint_2026_08_Issue_Tracker.md`
- Closure type: Tracker-to-issue backfill

## Metadata

- Issue ID: D-S08-024
- Sprint: 2026-08
- Status: Resolved
