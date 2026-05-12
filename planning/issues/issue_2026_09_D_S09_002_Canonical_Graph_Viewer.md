# D-S09-002: Canonical Graph Viewer

## Issue Summary

Add a dedicated canonical graph viewer that renders hierarchy and relationships from the generated canonical graph artifact.

## Related Requirements

- GUI-019
- PRJ-016

## Severity

Medium - Feature enhancement for analyst review and architecture validation.

## Acceptance Criteria

- [x] Add a canonical graph viewer screen in the UI navigation.
- [x] Display system, subsystem, component, function, and interface hierarchy.
- [x] Allow expansion/collapse of hierarchy nodes.
- [x] Show trust boundary crossing metadata on interfaces.
- [x] Ensure viewer content matches canonical graph export.

## Verification Evidence

### Planned Test Command

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_canonical_graph_viewer.py -q --tb=short
```

### Expected Result

- Hierarchy renders and is navigable.
- Interface and trust-boundary details are visible and accurate.

## Status

Resolved

## Implementation Notes (2026-05-10)

- Added UI screen: `src/threat_modeler/ui/screens/canonical_graph_viewer.py`
- Added display-model correctness tests: `Tests/integration/test_canonical_graph_viewer.py`
- Verified in automated non-manual sweep: `406 passed, 11 deselected`.

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: S09 planning seed during S08 closeout
