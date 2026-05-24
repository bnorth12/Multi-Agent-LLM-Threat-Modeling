# Traceability Matrix

**Last Updated:** Sprint 2026-12 HMI/HITL workflow refinement and header navigation consolidation
**Status:** Active reconciliation — Delivered vs Deferred columns now separate GUI requirements by sprint delivery

## React Refactor Addendum

- React refactor-specific requirements: `Requirements/11_React_HMI_Refactor_Requirements.md`
- React refactor test and artifact traceability: `Requirements/12_React_HMI_Traceability_To_Tests.md`
- Existing requirements review and remap status for the refactored frontend/backend interfaces is tracked in the addendum matrix above.

---

## Project Requirements → Component and Interface Mapping

Project to component and interface mapping:

- PRJ-001 -> C02-A01-001, INT-001
- PRJ-002 -> C01-STATE-001, C02-A01-001, INT-002, INT-003
- PRJ-003 -> C01-ORCH-001, C01-ORCH-002, INT-005
- PRJ-004 -> C01-STATE-003, INT-004
- PRJ-005 -> C04-A03-001, C05-A04-001, C06-A05-001, C07-A06-001, C08-A07-001, C09-A08-001, C10-A09-001
- PRJ-006 -> C12-HITL-001, C12-HITL-002, HITL-001 to HITL-006, INT-006
- PRJ-007 -> C01-STATE-002, C12-HITL-003, C12-HITL-004, INT-014
- PRJ-008 -> C11-LLM-001, C11-LLM-003, INT-012, INT-015, **GUI-012 (Delivered S07-02), GUI-013 (Delivered S07-02), GUI-014 (Delivered S07-03), GUI-015 (Delivered S08)**
- PRJ-009 -> C11-LLM-002, INT-012
- PRJ-010 -> C06-A05-002, C08-A07-003, INT-008
- PRJ-011 -> C07-A06-001, C09-A08-001, C10-A09-001, INT-10, INT-11, **GUI-006 (Deferred to S07-06), GUI-007 (Deferred to S07-06)**
- PRJ-012 -> C12-HITL-002, INT-013
- PRJ-013 -> C03-A02-001, C01-STATE-002, C12-HITL-004
- PRJ-014 -> C09-A08-003, INT-007
- PRJ-015 -> C01-STATE-003, C04-A03-002
- PRJ-016 -> **GUI-001 (Delivered S06-07), GUI-002 (Delivered S06-07), GUI-002B (Delivered S08), GUI-003 (Delivered S06-07), GUI-003B (Delivered S08), GUI-003C (Delivered S08), GUI-004 (Deferred to S07-05), GUI-005 (Deferred to S07-05), GUI-006 (Deferred to S07-06), GUI-011 (Deferred to S07-03), GUI-012 (Delivered S07-02), GUI-013 (Delivered S07-02), GUI-014 (Delivered S07-03), GUI-015 (Delivered S08), GUI-030 (Delivered S12), GUI-031 (Delivered S12), GUI-032 (Delivered S12), GUI-033 (Delivered S12), GUI-041 (Delivered S12), GUI-042 (Delivered S12)**, docs/HMI_Architecture_Blueprint.md
- PRJ-017 -> **GUI-007 (Deferred to S07-06), GUI-008 (Deferred to S07-06)**
- PRJ-018 -> **GUI-009 (Deferred to S07-04), GUI-010 (Deferred to S07-04)**
- PRJ-019 -> C01-ORCH-001, C01-STATE-002, INT-005, **GUI-016 (Planned S08 hotfix stream)**
- PRJ-020 -> C01-STATE-003, C11-LLM-003, INT-012, **GUI-017 (Planned S08 hotfix stream)**
- PRJ-023 -> C01-ORCH-001, C01-ORCH-002, C01-ORCH-003, INT-005
- PRJ-024 -> PRJ-016, GUI-001, VS-009
- PRJ-026 -> C01-ORCH-005, C02-A01-004, C03-A02-003, INT-005
- PRJ-027 -> C02-A01-004, C03-A02-003, GUI-001A, GUI-003B, GUI-014
- PRJ-028 -> C01-ORCH-004, C01-ORCH-005, HITL-001 to HITL-008, GUI-002, GUI-003A

---

## GUI Requirements Delivery Status

