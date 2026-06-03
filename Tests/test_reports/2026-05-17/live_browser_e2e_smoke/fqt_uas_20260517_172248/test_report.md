# Formal Qualification Test (FQT) Report

**Report ID:** FQT-UAS-20260517_172248
**Test Date:** 2026-05-17 17:28:21
**Executed By:** Autonomous E2E Smoke Test Runner
**System Under Test:** Multi-Agent Threat Modeler
**Test Fixture:** UAS Weapon System FQT

---

## 1. Executive Summary

| Property | Value |
|----------|-------|
| **Test Objective** | Autonomous full E2E smoke test of threat modeling pipeline with HITL gate participation and comprehensive artifact export |
| **Test Status** | **PASS ✅** |
| **Total Duration (seconds)** | 333 |
| **Stages Completed** | 9/9 |
| **HITL Gates Approved** | 5 |
| **Threat Count Detected** | 1 |
| **Token Usage (Total)** | 44,646 |
| **Screenshots Captured** | 16 |
| **Artifacts Downloaded** | 9 |

---

## 2. Test Execution Narrative

### 2.1 Test Configuration

- **Environment:** Windows 10, Python 3.11.9, Streamlit + Playwright headful browser
- **Browser:** Chromium (headless=False, --start-maximized, no_viewport=True)
- **LLM Provider:** xAI/Grok (live API)
- **Fixture:** UAS Weapon System (10 CSV/markdown files)
- **System Name:** UAS Weapon System FQT

### 2.2 Pipeline Stages Execution

| Stage # | Stage Name | Completed | Notes |
|---------|------------|-----------|-------|
| 0 | Home/Sidebar | ✅ PASS | — |
| 1 | Input Normalizer | ✅ PASS | — |
| 2 | Context Builder | ✅ PASS | — |
| 3 | Trust Boundary Validator | ✅ PASS | — |
| 4 | STRIDE Scorer | ✅ PASS | — |
| 5 | Threat Generator | ✅ PASS | — |
| 6 | STIX Packager | ✅ PASS | — |
| 7 | Report Generator | ✅ PASS | — |
| 8 | Export Controls & Download | ✅ PASS | — |

### 2.3 HITL Gate Approvals

| Gate ID | Triggered | Status |
|---------|-----------|--------|
| gate_1_scope_confirmation | True | ✅ APPROVED |
| gate_2_boundary_approval | True | ✅ APPROVED |
| gate_3_stride_calibration | True | ✅ APPROVED |
| gate_4_threat_plausibility | True | ✅ APPROVED |
| gate_5_mitigation_adequacy | True | ✅ APPROVED |

---

## 3. Artifact & Evidence Capture

### 3.1 Screenshots Captured

| # | Label | File | Status |
|---|-------|------|--------|
| 1 | 01_home_sidebar_ready | `screenshots/01_home_sidebar_ready.png` | ✅ Captured |
| 2 | 02_pipeline_configuration | `screenshots/02_pipeline_configuration.png` | ✅ Captured |
| 3 | 03_input_entry_uploaded | `screenshots/03_input_entry_uploaded.png` | ✅ Captured |
| 4 | 04_run_dashboard_started | `screenshots/04_run_dashboard_started.png` | ✅ Captured |
| 5 | 05_run_completed | `screenshots/05_run_completed.png` | ✅ Captured |
| 6 | 06_token_usage | `screenshots/06_token_usage.png` | ✅ Captured |
| 7 | 07_stage_results | `screenshots/07_stage_results.png` | ✅ Captured |
| 8 | 08_results_export | `screenshots/08_results_export.png` | ✅ Captured |
| 9 | 09_stix_viewer | `screenshots/09_stix_viewer.png` | ✅ Captured |
| 10 | 10_canonical_graph_viewer | `screenshots/10_canonical_graph_viewer.png` | ✅ Captured |
| 11 | 11_mermaid_viewer | `screenshots/11_mermaid_viewer.png` | ✅ Captured |
| 12 | 12_stride_viewer | `screenshots/12_stride_viewer.png` | ✅ Captured |
| 13 | 13_markdown_viewer | `screenshots/13_markdown_viewer.png` | ✅ Captured |
| 14 | 14_snapshot_manager | `screenshots/14_snapshot_manager.png` | ✅ Captured |
| 15 | 15_last_prompt | `screenshots/15_last_prompt.png` | ✅ Captured |
| 16 | 16_prompt_editor | `screenshots/16_prompt_editor.png` | ✅ Captured |

### 3.2 Downloaded Artifacts

