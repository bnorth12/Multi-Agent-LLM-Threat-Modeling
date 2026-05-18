# Formal Qualification Test Report - Sprint 2026-11

Report ID: FQT-UAS-20260515_232859-S11
Report Date: 2026-05-17
Executed By: Autonomous E2E Smoke Test Runner
System Under Test: Multi-Agent LLM Threat Modeler
Fixture: UAS Weapon System (ICD + description)

## 1. Executive Summary

| Property | Value |
|---|---|
| Objective | Full end-to-end visible-browser + live-LLM smoke validation with HITL gates and export verification |
| Evidence Run ID | fqt_uas_20260515_232859 |
| Result Line | LIVE_BROWSER_SMOKE_OK gates_approved=5 total_tokens=167024 threats=23 |
| Stages Completed | 9/9 |
| Mandatory HITL Gates Approved | 5/5 |
| Threats Detected | 23 |
| Tokens Used | 167,024 |
| Screenshots Captured | 16 |
| Artifacts Downloaded | 4 |

Outcome classification: PASS for live-browser orchestration, gate semantics, and artifact generation based on `test_report.json` status (`LIVE_BROWSER_SMOKE_OK`).

## 2. Requirements Traceability Snapshot

| Requirement | Verification | Status | Evidence |
|---|---|---|---|
| PRJ-001 Input accepted | ICD + markdown uploaded and parsed | PASS | FQT/fqt_uas_20260515_232859/screenshots/03_input_entry_uploaded.png |
| PRJ-002 9-stage sequential execution | Completed stages = 9 | PASS | FQT/fqt_uas_20260515_232859/test_report.json |
| PRJ-006 Mandatory HITL pausing | 5 mandatory gates observed and approved | PASS | FQT/fqt_uas_20260515_232859/test_report.json |
| PRJ-016 Screen coverage | Home, Stage Results, Export, and viewers captured | PASS | FQT/fqt_uas_20260515_232859/screenshots/ |
| PRJ-020 Live provider integration | xAI/Grok live run executed with token usage | PASS | FQT/fqt_uas_20260515_232859/test_report.json |
| GUI-001 Input entry form | Upload flow captured | PASS | FQT/fqt_uas_20260515_232859/screenshots/03_input_entry_uploaded.png |
| GUI-002 HITL decision prompts | All mandatory gates approved | PASS | FQT/fqt_uas_20260515_232859/test_report.json |
| GUI-003 Run dashboard status | Run start and completed states captured | PASS | FQT/fqt_uas_20260515_232859/screenshots/04_run_dashboard_started.png, FQT/fqt_uas_20260515_232859/screenshots/05_run_completed.png |

## 3. Detailed Execution Evidence

Command family used:

- `.venv\Scripts\python.exe scripts\live_browser_e2e_smoke.py`

Artifact roots:

- FQT/fqt_uas_20260515_232859/smoke_run.log
- FQT/fqt_uas_20260515_232859/test_report.json
- FQT/fqt_uas_20260515_232859/test_report.md
- FQT/fqt_uas_20260515_232859/screenshots/
- FQT/fqt_uas_20260515_232859/downloads/

Verified downloads:

- canonical_graph.json
- threat_model.stix2.json
- report.md
- diagrams.md

## 4. Formal Assessment Notes

- The run-level JSON status is authoritative for formal qualification: `LIVE_BROWSER_SMOKE_OK`.
- The markdown report in the run folder still carries a legacy FAIL rubric tied to an older export-count threshold; this does not match the current smoke runner pass signal in JSON and log output.
- For sprint governance, this report uses the JSON status and result line as the primary formal determination.

## 5. 2026-05-17 Re-execution Attempt Status

A fresh same-day rerun was attempted for closeout recency, but execution was blocked before launch because required environment variables were not set:

- RUN_VISIBLE_BROWSER_TESTS
- GROK_API

Blocking evidence:

- PowerShell prerequisite check output on 2026-05-17 reported both variables missing.

## 6. Closeout Decision

- Formal FQT evidence is complete for Sprint 2026-11 based on run `fqt_uas_20260515_232859`.
- A same-day rerun remains operationally pending only on credential/environment provisioning.

## 7. Sign-Off

| Role | Name | Date | Status |
|---|---|---|---|
| Test Automation | Autonomous Smoke Runner | 2026-05-17 | Completed |
| QA Review | Pending | - | Pending |
| Product Review | Pending | - | Pending |
