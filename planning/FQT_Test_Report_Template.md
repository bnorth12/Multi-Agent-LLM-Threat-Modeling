# Formal Qualification Test (FQT) Report Template

**Report ID:** FQT-UAS-{TIMESTAMP}
**Test Date:** {DATE}
**Executed By:** Autonomous E2E Smoke Test Runner
**System Under Test:** Multi-Agent Threat Modeler v{VERSION}
**Test Fixture:** UAS Weapon System (ICD-based fixture)

---

## 1. Executive Summary

| Property | Value |
|----------|-------|
| **Test Objective** | Autonomous full end-to-end smoke test of threat modeling pipeline with HITL gate participation and comprehensive artifact export |
| **Test Status** | {PASS/FAIL} |
| **Total Duration (seconds)** | {DURATION} |
| **Stages Completed** | {COMPLETED_STAGES}/9 |
| **HITL Gates Approved** | {GATES_APPROVED} |
| **Threat Count Detected** | {THREAT_COUNT} |
| **Token Usage (Total)** | {TOKEN_COUNT} |
| **Screenshots Captured** | {SCREENSHOT_COUNT} |
| **Artifacts Downloaded** | {ARTIFACT_COUNT} |

---

## 2. Test Scope & Requirements Traceability

### 2.1 Functional Requirements Covered

| Req ID | Requirement | Test Step | Result | Evidence |
|--------|-------------|-----------|--------|----------|
| PRJ-001 | System accepts structured threat context (CAV/markdown) | Input Upload | {PASS/FAIL} | `screenshots/03_input_entry_uploaded.png` |
| PRJ-002 | Pipeline executes 9 stages sequentially | Stage Monitoring | {PASS/FAIL} | Log entries: Stage 01-09 transitions |
| PRJ-003 | Mandatory HITL gates pause execution | Gate Approval | {PASS/FAIL} | `{GATE_SCREENSHOTS}` |
| PRJ-016 | GUI renders home, input, results, and export screens | Screen Navigation | {PASS/FAIL} | Screenshots: home, pipeline config, results, exports |
| GUI-001 | Input Entry Form accepts CSV + markdown uploads | Input Stage | {PASS/FAIL} | `screenshots/03_input_entry_uploaded.png` |
| GUI-003 | Home/Dashboard displays pipeline status | Home Screen | {PASS/FAIL} | `screenshots/01_home_sidebar_ready.png` |
| GUI-002 | HITL Gate screens present decision prompts | Gate Approval | {PASS/FAIL} | `screenshots/gate_*.png` |

### 2.2 Non-Functional Requirements

| Req ID | Requirement | Target | Measured | Result |
|--------|-------------|--------|----------|--------|
| PRJ-020 | LLM provider integration (xAI/Grok) | API call succeeds | {API_STATUS} | {PASS/FAIL} |
| PRJ-006 | HITL gate pausing mechanism | ≥5 gates triggered | {GATES_APPROVED} gates | {PASS/FAIL} |
| REL-001 | No crashes during full pipeline run | 0 exceptions | {EXCEPTION_COUNT} | {PASS/FAIL} |

---

## 3. Test Execution Narrative

### 3.1 Pre-Test Setup
- **Test Environment:** Windows 10, Python 3.11.9, Streamlit with Playwright headful browser
- **Configuration:**
  - `RUN_VISIBLE_BROWSER_TESTS=1` (visible browser automation)
  - `THREAT_MODELER_SMOKE_RUN_TIMEOUT=1800` seconds (30 min)
  - `THREAT_MODELER_SMOKE_KEEP_OPEN_UNTIL_INPUT=0` (autonomous execution)
  - `THREAT_MODELER_SMOKE_HOLD_SECONDS=600` (10 min post-completion hold)
- **Fixture:** ICD UAS Weapon System (10 CSV files + markdown description)
- **LLM Provider:** xAI/Grok (live API)

### 3.2 Test Flow & Stage Breakdown

