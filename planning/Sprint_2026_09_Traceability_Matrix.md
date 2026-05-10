# Sprint 2026-09 Traceability Matrix

**Sprint**: 2026-09
**Start Date**: TBD
**End Date**: TBD
**Status**: Planned

---

## Overview

This matrix tracks bidirectional traceability between requirements, issues, code, and tests for Sprint 2026-09.

**Completion Target**: 100%
**Current Status**: 0/10 requirements implemented

---

## Traceability Matrix

| # | Requirement ID | Requirement Name | Issue ID | Issue Status | Assigned To | Test File | Verification Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | GUI-018 | STIX Threat Model Viewer | D-S09-001 | In Progress | BN | Tests/integration/test_stix_viewer_screen.py | 8 tests passing | Implemented dedicated STIX viewer with grouped objects, counts, and filter/search |
| 2 | GUI-019 | Canonical Graph Viewer | D-S09-002 | In Progress | BN | Tests/integration/test_canonical_graph_viewer.py | Pending run | Viewer implemented; display-model tests validate hierarchy and trust-boundary fields |
| 3 | GUI-020 | Mermaid Diagram Viewer | D-S09-003 | In Progress | BN | Tests/integration/test_mermaid_viewer_screen.py | Pending run | Viewer implemented with source toggle and explicit invalid-syntax error state |
| 4 | GUI-021 | STRIDE Threat Model Viewer | D-S09-004 | In Progress | BN | Tests/integration/test_stride_viewer_screen.py | Pending run | Viewer implemented with sortable interface STRIDE rows and justification visibility |
| 5 | GUI-022 | STRIDE Threat Model Export | D-S09-004 | In Progress | BN | Tests/integration/test_stride_export_artifact.py | Pending run | Standalone STRIDE JSON/CSV exports added to Results Export |
| 6 | GUI-023 | Results Export Quick Preview Functionality | D-S09-005 | In Progress | BN | Tests/integration/test_results_export_quick_preview.py | Pending run | Quick preview coverage expanded to include STRIDE and version governance artifacts |
| 7 | GUI-024 | Component and File Version Visibility | D-S09-006 | In Progress | BN | Tests/integration/test_version_inventory_visibility.py | Pending run | Version inventories visible in Results Export and Snapshot Manager |
| 8 | PRJ-021 | Component Semantic Version Authority | D-S09-006 | In Progress | BN | Tests/integration/test_component_version_manifest.py | Pending run | Component semantic version manifest generator implemented |
| 9 | PRJ-022 | Component File Version Traceability | D-S09-006 | In Progress | BN | Tests/integration/test_component_file_version_inventory.py | Pending run | Deterministic component-file inventory generator implemented |
| 10 | GUI-025 | Markdown Viewer and Editor | D-S09-009 | In Progress | BN | Tests/integration/test_markdown_viewer_editor.py | 14 tests passing | Implementation: markdown display, edit, preview, export, snapshot integration complete |

## Release Documentation Workstream

| # | Requirement ID | Requirement Name | Issue ID | Issue Status | Assigned To | Test File | Verification Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R1 | PRJ-011 | Export Artifact Set | D-S09-007 | Open | TBD | Tests/e2e/test_release_deployment_guide_presence.py | Pending | RC1 deployment guide included as release artifact deliverable |
| R2 | VS-008 | Manual RC Validation Campaign | D-S09-008 | Open | TBD | planning/Test_Execution_Summary_Sprint_2026_09.md | Pending | Full manual validation evidence runs after clean automated pass for all RC-included features |

---

## Notes

- Seeded on 2026-05-09 during S08 closeout.
- Requirement definitions are in Requirements/10_GUI_Requirements.md.
- Issue source of truth is planning/issues/Sprint_2026_09_Issue_Tracker.md.

## S09 Phase Verification Cadence

- Requirements Phase: verify requirement text, acceptance criteria, and issue mappings for GUI-018 through GUI-025, PRJ-021, PRJ-022, and VS-008.
- Implementation Phase: verify test case mappings, evidence paths, and status updates for all S09 baseline requirements/features.
- Closure Phase: run traceability audit and confirm all baseline entries have verification status and evidence references.
