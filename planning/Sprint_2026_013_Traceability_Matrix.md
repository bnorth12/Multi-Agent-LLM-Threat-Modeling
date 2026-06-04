# Sprint 2026-013 Traceability Matrix

| Sprint Issue | Requirement ID | Verification Method | Evidence Artifact |
|---|---|---|---|
| S13-001 | ORCH-001 | Automated traceability verification | scripts/verify_sprint_traceability.py --sprint 2026_013 |
| S13-001 | INT-005 | Blocker backlog generation | scripts/run_traceability_blocker_planning.py --sprint 2026_013 |
| S13-002 | ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006 | Administration control implementation verification | scripts/verify_administration_controls.py |
| S13-003 | ADM-001, ADM-002, ADM-003, ADM-004, ADM-005, ADM-006 | Unit test evidence for administration controls | Tests/unit/test_administration_controls.py |
| S13-004 | PRJ-005, PRJ-026 | Architecture/design disposition workpack evidence | independent_reviews/latest/remediation_issue_drafts_latest.md |

## Code Implementation Trace Backfill

These rows capture the 15 currently reachable implementation modules that can be traced to an existing requirement anchor in the repository, with code implementation evidence listed first for now.

| Code Module | Requirement ID(s) | Code Implementation Evidence | Current Anchor Source |
|---|---|---|---|
| src/threat_modeler/ui/connection_validator.py | SCR-013, SCR-014 | src/threat_modeler/ui/connection_validator.py | Requirements/04_Traceability_Matrix.md; planning/archives/2026-06/issues/closed_trackers/Sprint_2026_013_Issue_Tracker.md |
| src/threat_modeler/ui/runtime_io.py | SCR-007 | src/threat_modeler/ui/runtime_io.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/canonical_graph_viewer.py | GUI-019 | src/threat_modeler/ui/screens/canonical_graph_viewer.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/config.py | SCR-003, SCR-012, SCR-013, SCR-014 | src/threat_modeler/ui/screens/config.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/last_prompt.py | SCR-015 | src/threat_modeler/ui/screens/last_prompt.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/markdown_viewer.py | GUI-025 | src/threat_modeler/ui/screens/markdown_viewer.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/mermaid_viewer.py | GUI-020 | src/threat_modeler/ui/screens/mermaid_viewer.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/results_export.py | SCR-007 | src/threat_modeler/ui/screens/results_export.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/role_select.py | SCR-002 | src/threat_modeler/ui/screens/role_select.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/snapshot_manager.py | SCR-008 | src/threat_modeler/ui/screens/snapshot_manager.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/stix_viewer.py | GUI-018 | src/threat_modeler/ui/screens/stix_viewer.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/stride_viewer.py | GUI-021 | src/threat_modeler/ui/screens/stride_viewer.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/threat_review.py | SCR-004 | src/threat_modeler/ui/screens/threat_review.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/screens/token_usage.py | SCR-014 | src/threat_modeler/ui/screens/token_usage.py | Requirements/04_Traceability_Matrix.md |
| src/threat_modeler/ui/version_governance.py | GUI-024 | src/threat_modeler/ui/version_governance.py | Requirements/04_Traceability_Matrix.md |

## Architecture / Design Relationship Evaluation

The reachable implementation surface now splits cleanly into two groups after excluding dead or unreachable code:

| Code Module Group | Count | Trace State | Notes |
|---|---|---|---|
| Requirement-anchored reachable modules | 15 | Architecture/design relationships can now be derived and backfilled from the existing capability/function families and verification artifacts | These are the modules listed in the backfill tables above and in the architecture/design appendices |
| Reachable modules still outside requirement and architecture/design trace | 13 | No current requirement, architecture, or design anchor | These remain outside the trace chain and should be handled as separate backlog items |

### Remaining Reachable Modules Outside Architecture / Design Trace

| Code Module | Status |
|---|---|
| src/threat_modeler/__main__.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/agents/base.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/agents/deserialise.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/backend/runtime_state.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/exports/json_exporter.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/exports/report_exporter.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/hitl/models.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/llm/llm_provider_error.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/llm/xai_adapter.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/server/hmi_data.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/state.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/ui/debug.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/ui/session.py | No existing requirement, architecture, or design anchor |
| src/threat_modeler/ui/theme.py | No existing requirement, architecture, or design anchor |
