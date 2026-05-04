# Traceability Matrix

Project to component and interface mapping:

- PRJ-001 -> C02-A01-001, INT-001
- PRJ-002 -> C01-STATE-001, C02-A01-001, INT-002, INT-003
- PRJ-003 -> C01-ORCH-001, C01-ORCH-002, INT-005
- PRJ-004 -> C01-STATE-003, INT-004
- PRJ-005 -> C04-A03-001, C05-A04-001, C06-A05-001, C07-A06-001, C08-A07-001, C09-A08-001, C10-A09-001
- PRJ-006 -> C12-HITL-001, C12-HITL-002, HITL-001 to HITL-006, INT-006
- PRJ-007 -> C01-STATE-002, C12-HITL-003, C12-HITL-004, INT-014
- PRJ-008 -> C11-LLM-001, C11-LLM-003, INT-012, INT-015, GUI-012, GUI-013, GUI-014
- PRJ-009 -> C11-LLM-002, INT-012
- PRJ-010 -> C06-A05-002, C08-A07-003, INT-008
- PRJ-011 -> C07-A06-001, C09-A08-001, C10-A09-001, INT-010, INT-011
- PRJ-012 -> C12-HITL-002, INT-013
- PRJ-013 -> C03-A02-001, C01-STATE-002, C12-HITL-004
- PRJ-014 -> C09-A08-003, INT-007
- PRJ-015 -> C01-STATE-003, C04-A03-002
- PRJ-016 -> GUI-001, GUI-002, GUI-003, GUI-004, GUI-005, GUI-006, GUI-011, GUI-012, GUI-013, GUI-014, docs/HMI_Architecture_Blueprint.md
- PRJ-017 -> GUI-007, GUI-008
- PRJ-018 -> GUI-009, GUI-010

Test suite linkage:

- Tests/unit/test_input_ingestion.py -> PRJ-001, PRJ-002, INT-001, INT-002
- Tests/integration/test_validation_gates.py -> PRJ-003, PRJ-015, INT-005

Note:

- Requirement identifiers intentionally map to component file prefixes for easier ticketing.

Administration linkage:

- ADM-001 -> 08_Feature_Branch_Checklist_Template.md (Section A)
- ADM-002 -> 07_Release_Process.md (Sections 2 and 3), 08_Feature_Branch_Checklist_Template.md (Section E)
- ADM-003 -> 08_Feature_Branch_Checklist_Template.md (Completion Decision)
- ADM-004 -> 07_Release_Process.md (Sections 3 and 4)
- ADM-005 -> 07_Release_Process.md (Section 2.4)
- ADM-006 -> 06_Project_Administration_Requirements.md
