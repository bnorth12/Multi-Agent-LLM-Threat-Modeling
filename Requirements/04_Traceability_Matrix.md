# Traceability Matrix

**Last Updated:** Sprint 2026-07 WA (S07-01)
**Status:** Active reconciliation — Delivered vs Deferred columns now separate GUI requirements by sprint delivery

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
- PRJ-008 -> C11-LLM-001, C11-LLM-003, INT-012, INT-015, **GUI-012 (Delivered S07-02), GUI-013 (Delivered S07-02), GUI-014 (Delivered S07-03)**
- PRJ-009 -> C11-LLM-002, INT-012
- PRJ-010 -> C06-A05-002, C08-A07-003, INT-008
- PRJ-011 -> C07-A06-001, C09-A08-001, C10-A09-001, INT-10, INT-11, **GUI-006 (Deferred to S07-06), GUI-007 (Deferred to S07-06)**
- PRJ-012 -> C12-HITL-002, INT-013
- PRJ-013 -> C03-A02-001, C01-STATE-002, C12-HITL-004
- PRJ-014 -> C09-A08-003, INT-007
- PRJ-015 -> C01-STATE-003, C04-A03-002
- PRJ-016 -> **GUI-001 (Delivered S06-07), GUI-002 (Delivered S06-07), GUI-003 (Delivered S06-07), GUI-004 (Deferred to S07-05), GUI-005 (Deferred to S07-05), GUI-006 (Deferred to S07-06), GUI-011 (Deferred to S07-03), GUI-012 (Delivered S07-02), GUI-013 (Delivered S07-02), GUI-014 (Delivered S07-03)**, docs/HMI_Architecture_Blueprint.md
- PRJ-017 -> **GUI-007 (Deferred to S07-06), GUI-008 (Deferred to S07-06)**
- PRJ-018 -> **GUI-009 (Deferred to S07-04), GUI-010 (Deferred to S07-04)**

---

## GUI Requirements Delivery Status

| GUI ID | Screen Name | Blueprint SCR | Sprint | Status | Notes |
|--------|-------------|---------------|--------|--------|-------|
| GUI-001 | Input Entry Form | SCR-001 | S06-07 | ✅ Delivered | `src/threat_modeler/ui/screens/input_entry.py`; shown in screenshot scr_004 |
| GUI-002 | HITL Gate Screen | SCR-005 | S06-07 | ✅ Delivered | Backend implemented in S05-04; GUI screens pending S07 implementation |
| GUI-003 | Home/Dashboard | SCR-002 | S06-07 | ✅ Delivered | Pipeline status view; shown in screenshot scr_001 |
| GUI-004 | Stage Results Viewer | SCR-003 | **Deferred S07** | ⏳ S07-05 | GUI-004 spec in HMI blueprint; stage output inspection deferred |
| GUI-005 | Threat and Mitigation Review | SCR-004 | **Deferred S07** | ⏳ S07-05 | Threat/mitigation analyst review deferred |
| GUI-006 | Results Export | SCR-007 | **Deferred S07** | ⏳ S07-06 | Export JSON/STIX/Mermaid/report GUI deferred |
| GUI-007 | Snapshot Export | SCR-008 | **Deferred S07** | ⏳ S07-06 | Run snapshot save deferred |
| GUI-008 | Snapshot Restore | SCR-009 | **Deferred S07** | ⏳ S07-06 | Run restoration from snapshot deferred |
| GUI-009 | Agent Prompt Editor | SCR-010 | **Deferred S07** | ⏳ S07-04 | Per-agent prompt editing deferred |
| GUI-010 | Prompt Version History | SCR-011 | **Deferred S07** | ⏳ S07-04 | Prompt version history and rollback deferred |
| GUI-011 | Input Entry Validation Banner | — | **Deferred S07** | ⏳ S07-03 | Validation gate guidance banner deferred |
| GUI-012 | Model Provider Selection | SCR-012 | **S07-02** | ⏳ Active | Provider dropdown (Custom/Intranet support) |
| GUI-013 | Model Connection Details | SCR-013 | **S07-02** | ⏳ Active | Connection string/URL input |
| GUI-014 | Model Connection Validation | SCR-014 | **S07-03** | ⏳ Active | Connection test and validation gate |

---

## Test Suite Linkage

- Tests/unit/test_input_ingestion.py -> PRJ-001, PRJ-002, INT-001, INT-002
- Tests/integration/test_validation_gates.py -> PRJ-003, PRJ-015, INT-005
- **Tests/unit/test_ui_app_shell.py** -> PRJ-016, PRJ-018 (S06-07 partial coverage; S07 expansion in S07-07)

---

## Administration Linkage

- ADM-001 -> 08_Feature_Branch_Checklist_Template.md (Section A)
- ADM-002 -> 07_Release_Process.md (Sections 2 and 3), 08_Feature_Branch_Checklist_Template.md (Section E)
- ADM-003 -> 08_Feature_Branch_Checklist_Template.md (Completion Decision)
- ADM-004 -> 07_Release_Process.md (Sections 3 and 4)
- ADM-005 -> 07_Release_Process.md (Section 2.4)
- ADM-006 -> 06_Project_Administration_Requirements.md
