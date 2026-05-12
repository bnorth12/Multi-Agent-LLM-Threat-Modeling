# D-S09-004: STRIDE Threat Model Viewer and Export

## Issue Summary

Add a dedicated STRIDE threat model viewer and a standalone STRIDE export artifact from the GUI.

## Related Requirements

- GUI-021
- GUI-022
- PRJ-016

## Severity

Medium - Feature enhancement for risk review, reporting, and downstream workflow integration.

## Acceptance Criteria

- [x] Add STRIDE viewer screen in UI navigation.
- [x] Display per-interface STRIDE scores and justifications.
- [x] Show linked threats for each interface.
- [x] Support sorting by score and interface.
- [x] Add standalone STRIDE export action (JSON or CSV) in Results Export.
- [x] Export payload matches data shown in STRIDE viewer.

## Verification Evidence

### Planned Test Commands

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_stride_viewer_screen.py -q --tb=short
```

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_stride_export_artifact.py -q --tb=short
```

### Expected Result

- STRIDE viewer rows match canonical interface STRIDE fields.
- STRIDE export is downloadable and schema-valid.

## Status

Resolved

## Implementation Notes (2026-05-10)

- Added UI screen: `src/threat_modeler/ui/screens/stride_viewer.py`
- Added STRIDE export helpers in `src/threat_modeler/ui/runtime_io.py`
- Added correctness tests: `Tests/integration/test_stride_viewer_screen.py`, `Tests/integration/test_stride_export_artifact.py`
- Verified in automated non-manual sweep: `406 passed, 11 deselected`.

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout
