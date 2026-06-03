# Test Execution Summary — Sprint 2026-09

## 1. Scope

This summary records automated and manual test evidence for Sprint 2026-09.

Validation sequencing policy:

1. Clean automated pass across RC-included features.
1. Manual RC campaign execution after automated gate passes.

## 2. Automated Gate Evidence

Execution date: 2026-05-10

Command:

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit Tests/integration Tests/e2e -m "not llm_live" -q --tb=short
```

Result:

- Passed: 406
- Deselected: 11
- Failed: 0
- Errors: 0

Notes:

- Automated gate includes display-correctness tests for graphs, plots, charts, and artifact previews.
- Token/browser validation blockers were resolved under D-S09-010 before final passing sweep.

## 3. Feature-Level Automated Evidence

- GUI-018: `Tests/integration/test_stix_viewer_screen.py` (8 passed)
- GUI-019: `Tests/integration/test_canonical_graph_viewer.py` (4 passed)
- GUI-020: `Tests/integration/test_mermaid_viewer_screen.py` (3 passed)
- GUI-021: `Tests/integration/test_stride_viewer_screen.py` (3 passed)
- GUI-022: `Tests/integration/test_stride_export_artifact.py` (2 passed)
- GUI-023: `Tests/integration/test_results_export_quick_preview.py` (2 passed)
- GUI-024/PRJ-021/PRJ-022:
  - `Tests/integration/test_component_version_manifest.py` (2 passed)
  - `Tests/integration/test_component_file_version_inventory.py` (2 passed)
  - `Tests/integration/test_version_inventory_visibility.py` (2 passed)
- GUI-025: `Tests/integration/test_markdown_viewer_editor.py` (14 passed)

## 4. Manual RC Campaign Status

Status: Pending (not started)

Manual execution MUST follow `Tests/Test_Plan.md` sections TC-RC-001 through TC-RC-011 and record PASS/FAIL/BLOCK outcomes with evidence links.

## 5. Exit Status

- Automated entry gate: PASS
- Manual RC campaign: PENDING
- RC publication decision: PENDING manual evidence completion
