# React HMI Refactor Requirements

Status: Active
Scope: React frontend, operational backend API interfaces, and runtime run-history controls.

## Requirements

| ID | Requirement | Verification Method | Primary Tests | Evidence Artifact |
|---|---|---|---|---|
| RHMI-001 | The HMI SHALL present setup screens for Home, Role Selection, Pipeline Configuration, and Input Entry before run start. | Automated E2E + manual demonstration | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/screenshots/01_home.png |
| RHMI-002 | The Pipeline Configuration screen SHALL enforce connection verification before applying live-provider settings. | Functional test | scripts/live_browser_e2e_smoke_react.py; Tests/test_hmi_backend_api.py | FQT/fqt_react_*/test_report.json |
| RHMI-003 | The HMI SHALL create runs through backend API using system name and initial input payload. | Integration test | Tests/test_hmi_backend_api.py::test_create_run | pytest output and API response logs |
| RHMI-004 | The HMI SHALL expose Last Prompt and Prompt Editor views backed by backend prompt APIs. | Component + API test | Tests/test_hmi_backend_api.py; scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/screenshots and test_report.json |
| RHMI-005 | The HMI SHALL display watchdog telemetry indicating heartbeat age versus timeout during monitoring. | UI functional verification | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-006 | Run history SHALL support per-run naming and archive state metadata. | API + UI functional test | Tests/test_hmi_backend_api.py; scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-007 | Run history SHALL support bulk selection, archive selected, and purge selected operations from All Runs. | UI functional test | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/screenshots/02_run_created.png |
| RHMI-008 | Backend SHALL support managed historical lifecycle endpoints for run metadata update and purge operations. | API integration test | Tests/test_hmi_backend_api.py | pytest output and API response logs |
| RHMI-009 | Connection verification SHALL execute a live provider prompt ping using configured provider, model, endpoint mode, and run-scoped API key, and SHALL only pass on successful non-empty provider response. | API integration test + UI functional test | Tests/test_hmi_backend_api.py; scripts/live_browser_e2e_smoke_react.py | pytest output and FQT test report |
| RHMI-010 | The Mermaid artifact viewer SHALL support parsed multi-diagram navigation with named selection, split/diagram/text display modes, editable source, rendered preview, and position indicator text (`x of n - diagram name`). | Component behavior validation + browser workflow test | frontend/src/components/ArtifactsViewer.tsx; Tests/e2e/test_frontend_react_mui_full_workflow.py; scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json and frontend diagnostics for ArtifactsViewer |

## Notes

- Purge permanently removes selected runs from backend runtime metadata and checkpoint storage.
- Archive marks runs for retention while removing them from active operational focus.
