# C05 Agent 04 STRIDE Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From
- C05-A04-00x derived from C05 (STRIDE scoring) slices under C04/C05 threat analysis capabilities (M3) and C13-UI-001 / C16-PRJ-001 for review and export surfaces.

### Allocated To
- Allocated to C05-A04-* L2/L3 functions realized in Agent_Subsystem_Design_Specification.md + src/threat_modeler/agents/agent_04_stride_scorer.py + related viewers (stride_viewer.py) and export paths.

### Satisfied By / Verified By
- STRIDE vector assignment, rationale per interface/flow, and integration with canonical entities + export satisfied by agent_04_stride_scorer.py, canonical model, stride viewer and export tests (Tests/integration/test_stride_viewer_screen.py, test_stride_export_artifact.py), and FQT threat review cases. Cross-ref 15_End_To_End and Functional_Data_Flow for the specific rows.

### Depends On
- Agent_Subsystem_Design_Specification.md, Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md, 01/02/10/12 requirements for analysis inputs and review surfaces, 15_End_To_End_Traceability_Attributes_Registry.md, and the threat analysis portions of the functional decomposition.
|C05-A04-001|STRIDE Score Assignment|Agent 4 SHALL assign STRIDE severity scores for each data flow using the configured scoring scale.|Quantified scoring is required for consistent risk ranking.|Test|Verified by STRIDE fixture tests with expected score outputs.|
|C05-A04-002|Score Justification Output|Agent 4 SHALL provide concise justification text for each STRIDE dimension score.|Justification supports analyst review and calibration.|Inspection|Verified by artifact review confirming six STRIDE justification fields per flow.|
|C05-A04-003|Override Preservation|Agent 4 SHALL preserve analyst-overridden scores and associated rationale metadata.|Human overrides must remain traceable and stable across reruns.|Test|Verified by override and rerun test confirming overridden values and rationale persistence.|
