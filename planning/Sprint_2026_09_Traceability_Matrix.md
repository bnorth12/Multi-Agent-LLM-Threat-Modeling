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
| 1 | GUI-018 | STIX Threat Model Viewer | D-S09-001 | Resolved | BN | Tests/integration/test_stix_viewer_screen.py | 8 tests passing | Included in automated non-manual sweep: 406 passed, 11 deselected |
| 2 | GUI-019 | Canonical Graph Viewer | D-S09-002 | Resolved | BN | Tests/integration/test_canonical_graph_viewer.py | 4 tests passing | Display-model tests validate hierarchy and trust-boundary values |
| 3 | GUI-020 | Mermaid Diagram Viewer | D-S09-003 | Resolved | BN | Tests/integration/test_mermaid_viewer_screen.py | 3 tests passing | Source toggle + explicit invalid-source behavior validated |
| 4 | GUI-021 | STRIDE Threat Model Viewer | D-S09-004 | Resolved | BN | Tests/integration/test_stride_viewer_screen.py | 3 tests passing | Per-interface STRIDE rows/justifications validated against expected data |
| 5 | GUI-022 | STRIDE Threat Model Export | D-S09-004 | Resolved | BN | Tests/integration/test_stride_export_artifact.py | 2 tests passing | JSON/CSV exports validated for expected fields and values |
| 6 | GUI-023 | Results Export Quick Preview Functionality | D-S09-005 | Resolved | BN | Tests/integration/test_results_export_quick_preview.py | 2 tests passing | Preview payloads validated against current run artifacts |
| 7 | GUI-024 | Component and File Version Visibility | D-S09-006 | Resolved | BN | Tests/integration/test_version_inventory_visibility.py | 2 tests passing | Version inventories displayed and cross-checked for consistency |
| 8 | PRJ-021 | Component Semantic Version Authority | D-S09-006 | Resolved | BN | Tests/integration/test_component_version_manifest.py | 2 tests passing | Component semantic manifest generated and validated |
| 9 | PRJ-022 | Component File Version Traceability | D-S09-006 | Resolved | BN | Tests/integration/test_component_file_version_inventory.py | 2 tests passing | Deterministic file inventory hashes and ordering validated |
| 10 | GUI-025 | Markdown Viewer and Editor | D-S09-009 | Resolved | BN | Tests/integration/test_markdown_viewer_editor.py | 14 tests passing | Markdown display/edit/preview/persistence validated |

## Release Documentation Workstream

| # | Requirement ID | Requirement Name | Issue ID | Issue Status | Assigned To | Test File | Verification Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R1 | PRJ-011 | Export Artifact Set | D-S09-007 | Resolved | BN | Tests/e2e/test_release_deployment_guide_presence.py | Guide updated; automated evidence recorded | RC1 deployment guide completed and aligned to automated-first sequencing |
| R2 | VS-008 | Manual RC Validation Campaign | D-S09-008 | In Progress | BN | planning/Test_Execution_Summary_Sprint_2026_09.md | Automated prerequisite complete (`406 passed, 11 deselected`) | Full manual validation evidence pending user-driven campaign execution |

---

## Notes

- Seeded on 2026-05-09 during S08 closeout.
- Requirement definitions are in Requirements/10_GUI_Requirements.md.
- Issue source of truth is planning/issues/Sprint_2026_09_Issue_Tracker.md.

## S09 Phase Verification Cadence

- Requirements Phase: verify requirement text, acceptance criteria, and issue mappings for GUI-018 through GUI-025, PRJ-021, PRJ-022, and VS-008.
- Implementation Phase: verify test case mappings, evidence paths, and status updates for all S09 baseline requirements/features.
- Closure Phase: run traceability audit and confirm all baseline entries have verification status and evidence references.
