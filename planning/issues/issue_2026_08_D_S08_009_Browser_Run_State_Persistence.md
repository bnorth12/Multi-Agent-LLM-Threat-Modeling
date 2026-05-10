# D-S08-009: Browser run state persistence lost on reload

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Browser run state persistence
- Severity: High
- Sprint: 2026-08

## Related Requirements

- PRJ-016, GUI-003C, SCR-002

## Reproduction

In live UI run, page reload returned to Home with no active run and no gate records.

## Fix Reference

src/threat_modeler/ui/execution.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

Process-local run registry persists across reruns; query-param restoration verified.

### Tracker Disposition

2026-05-07 BN: Process-local registry plus query param persistence added; reload recovery verified.

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

- Issue ID: D-S08-009
- Sprint: 2026-08
- Status: Resolved
