# D-S08-012: HITL resume button invoked blocking synchronous path

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: HITL resume pipeline action
- Severity: High
- Sprint: 2026-08

## Related Requirements

- HITL-002, PRJ-016, GUI-002

## Reproduction

Resume Pipeline button called local synchronous path; pipeline ran on UI thread and dashboard did not update during resume.

## Fix Reference

src/threat_modeler/ui/screens/threat_review.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

Button now uses resume_pipeline_execution background path with registry integration.

### Tracker Disposition

2026-05-07 BN: Dead import converted to active call site matching start path.

## Resolution

- Status: Resolved
- Source of truth: `planning/issues/Sprint_2026_08_Issue_Tracker.md`
- Closure type: Tracker-to-issue backfill

## Closure Evidence Template

Use this block for future closure updates.

- Resolution date:
- Implementation commit or PR:
- Verification command(s):
- Verification result summary (include pass counts):
- Evidence artifact path(s):
- Reviewer or approver initials:

## Metadata

- Issue ID: D-S08-012
- Sprint: 2026-08
- Status: Resolved
