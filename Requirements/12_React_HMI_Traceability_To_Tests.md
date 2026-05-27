# React HMI Traceability to Tests and Artifacts

This matrix traces new refactor requirements to automated tests and generated evidence artifacts.

| Requirement | Source | Backend Interface | Automated Test Coverage | Evidence Artifact Path |
|---|---|---|---|---|
| RHMI-001 Setup wizard screens | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs, POST /config | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/screenshots/01_home.png |
| RHMI-002 Connection verification gate | Requirements/11_React_HMI_Refactor_Requirements.md | POST /config/verify | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-003 Run creation by system name/input | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs, POST /runs/{run_id} | Tests/test_hmi_backend_api.py::test_create_run | pytest terminal report |
| RHMI-004 Last Prompt screen | Requirements/11_React_HMI_Refactor_Requirements.md | GET /runs/{run_id}/state/prompts | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-004 Prompt Editor screen | Requirements/11_React_HMI_Refactor_Requirements.md | GET /prompts, GET/POST /prompts/{agent_id} | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-005 LLM watchdog telemetry and animated running-state cue | Requirements/11_React_HMI_Refactor_Requirements.md | GET /runs with heartbeat fields | frontend/src/components/ExecutionProgress.test.tsx; frontend/src/App.test.tsx; scripts/live_browser_e2e_smoke_react.py | frontend vitest output and FQT/fqt_react_*/test_report.json |
| RHMI-006 Run naming and archive state | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs/{run_id}/metadata | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-007 Bulk select and lifecycle actions | Requirements/11_React_HMI_Refactor_Requirements.md | DELETE /runs/{run_id}/purge | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/screenshots/02_run_created.png |
| RHMI-008 Historical lifecycle endpoint support | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs/purge, DELETE /runs/{run_id}/purge | Tests/test_hmi_backend_api.py | pytest terminal report |
| RHMI-010 Mermaid multi-diagram selector and split view | Requirements/11_React_HMI_Refactor_Requirements.md | GET /runs/{run_id}/artifacts/mermaid | scripts/live_browser_e2e_smoke_react.py; Tests/e2e/test_frontend_react_mui_full_workflow.py | FQT/fqt_react_*/test_report.json |
| RHMI-011 Persistent left navigation rail | Requirements/11_React_HMI_Refactor_Requirements.md | N/A (shell layout requirement) | frontend/src/App.test.tsx | frontend vitest output |
| RHMI-012 Threats under Artifacts | Requirements/11_React_HMI_Refactor_Requirements.md | GET /runs/{run_id}/artifacts/canonical | frontend/src/components/ArtifactsViewer.test.tsx | frontend vitest output |
| RHMI-013 Header-anchored two-row top control strip | Requirements/11_React_HMI_Refactor_Requirements.md | N/A (shell layout requirement) | frontend/src/App.test.tsx | frontend vitest output |
| RHMI-014 Expanded left navigation rail | Requirements/11_React_HMI_Refactor_Requirements.md | N/A (shell layout requirement) | frontend/src/App.test.tsx | frontend vitest output |
| RHMI-015 Wizard-created run pin and badge visibility window | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs, GET /runs | scripts/live_browser_e2e_smoke_react.py | FQT/fqt_react_*/test_report.json |
| RHMI-016 Completed/paused run artifact availability after backend restart | Requirements/11_React_HMI_Refactor_Requirements.md | GET /runs/{run_id}/artifacts/canonical, /mermaid, /stix, /report | Tests/test_hmi_backend_api.py; backend restart health + artifact endpoint probes | pytest terminal report and planning/Sprint_2026_12_Execution_Log.md |
| RHMI-017 React CSV/XLSX parsing parity and spreadsheet binary-injection guard | Requirements/11_React_HMI_Refactor_Requirements.md | POST /runs (`initial_state.raw_text`, `initial_state.tables`) | scripts/live_browser_e2e_smoke_react.py; manual full UAS suite run verification | planning/Sprint_2026_12_Execution_Log.md and frontend payload behavior evidence |

## Existing Requirement Mapping Review

| Existing Requirement Area | Refactor Mapping Summary |
|---|---|
| GUI-001 / GUI-003 / GUI-012 / GUI-013 / GUI-014 | Mapped to setup wizard and verified connection flow in React HMI |
| GUI-009 / GUI-010 | Mapped to Prompt Editor and prompt history APIs |
| GUI-016 / PRJ-019 | Mapped to backend-authoritative runtime projection and watchdog telemetry |
| PRJ-011 / GUI-006 / GUI-007 | Mapped to artifacts and run-history operational controls |

## Artifact Retention

- Smoke/FQT run artifacts are produced under FQT/fqt_react_*/
- Formal API and unit/integration evidence is produced in pytest output and test reports