| Export Control | File | Status |
|---|------|--------|
| Download Canonical Graph JSON | `downloads/canonical_graph.json` | ✅ Downloaded |
| Download STIX Bundle JSON | `downloads/threat_model.stix2.json` | ✅ Downloaded |
| Download Final Report (Markdown) | `downloads/report.md` | ✅ Downloaded |
| Download Mermaid Diagrams (Markdown) | `downloads/diagrams.md` | ✅ Downloaded |
| Download Token Usage JSON | `downloads/token_usage.json` | ✅ Downloaded |
| Download STRIDE JSON | `downloads/stride.json` | ✅ Downloaded |
| Download STRIDE CSV | `downloads/stride.csv` | ✅ Downloaded |
| Download Component Version Manifest | `downloads/component_version_manifest.json` | ✅ Downloaded |
| Download Component File Inventory | `downloads/component_file_inventory.json` | ✅ Downloaded |

---

## 4. Pass/Fail Criteria

| Criterion | Required | Actual | Status |
|-----------|----------|--------|--------|
| Pipeline completes all 9 stages | 9/9 | 9/9 | ✅ PASS |
| ≥3 HITL gates triggered and approved | ≥3 | 5 | ✅ PASS |
| ≥1 threat detected | ≥1 | 1 | ✅ PASS |
| ≥5 export controls respond | ≥5 | 9 | ✅ PASS |
| No unhandled exceptions | 0 | 0 | ✅ PASS |
| **OVERALL TEST RESULT** | — | — | **✅ PASS** |

---

## 5. Verified Findings

> Capabilities confirmed functional during this run regardless of overall pass/fail outcome.
> These constitute standalone evidence of correct behaviour for the listed features.

| # | Finding | Evidence | Verified |
|---|---------|----------|----------|
| 1 | Streamlit UI starts and Home page renders | Screenshot 01_home_sidebar_ready captured | ✅ CONFIRMED |
| 2 | File upload widget accepts CSV and markdown inputs | Screenshots 03_input_entry_uploaded captured; run started | ✅ CONFIRMED |
| 3 | Orchestrator executes at least one pipeline stage | 9 stage(s) observed completing | ✅ CONFIRMED |
| 4 | Gate 1 – Scope Confirmation HITL pause and resume | Gate pause detected, screenshot captured, Resume clicked | ✅ CONFIRMED |
| 5 | Gate 2 – Trust Boundary Approval HITL pause and resume | Gate pause detected, screenshot captured, Resume clicked | ✅ CONFIRMED |
| 6 | Gate 3 – STRIDE Calibration HITL pause and resume | Gate pause detected, screenshot captured, Resume clicked | ✅ CONFIRMED |
| 7 | Gate 4 – Threat Plausibility HITL pause and resume | Gate pause detected, screenshot captured, Resume clicked | ✅ CONFIRMED |
| 8 | Gate 5 – Mitigation Adequacy HITL pause and resume | Gate pause detected, screenshot captured, Resume clicked | ✅ CONFIRMED |
| 9 | Heartbeat watchdog correctly detects backend stall and transitions to FAILED | Not triggered this run | ⏭ NOT REACHED |
| 10 | Export controls produce downloadable artifacts | 9 artifact(s) downloaded to downloads/ | ✅ CONFIRMED |

---

## 6. Pass/Fail Criteria

| Criterion | Required | Actual | Status |
|-----------|----------|--------|--------|
| Pipeline completes all 9 stages | 9/9 | 9/9 | ✅ PASS |
| ≥3 HITL gates triggered and approved | ≥3 | 5 | ✅ PASS |
| ≥1 threat detected | ≥1 | 1 | ✅ PASS |
| ≥5 export controls respond | ≥5 | 9 | ✅ PASS |
| No unhandled exceptions | 0 | 0 | ✅ PASS |
| **OVERALL TEST RESULT** | — | — | **✅ PASS** |

---

## 7. Artifact Locations

```
FQT/
├── 20260517_172248/           # Test execution directory
│   ├── test_report.md                   # This report (markdown)
│   ├── test_report.json                 # This report (structured JSON)
│   ├── smoke_run.log                    # Full execution log
│   ├── screenshots/                     # All captured screenshots
│   │   ├── 01_home_sidebar_ready.png
│   │   ├── 02_pipeline_configuration.png
│   │   ├── gate_*.png                   # Gate approval screenshots
│   │   └── stage_*.png                  # Stage result screenshots
│   └── downloads/                       # Downloaded artifacts
│       ├── canonical_graph.json
│       ├── threat_model.stix2
│       ├── threat_model_report.md
│       └── (other exports)
```

---

## 8. Notes & Observations

Visible browser FQT completed against UAS Weapon System with HITL approvals and export verification.

---

**Report Generated:** 2026-05-17 17:28:21
**Status:** ✅ Downloaded
