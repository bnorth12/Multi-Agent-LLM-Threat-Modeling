# D-S08-007: Home dashboard missing live execution telemetry

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Home dashboard live monitoring
- Severity: Medium
- Sprint: 2026-08

## Related Requirements

- PRJ-016, GUI-003, SCR-002

## Reproduction

During background execution, Home view did not expose full live execution status and elapsed telemetry.

## Fix Reference

src/threat_modeler/ui/screens/home.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

Execution status, elapsed, paused gate warning, and runtime error now rendered on Home screen.

### Tracker Disposition

2026-05-07 BN: Added live execution status block to home.py render().

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

- Issue ID: D-S08-007
- Sprint: 2026-08
- Status: Resolved
