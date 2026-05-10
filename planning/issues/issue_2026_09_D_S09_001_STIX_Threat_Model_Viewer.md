# D-S09-001: STIX Threat Model Viewer

## Issue Summary

Add a dedicated GUI viewer for the STIX threat model bundle so analysts can inspect STIX objects without leaving the app or parsing raw JSON manually.

## Related Requirements

- GUI-018
- PRJ-016

## Severity

Medium - Feature enhancement for analyst workflow and verification clarity.

## Acceptance Criteria

- [ ] Add a STIX viewer screen in the UI navigation.
- [ ] Render STIX objects grouped by object type.
- [ ] Show object counts by type.
- [ ] Provide simple filter/search by object type and name/id.
- [ ] Keep parity with STIX export artifact content.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_stix_viewer_screen.py -q --tb=short
```

### Expected Result

- Viewer renders grouped STIX content from completed run.
- Filtering and object counts are correct.

## Status

Open

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout
