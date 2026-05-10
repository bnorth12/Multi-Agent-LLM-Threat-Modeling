# D-S09-001: STIX Threat Model Viewer

## Issue Summary

Add a dedicated GUI viewer for the STIX threat model bundle so analysts can inspect STIX objects without leaving the app or parsing raw JSON manually.

## Related Requirements

- GUI-018
- PRJ-016

## Severity

Medium - Feature enhancement for analyst workflow and verification clarity.

## Acceptance Criteria

- [x] Add a STIX viewer screen in the UI navigation.
- [x] Render STIX objects grouped by object type.
- [x] Show object counts by type.
- [x] Provide simple filter/search by object type and name/id.
- [x] Keep parity with STIX export artifact content.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_stix_viewer_screen.py -q --tb=short
```

### Expected Result

- Viewer renders grouped STIX content from completed run.
- Filtering and object counts are correct.
- Automated integration tests pass for extraction, grouping, filtering, and summary rendering logic.

## Status

In Progress

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout

## Implementation Notes (2026-05-10)

- Added UI screen: `src/threat_modeler/ui/screens/stix_viewer.py`
- Added navigation entry in `src/threat_modeler/ui/app.py`
- Added automated tests: `Tests/integration/test_stix_viewer_screen.py`
