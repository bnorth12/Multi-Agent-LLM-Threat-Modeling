# D-S09-006: Component and Component-File Version Governance

## Issue Summary

S09 must introduce firm version governance so each major component has a semantic version and each component-owned file has a deterministic file-level version identifier that can be traced in RC release evidence.

## Related Requirements

- PRJ-021
- PRJ-022
- GUI-024

## Severity

Medium - Release traceability and auditability requirement for RC and GA.

## Scope

1. Define and generate a component semantic version manifest.
2. Define and generate a component-file version inventory.
3. Surface version inventories in Results Export and Snapshot Manager.
4. Include both inventories in release evidence artifacts.

## Acceptance Criteria

- [x] Component semantic version manifest generated for RC1.
- [x] Deterministic component-file version inventory generated for RC1.
- [x] Mapping between file inventory and component manifest is complete.
- [x] GUI displays component/file versions for active run evidence contexts.
- [x] Release evidence includes both version artifacts.

## Verification Evidence

### Planned Test Commands

```powershell
.venv\Scripts\python.exe -m pytest Tests/integration/test_component_version_manifest.py -q --tb=short
.venv\Scripts\python.exe -m pytest Tests/integration/test_component_file_version_inventory.py -q --tb=short
.venv\Scripts\python.exe -m pytest Tests/integration/test_version_inventory_visibility.py -q --tb=short
```

### Expected Result

- Version artifacts are generated, internally consistent, and visible in GUI release evidence views.

## Status

Resolved

## Implementation Notes (2026-05-10)

- Added generator module: `src/threat_modeler/ui/version_governance.py`.
- Added version inventory visibility in `src/threat_modeler/ui/screens/results_export.py` and `src/threat_modeler/ui/screens/snapshot_manager.py`.
- Added correctness tests: `Tests/integration/test_component_version_manifest.py`, `Tests/integration/test_component_file_version_inventory.py`, `Tests/integration/test_version_inventory_visibility.py`.
- Verified in automated non-manual sweep: `406 passed, 11 deselected`.

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: RC release traceability enhancement
