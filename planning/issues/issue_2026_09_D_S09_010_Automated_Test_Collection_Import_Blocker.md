# D-S09-010: Automated Test Collection Import Blocker

## Issue Summary

Automated non-manual RC gate sweep encountered blockers in two phases:

1. Initial pytest collection blocked because `Tests/e2e/test_live_llm_validation.py` imported `threat_modeler.framework`, which does not exist in the current package layout.
1. After import-path correction, execution blocked by `TypeError` in `Tests/e2e/test_browser_run_validation.py` where token-usage validation attempted `sum()` over mixed numeric/string values.

## Related Requirements

- VS-008

## Severity

Medium - blocks automated clean-pass gate needed before manual RC validation.

## Reproduction

1. Run:

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit Tests/integration Tests/e2e -m "not llm_live" -q --tb=short
```

1. Observe collection error:

- `ModuleNotFoundError: No module named 'threat_modeler.framework'`

## Acceptance Criteria

- [x] Automated test sweep no longer fails at collection for this import.
- [x] Live validation tests import `FrameworkOrchestrator` from the correct module path.
- [x] Automated non-manual test sweep proceeds to execution stage.
- [x] Browser run validation token-usage checks sum numeric token fields only.
- [x] Automated non-manual sweep completes with no failures.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit Tests/integration Tests/e2e -m "not llm_live" -q --tb=short
```

### Expected Result

- Pytest collection succeeds without `threat_modeler.framework` import errors.
- Browser validation tests execute without token-usage `TypeError`.

## Status

Resolved

## Metadata

- Sprint: 2026-09
- Created: 2026-05-10
- Source: Automated clean-pass gate execution

## Resolution Notes

- 2026-05-10 BN: Fixed collection imports in `Tests/e2e/test_live_llm_validation.py` for orchestrator and adapter class paths.
- 2026-05-10 BN: Fixed browser token validation summation to include numeric token fields only in `Tests/e2e/test_browser_run_validation.py`.
- 2026-05-10 BN: Verified with automated sweep: `406 passed, 11 deselected`.
