# D-S09-003: Mermaid Diagram Viewer

## Issue Summary

Add an in-app Mermaid viewer for generated diagram artifacts, including rendered output and source-text inspection.

## Related Requirements

- GUI-020
- PRJ-016

## Severity

Medium - Feature enhancement for visual architecture review workflows.

## Acceptance Criteria

- [x] Add a Mermaid viewer screen in UI navigation.
- [x] Render available Mermaid diagrams (Level 0/1/2 where present).
- [x] Provide toggle between rendered diagram and Mermaid source text.
- [x] Display clear error state if Mermaid source cannot be rendered.
- [x] Viewer content remains consistent with Mermaid export artifact.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_mermaid_viewer_screen.py -q --tb=short
```

### Expected Result

- Rendered diagrams and source views are available and synchronized.
- Invalid Mermaid is surfaced with explicit error messaging.

## Status

Resolved

## Implementation Notes (2026-05-10)

- Added UI screen: `src/threat_modeler/ui/screens/mermaid_viewer.py`
- Added display-model correctness tests: `Tests/integration/test_mermaid_viewer_screen.py`
- Verified in automated non-manual sweep: `406 passed, 11 deselected`.

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout
