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

- [ ] Add STRIDE viewer screen in UI navigation.
- [ ] Display per-interface STRIDE scores and justifications.
- [ ] Show linked threats for each interface.
- [ ] Support sorting by score and interface.
- [ ] Add standalone STRIDE export action (JSON or CSV) in Results Export.
- [ ] Export payload matches data shown in STRIDE viewer.

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

Open

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout
