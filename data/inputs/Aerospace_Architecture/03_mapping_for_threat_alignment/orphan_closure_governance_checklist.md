# Orphan Closure Governance Checklist

## Purpose

This checklist tracks closure of all ORPH-FN and ORPH-TRACE items to release gate criteria.
Each tranche maps to a release gate. Items must satisfy the gate criteria before the gate can be declared passed.

## Tranche-to-Gate Mapping

| Tranche | Priority | Domain Focus | Release Gate | Gate Criterion |
|---------|----------|--------------|--------------|----------------|
| T1 | P1 Flight Critical | AVIATE STAB/GUID/ELEC/PROP/HYDR; NAVIGATE SENS | G7-SAFETY | Safety case updated; all very_high interfaces have EA-SAFETY-CASE artifact evidence |
| T2 | P2 Hazardous | AVIATE HYDR/PNEU/INTG/HLTH; COMMUNICATE DLNK/AGND; NAVIGATE GUID | G5-THREAT | Threat model updated; all high interfaces have EA-THREAT-MODEL or EA-TRUST-CONFIG evidence |
| T3 | P3 Major Operational | COMMUNICATE INTC; NAVIGATE PLAN/RTE; OPERATE MAINT/OMMS | G4-VERIFICATION | Verification evidence present; ICD schema refs complete |
| T4 | P4 Missionized | OPERATE MDIS/MSN/SCAL/SFUS/SOPS/WRLS; inference expansion | G4-VERIFICATION | Inference matrix coverage expanded; operational functions linked |
| T5 | P5 Passenger/Commercial | OPERATE CABN/COMS/PAX | G9-READINESS | Operational readiness evidence; service isolation confirmed |

## Gate G7-SAFETY Closure Checklist (T1 — P1)

Applies to: IF-055 through IF-074 (20 interfaces, 20 orphan functions resolved).

- [ ] **G7-SAF-01** All 20 T1 interfaces have `EA-SAFETY-CASE` artifact reference populated in interface_governance_matrix
- [ ] **G7-SAF-02** Control-loop closure matrix CL-001 (STAB) updated to reference IF-055 IF-056 IF-057
- [ ] **G7-SAF-03** Control-loop closure matrix CL-002 (GUID/NAV) updated to reference IF-059 IF-060 IF-091 IF-093
- [ ] **G7-SAF-04** AVI.ELEC power chain (IF-063..IF-067) traced to FM-005 in safety case annex
- [ ] **G7-SAF-05** AVI.PROP protection chain (IF-068 IF-070) traced to FM-001 in safety case annex
- [ ] **G7-SAF-06** NAV.SENS spoofing chain (IF-071 IF-073) traced to FM-004 in threat model
- [ ] **G7-SAF-07** AVI.HYDR pressure chain (IF-074) traced to FM-006 in safety case annex
- [ ] **G7-SAF-08** Verification evidence refs (EA-VV-TEST) for all T1 very_high interfaces confirmed in EA backlog
- [ ] **G7-SAF-09** HITL gate review conducted for T1 interfaces; reviewer sign-off recorded
- [ ] **G7-SAF-10** cross_entrypoint_traceability_audit.md re-run and updated with new unreferenced count

## Gate G5-THREAT Closure Checklist (T2 — P2)

Applies to: IF-075 through IF-098 (24 interfaces, 28 orphan functions resolved; 0 open items remain).

- [ ] **G5-THR-01** All 22 T2 interfaces have threat model reference or trust-config evidence populated
- [ ] **G5-THR-02** AVI.PNEU chain (IF-078..IF-081) linked to FM-007 in FMEA hazard register inference rows
- [ ] **G5-THR-03** AVI.INTG L2 chain (IF-082..IF-084) linked to FM-008 trust boundary hazard analysis
- [ ] **G5-THR-04** COM.DLNK session and crypto chain (IF-087..IF-089) linked to FM-008 with encryption evidence
- [ ] **G5-THR-05** NAV.GUID trajectory chain (IF-091..IF-093) linked to HZ-002 HZ-030 in threat model
- [ ] **G5-THR-06** COM.AGND ADS-B interface (IF-096) linked to FM-004 with spoofing countermeasure evidence
- [x] **G5-THR-07** AVI.VSYS.001 L2 decomposition decision documented (ORPH-HIER-001 resolution record)
- [ ] **G5-THR-08** COM.DLNK.106 and COM.DLNK.107 (passenger datalinks) scheduled for T5 with boundary isolation evidence
- [ ] **G5-THR-09** HITL gate review conducted for T2 interfaces; reviewer sign-off recorded

- [ ] **G5-THR-11** Cross-domain L1 bridge exceptions reviewed against trust-boundary controls and threat model traceability (cross_domain_interface_exception_register.csv)

### ORPH-HIER-001 Closure Evidence

| Evidence Item | Value |
|---------------|-------|
| Parent function | AVI.VSYS.001 |
| Closure action | Define L2 children |
| Added child functions | AVI.VSYS.101; AVI.VSYS.102; AVI.VSYS.103 |
| Evidence artifact | function_catalog.csv |
| Tranche status update | ORPH-HIER-001 and ORPH-FN-032 set to executed |
| Remaining T2 open items | 0 |

## Gate G4-VERIFICATION Closure Checklist (T3/T4 — P3/P4)

Applies to: 27 open T3 and T4 items.

- [ ] **G4-VER-01** COM.INTC internal coordination interfaces (ORPH-FN-042..045) added with EA-ICD and EA-VV-TEST
- [ ] **G4-VER-02** NAV.PLAN route planning L2 chain (ORPH-FN-049..052) interfaces defined and linked to FM-004
- [ ] **G4-VER-03** NAV.RTE route management L2 chain (ORPH-FN-053..056) interfaces defined
- [ ] **G4-VER-04** OPS.MAINT.001 interface to AVI.HLTH.001 consumer path defined (ORPH-FN-067)
- [ ] **G4-VER-05** OPS.OMMS L1 and trend tracking (ORPH-FN-075 076) interface to external OMMS node defined
- [ ] **G4-VER-06** All T4 missionized sensor function interfaces (ORPH-FN-081..099) defined with EA-SENSOR-VALIDATION

- [ ] **G4-VER-09** Cross-domain interface exception register reviewed; all flagged L1-to-L1 and L2-to-L2 links have rationale, trust boundary class, and gate evidence refs (cross_domain_interface_exception_register.csv)

## Gate G9-READINESS Closure Checklist (T5 — P5)

Applies to: 11 T5 passenger/commercial items (executed).

- [x] **G9-RDY-01** OPS.CABN cabin operations interfaces defined with service-domain isolation evidence
- [x] **G9-RDY-02** OPS.PAX passenger services interfaces defined; AVI.INTG boundary enforcement cross-referenced
- [x] **G9-RDY-03** OPS.COMS commercial coordination interfaces defined with EA-CONOPS evidence
- [x] **G9-RDY-04** COM.DLNK.106 and COM.DLNK.107 passenger datalinks interfaced and isolated
- [x] **G9-RDY-05** Full orphan register: zero open items remain; all ORPH-FN statuses resolved or deferred with justification

## ORPH-TRACE-001 Inference Expansion Checklist

Applies to BULK inference gap: 262 FMEA entries not linked to l3_l4_l5_inference_matrix.

- [x] **TR-001** Prioritize FM-001..FM-009 (9 seeded failure modes) as first inference expansion tranche
- [x] **TR-002** Add inference rows for AVI domain HZs linked to CL-001 and CL-002
- [x] **TR-003** Add inference rows for COM domain HZs linked to CL-003
- [x] **TR-004** Add inference rows for OPS domain HZs linked to CL-004 and CL-005
- [ ] **TR-005** Re-run cross-entrypoint audit after each inference expansion batch

## Summary Metrics (as of T1-T5 execution and ORPH-TRACE batch expansion)

| Metric | Before | After T1+T2 | Target |
|--------|--------|-------------|--------|
| Total interfaces | 54 | 149 | 140+ |
| Orphaned functions (flow) | 99 | 0 | 0 |
| P1 orphans resolved | 0 | 20 | 20 |
| P2 orphans resolved | 0 | 28 | 28 |
| Inference coverage | 4/266 (2%) | 32/266 (12%) | 80%+ |
| Hierarchy orphans | 1 | 0 | 0 |

## Sign-off Block

| Gate | Reviewer | Date | Status |
|------|----------|------|--------|
| G7-SAFETY | | | open |
| G5-THREAT | | | open |
| G4-VERIFICATION | | | open |
| G9-READINESS | | | open |