| GUI ID | Screen Name | Blueprint SCR | Sprint | Status | Notes |
|--------|-------------|---------------|--------|--------|-------|
| GUI-001 | Input Entry Form | SCR-001 | S06-07 | ✅ Delivered | `src/threat_modeler/ui/screens/input_entry.py`; shown in screenshot scr_004 |
| GUI-002 | HITL Gate Screen | SCR-005 | S06-07 | ✅ Delivered | Backend implemented in S05-04; GUI screens pending S07 implementation |
| GUI-002B | Non-Blocking HITL Gate Resume | SCR-005 / execution.py | S08 | ✅ Delivered S08 | Resume wired to `resume_pipeline_execution()` background thread; D-S08-012 fix |
| GUI-003 | Home/Dashboard | SCR-002 | S06-07 | ✅ Delivered | Pipeline status view; shown in screenshot scr_001 |
| GUI-003B | Screen-Level Execution State Synchronization | All screens | S08 | ✅ Delivered S08 | `sync_execution_state_to_session()` added to results_export.py, snapshot_manager.py; D-S08-013/014 fix |
| GUI-003C | Cross-Screen State Coherence | All artifact screens | S08 | ✅ Delivered S08 | Coherence guaranteed by GUI-003B sync call at top of each screen render(); D-S08-013/014 |
| GUI-004 | Stage Results Viewer | SCR-003 | **Deferred S07** | ⏳ S07-05 | GUI-004 spec in HMI blueprint; stage output inspection deferred |
| GUI-005 | Threat and Mitigation Review | SCR-004 | **Deferred S07** | ⏳ S07-05 | Threat/mitigation analyst review deferred |
| GUI-006 | Results Export | SCR-007 | **Deferred S07** | ⏳ S07-06 | Export JSON/STIX/Mermaid/report GUI deferred |
| GUI-007 | Snapshot Export | SCR-008 | **Deferred S07** | ⏳ S07-06 | Run snapshot save deferred |
| GUI-008 | Snapshot Restore | SCR-009 | **Deferred S07** | ⏳ S07-06 | Run restoration from snapshot deferred |
| GUI-009 | Agent Prompt Editor | SCR-010 | **Deferred S07** | ⏳ S07-04 | Per-agent prompt editing deferred |
| GUI-010 | Prompt Version History | SCR-011 | **Deferred S07** | ⏳ S07-04 | Prompt version history and rollback deferred |
| GUI-011 | Input Entry Validation Banner | — | **Deferred S07** | ⏳ S07-03 | Validation gate guidance banner deferred |
| GUI-012 | Model Provider Selection | SCR-012 | **S07-02** | ⏳ Active | Provider dropdown (Custom/Intranet support) |
| GUI-013 | Model Connection Details | SCR-013 | **S07-02** | ⏳ Active | Connection URL plus masked API-key input (session-only) for authenticated providers |
| GUI-014 | Model Connection Validation | SCR-014 | **S07-03** | ⏳ Active | Connection test and validation gate |
| GUI-015 | Token Usage Telemetry Dashboard and Export | SCR-014A | S08 | ✅ Delivered S08 | Token usage captured per stage from live provider responses and exposed in Token Usage screen plus Results Export JSON artifact |
| GUI-016 | Backend Runtime State Projection | SCR-002/SCR-003 runtime projection | S08 | 🔄 In Progress | Backend async runtime state as authority; GUI consumes projected state only |
| GUI-017 | Live Mode Failover Hard-Stop Visibility | SCR-014B | S08 | 🔄 In Progress | Live-intent runs must fail hard if fallback to fixture/offline occurs |
| GUI-030 | Ordered HITL Gate Ledger | SCR-005 / footer-aligned workflow | S12 | ✅ Delivered S12 | React HMI shows all gates in pipeline order with Approved/Rejected/Bypassed/Pending counts on one gate ledger page |
| GUI-031 | Persistent Timeline Status and Gate-Centric Monitoring | SCR-002 / SCR-005 / footer | S12 | ✅ Delivered S12 | Centered footer status text persists across pages and resume does not force navigation away from the HITL Gate page |
| GUI-032 | Input Integrity Preflight Review Gate | SCR-001 / SCR-005 pre-stage governance | S12 | ✅ Delivered S12 | Gate 0 now provides enforceable preflight review with human-readable input checks before Stage 1 execution |
| GUI-033 | Post-Stage-1 Normalization Review Gate | SCR-005 post-stage governance | S12 | ✅ Delivered S12 | New normalization review gate blocks Stage 2 until analyst approval of Stage 1 normalized artifact summary |
| GUI-041 | Header-Authoritative Artifact Domain Navigation | SCR-003 / header control rows | S12 | ✅ Delivered S12 | Artifact-domain switching moved to header tabs; left rail retained as persistent global navigation without duplicate artifact selector controls |
| GUI-042 | Header Review and Export Icon Entry Points | SCR-003 / SCR-006 | S12 | ✅ Delivered S12 | Header now exposes icon-labeled Threat Review and Results Export tabs; export surface includes mitigations export control |

---

## Test Suite Linkage

- Tests/unit/test_input_ingestion.py -> PRJ-001, PRJ-002, INT-001, INT-002
- Tests/integration/test_validation_gates.py -> PRJ-003, PRJ-015, INT-005
- **Tests/unit/test_ui_app_shell.py** -> PRJ-016, PRJ-018 (S06-07 partial coverage; S07 expansion in S07-07)
- Tests/unit/test_framework_orchestrator_langgraph.py -> PRJ-023, C01-ORCH-001, C01-ORCH-002
- Tests/unit/test_execution_mode_governance.py -> PRJ-023, C01-ORCH-003
- Tests/integration/test_agent_pipeline_completeness.py -> PRJ-003, PRJ-023, C01-ORCH-003
- Tests/e2e/test_browser_cav_markdown_upload.py -> PRJ-016, PRJ-024, VS-009
- frontend/src/App.test.tsx -> GUI-041, GUI-042
- frontend/src/components/HITLGateManager.test.tsx -> GUI-030, GUI-031
- Tests/integration/test_avionics_expected_results.py -> GUI-032, GUI-033
- Tests/Formal_Qualification_Test_Plan.md -> PRJ-001 through PRJ-028, HITL-001 through HITL-012, GUI-001A, GUI-002, GUI-003, GUI-003A, GUI-003B, GUI-003C, GUI-004, GUI-005, GUI-006, GUI-007, GUI-008, GUI-009, GUI-010, GUI-012, GUI-012A, GUI-013, GUI-014, GUI-015, GUI-016, GUI-017

---

## Administration Linkage

- ADM-001 -> 08_Feature_Branch_Checklist_Template.md (Section A)
- ADM-002 -> 07_Release_Process.md (Sections 2 and 3), 08_Feature_Branch_Checklist_Template.md (Section E)
- ADM-003 -> 08_Feature_Branch_Checklist_Template.md (Completion Decision)
- ADM-004 -> 07_Release_Process.md (Sections 3 and 4)
- ADM-005 -> 07_Release_Process.md (Section 2.4)
- ADM-006 -> 06_Project_Administration_Requirements.md
