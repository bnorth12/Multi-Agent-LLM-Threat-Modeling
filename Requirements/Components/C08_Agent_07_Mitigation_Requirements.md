# C08 Agent 07 Mitigation Requirements

| ID | Name | Requirement Text | Requirement Rationale | Verification Method | Verification Statement |
| --- | --- | --- | --- | --- | --- |
| C08-A07-001 | Threat-to-Control Mapping | Agent 7 SHALL map each approved threat to technical and administrative controls based on configured control frameworks. | Mitigation quality depends on direct threat-to-control mapping. | Test | Verified by coverage test confirming controls are generated for each approved threat. |
| C08-A07-004 | Threat-Level Mitigation Placement | Agent 7 SHALL store mitigations_technical and mitigations_administrative arrays under each threat object in canonical graph output. | Threat-level placement preserves one-to-one traceability between threat and selected controls. | Test | Verified by schema and path assertions confirming mitigation arrays exist under each threat object. |
| C08-A07-002 | Residual Risk Estimation | Agent 7 SHALL assign residual-risk estimates after proposed controls. | Residual risk is required for risk acceptance decisions. | Test | Verified by range and presence checks on residual risk values per mapped threat. |
| C08-A07-003 | Mitigation Rationale | Agent 7 SHALL include rationale linking control selections to threat mechanics. | Analysts require rationale to evaluate control suitability. | Inspection | Verified by manual review confirming rationale text references threat mechanism and control effect. |
