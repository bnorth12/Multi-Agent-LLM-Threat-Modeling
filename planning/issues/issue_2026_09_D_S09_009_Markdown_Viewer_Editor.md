# D-S09-009: Markdown Viewer and Editor

## Issue Summary

Add an in-app markdown viewer and editor so users can open, edit, preview, and save markdown files produced or managed by the tool during requirements, implementation, and release preparation workflows.

## Related Requirements

- GUI-025
- PRJ-016

## Severity

Medium - Required for in-workflow documentation maintenance and reduced context switching.

## Scope

1. Add markdown file selection/open action for tool-managed markdown files.
1. Add markdown source editor with save/cancel behavior.
1. Add rendered markdown preview mode.
1. Add save-state and change-state feedback (saved/unsaved/error).
1. Add basic safeguards (confirm before discard, block unsafe path writes if applicable).

## Acceptance Criteria

- [x] User can open supported markdown files from within GUI.
- [x] User can edit markdown content and save changes.
- [x] Rendered preview reflects current saved content.
- [x] UI indicates unsaved changes and save outcome.
- [x] Reopen confirms persisted updates.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_markdown_viewer_editor.py -q --tb=short
```

### Expected Result

- Markdown viewer/editor functions correctly for open, edit, preview, and save flow with persisted results.

## Status

Resolved

## Implementation Notes (2026-05-10)

- Added UI screen: `src/threat_modeler/ui/screens/markdown_viewer.py`.
- Added snapshot persistence for markdown edits in `src/threat_modeler/ui/runtime_io.py` and `src/threat_modeler/ui/screens/snapshot_manager.py`.
- Added correctness tests: `Tests/integration/test_markdown_viewer_editor.py`.
- Verified in automated non-manual sweep: `406 passed, 11 deselected`.

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: Added per S09 scope update for in-app markdown maintenance
