# D-S08-018: Live run timeout after Gate 1 resume

## Issue Summary

Backfilled from `planning/issues/Sprint_2026_08_Issue_Tracker.md` defect log.

- Area: Live run provider timeout after resume
- Severity: High
- Sprint: 2026-08

## Related Requirements

- PRJ-008, INT-012, INT-015

## Reproduction

Browser E2E run failed after Gate 1 resume with RuntimeError timeout after 3 attempts at Stage 3.

## Fix Reference

src/threat_modeler/llm/openai_compatible_adapter.py and Tests/unit/test_openai_compatible_adapter.py

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

Timeout default raised to 180s, attempts configurable, 19-test regression added, full suite 310 passed, live rerun completed all 9 stages.

### Tracker Disposition

2026-05-08 BN: End-to-end verified; regression and live rerun passed.

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

- Issue ID: D-S08-018
- Sprint: 2026-08
- Status: Resolved
