# HITL Requirements

Implementation options reference:

- see 09_HITL_Framework_Options.md

| ID | Name | Requirement Text | Requirement Rationale | Verification Method | Verification Statement |
| --- | --- | --- | --- | --- | --- |
| HITL-001 | Scope Confirmation Gate | Threat Modeler SHALL provide Scope Confirmation Gate after context merge completion. | Early confirmation prevents downstream work on invalid scope. | Demonstration | Verified by run walkthrough pausing at scope gate after context merge stage. |
| HITL-002 | Boundary Approval Gate | Threat Modeler SHALL provide Trust Boundary Approval Gate after trust-boundary validation. | Boundary errors drive major threat-model inaccuracies. | Demonstration | Verified by trust-boundary stage pause requiring analyst approval. |
| HITL-003 | STRIDE Calibration Gate | Threat Modeler SHALL provide STRIDE Calibration Gate after STRIDE scoring. | Analyst calibration is needed for mission-context accuracy. | Demonstration | Verified by post-STRIDE review screen supporting approve and override actions. |
| HITL-004 | Threat Plausibility Gate | Threat Modeler SHALL provide Threat Plausibility Gate after threat generation. | Threat quality requires analyst validation before mitigation mapping. | Demonstration | Verified by threat review gate with approve and reject paths. |
| HITL-005 | Mitigation Adequacy Gate | Threat Modeler SHALL provide Mitigation Adequacy Gate after mitigation generation. | Control mappings must be reviewed for applicability and residual risk. | Demonstration | Verified by mitigation gate requiring analyst decision before release stages. |
| HITL-006 | Final Release Gate | Threat Modeler SHALL provide Final Release Gate before report and STIX publication. | Final publication requires explicit accountable approval. | Demonstration | Verified by final gate requirement prior to export operations. |
| HITL-007 | Override Rationale Capture | Threat Modeler SHALL require rationale entry for analyst overrides at all gates. | Rationale is necessary for audit and future review. | Test | Verified by UI/API validation rejecting override actions without rationale text. |
| HITL-008 | Signed Decision Records | Threat Modeler SHALL preserve gate decisions as signed run records. | Signed records provide non-repudiation for governance. | Inspection | Verified by audit artifact review showing signed gate decision entries per run. |