| Stage | Name | Status | Duration (s) | Gates Triggered | Notes |
|-------|------|--------|--------------|-----------------|-------|
| 00 | Home/Sidebar | {PASS/FAIL} | {DURATION} | — | Initial load and navigation |
| 01 | Input Normalizer | {PASS/FAIL} | {DURATION} | {COUNT} | 10 CSV files uploaded; markdown parsed |
| 02 | Hierarchical Context Builder | {PASS/FAIL} | {DURATION} | {COUNT} | Context aggregation completed |
| 03 | Trust Boundary Validator | {PASS/FAIL} | {DURATION} | {COUNT} | Threat boundary extraction |
| 04 | STRIDE Scorer | {PASS/FAIL} | {DURATION} | {COUNT} | Threat classification and scoring |
| 05 | Concrete Threat Generator | {PASS/FAIL} | {DURATION} | {COUNT} | Threat narratives synthesized |
| 06 | STIX Packager | {PASS/FAIL} | {DURATION} | {COUNT} | Standardized output generated |
| 07 | Report Generator | {PASS/FAIL} | {DURATION} | — | Markdown report composed |
| 08 | Export Controls & Download Capture | {PASS/FAIL} | {DURATION} | — | 9 export controls verified |
| 09 | Completion & Hold | {PASS/FAIL} | {HOLD_DURATION} | — | Browser held open for manual inspection |

### 3.3 HITL Gate Verification

| Gate ID | Triggered | Approved | Timestamp | Screenshot |
|---------|-----------|----------|-----------|------------|
| gate_1_scope_confirmation | {YES/NO} | {YES/NO} | {TS} | `{PATH}` |
| gate_2_boundary_approval | {YES/NO} | {YES/NO} | {TS} | `{PATH}` |
| gate_3_stride_calibration | {YES/NO} | {YES/NO} | {TS} | `{PATH}` |
| gate_4_threat_plausibility | {YES/NO} | {YES/NO} | {TS} | `{PATH}` |
| gate_5_mitigation_adequacy | {YES/NO} | {YES/NO} | {TS} | `{PATH}` |

---

## 4. Artifact & Evidence Capture

### 4.1 Screenshots

| # | Step | File | Timestamp | Status |
|---|------|------|-----------|--------|
| 1 | Home/Sidebar Ready | `01_home_sidebar_ready.png` | {TS} | ✅ Captured |
| 2 | Pipeline Configuration | `02_pipeline_configuration.png` | {TS} | ✅ Captured |
| 3 | Input Entry Uploaded | `03_input_entry_uploaded.png` | {TS} | ✅ Captured |
| 4 | Run Dashboard Started | `04_run_dashboard_started.png` | {TS} | ✅ Captured |
| 5-N | Gate Approvals & Stage Results | `gate_*.png`, `stage_*.png` | {TS} | {CAPTURED_COUNT}/{EXPECTED_COUNT} |

### 4.2 Downloaded Artifacts

| Export Control | Target File | Status | Size (bytes) | Hash (MD5) |
|---|---|---|---|---|
| Canonical Graph | `canonical_graph.json` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| STIX 2.1 Bundle | `threat_model.stix2` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| Markdown Report | `threat_model_report.md` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| Mermaid Diagram | `threat_diagram.mmd` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| Token Usage Report | `token_usage.json` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| STRIDE Summary | `stride_summary.json` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| Manifest | `manifest.json` | {CAPTURED/MISSING} | {SIZE} | {HASH} |
| Inventory | `inventory.json` | {CAPTURED/MISSING} | {SIZE} | {HASH} |

### 4.3 Viewer Content Verification

| Viewer | Screen Name | Content Rendered | Heading Visible | Screenshot |
|--------|-------------|------------------|-----------------|------------|
| Home Sidebar | Home Dashboard | {YES/NO} | {YES/NO} | `{PATH}` |
| Threat Review | Threat List | {YES/NO} | {YES/NO} | `{PATH}` |
| Attack Path | Attack Paths | {YES/NO} | {YES/NO} | `{PATH}` |
| Mitigation Plan | Mitigations | {YES/NO} | {YES/NO} | `{PATH}` |
| Risk Assessment | Risk Matrix | {YES/NO} | {YES/NO} | `{PATH}` |
| State Inspector | Backend State | {YES/NO} | {YES/NO} | `{PATH}` |
| Logs | Execution Logs | {YES/NO} | {YES/NO} | `{PATH}` |
| Mermaid Viewer | Threat Diagram | {YES/NO} | {YES/NO} | `{PATH}` |
| STIX Viewer | STIX Output | {YES/NO} | {YES/NO} | `{PATH}` |
| Canonical Graph Viewer | Graph Output | {YES/NO} | {YES/NO} | `{PATH}` |
| Markdown Viewer | Report | {YES/NO} | {YES/NO} | `{PATH}` |
| Snapshot Manager | Snapshots | {YES/NO} | {YES/NO} | `{PATH}` |
| Last Prompt | Prompt History | {YES/NO} | {YES/NO} | `{PATH}` |
| Prompt Editor | Prompt Editing | {YES/NO} | {YES/NO} | `{PATH}` |

---

## 5. Findings & Observations

### 5.1 Passed Verifications
- [ ] All 9 stages executed without crash
- [ ] At least 3 HITL gates triggered and approved
- [ ] Threat count extracted and ≥ 1 threat identified
- [ ] All 9 export controls clickable and responded
- [ ] At least 8 left-nav viewers accessible and rendered
- [ ] Screenshots captured for major steps
- [ ] Pipeline reached COMPLETED state
- [ ] Browser hold activated post-completion

### 5.2 Failed Verifications
- [ ] {FAILURE_1}
- [ ] {FAILURE_2}

### 5.3 Coverage Gaps
- [ ] {GAP_1}
- [ ] {GAP_2}

### 5.4 Performance Observations
- **LLM Latency:** {AVG_LATENCY} seconds per stage
- **Token Efficiency:** {TOKEN_COUNT} tokens for {THREAT_COUNT} threats
- **Browser Responsiveness:** {RESPONSIVENESS_NOTES}
- **Stage Bottleneck:** {SLOWEST_STAGE} at {MAX_DURATION} seconds

---

## 6. Artifact Locations

```
FQT/
├── {TIMESTAMP}/                          # Test execution directory
│   ├── test_report.md                    # This report (markdown)
│   ├── test_report.json                  # This report (JSON structured)
│   ├── smoke_run.log                     # Full execution log
│   ├── screenshots/                      # All captured screenshots
│   │   ├── 01_home_sidebar_ready.png
│   │   ├── 02_pipeline_configuration.png
│   │   ├── 03_input_entry_uploaded.png
│   │   ├── 04_run_dashboard_started.png
│   │   └── gate_*.png, stage_*.png
│   └── downloads/                        # Downloaded artifacts
│       ├── canonical_graph.json
│       ├── threat_model.stix2
│       ├── threat_model_report.md
│       ├── threat_diagram.mmd
│       ├── token_usage.json
│       ├── stride_summary.json
│       ├── manifest.json
│       └── inventory.json
```

---

## 7. Pass/Fail Criteria

| Criterion | Required | Actual | Status |
|-----------|----------|--------|--------|
| Pipeline completes all 9 stages | YES | {COMPLETED_STAGES}/9 | {PASS/FAIL} |
| ≥3 HITL gates triggered and approved | YES | {GATES_APPROVED} | {PASS/FAIL} |
| ≥1 threat detected | YES | {THREAT_COUNT} | {PASS/FAIL} |
| ≥8 viewers render and display heading | YES | {VIEWER_COUNT}/8+ | {PASS/FAIL} |
| ≥5 export controls respond and download | YES | {EXPORT_COUNT}/9 | {PASS/FAIL} |
| ≥10 screenshots captured | YES | {SCREENSHOT_COUNT} | {PASS/FAIL} |
| No unhandled exceptions | YES | {EXCEPTION_COUNT} exceptions | {PASS/FAIL} |
| **OVERALL TEST RESULT** | — | — | **{PASS/FAIL}** |

---

## 8. Recommendations

1. {RECOMMENDATION_1}
2. {RECOMMENDATION_2}
3. {RECOMMENDATION_3}

---

## 9. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Test Automation | Autonomous Smoke Runner | {DATE} | Automated |
| Review | {REVIEWER} | {DATE} | {SIGNATURE} |

---

**Document Version:** 1.0
**Last Updated:** {TIMESTAMP}
**Classification:** Test Evidence
