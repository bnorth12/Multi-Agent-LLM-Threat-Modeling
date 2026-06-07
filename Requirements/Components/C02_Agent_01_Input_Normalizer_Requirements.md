# C02 Agent 01 Input Normalizer Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C02-A01-001|Canonical Transformation|Agent 1 SHALL transform raw text and table inputs into canonical graph structures without introducing unsupported fields.|Reliable normalization is foundational for all downstream stages.|Test|Verified by parser tests against canonical schema and unsupported-field rejection checks.|
|C02-A01-002|Deterministic ID Assignment|Agent 1 SHALL assign deterministic identifiers to new systems, subsystems, components, and data flows.|Stable IDs are required for merge, diff, and rerun consistency.|Test|Verified by repeated identical input runs producing identical IDs.|
|C02-A01-003|Unknown Boundary Marking|Agent 1 SHALL mark unknown trust-boundary status explicitly when source data is insufficient.|Unknown state is safer than implicit false confidence.|Inspection|Verified by artifact review on sparse input showing explicit unknown boundary flags.|
|C02-A01-004|ICD Source Compliance Flagging|Agent 1 SHALL preserve source provenance for ICD spreadsheet rows and narrative documents and SHALL emit structured compliance flags when required fields, interface references, or source mappings are missing or inconsistent.|Downstream stages and orchestrator gates need a machine-readable compliance record for ICD-derived inputs.|Test|Verified by invalid-input tests and browser upload evidence showing compliance errors are surfaced before downstream handoff.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From
- C02-A01-00x derived from C02 (input normalization) slices under C13-UI-001 / C15-INT-001 and M1 (Source Ingestion and Normalization) in the capability and functional hierarchies

### Allocated To
- Allocated to C02-A01-00x functions (F221 and children) realized in Agent_Subsystem_Design_Specification.md + src/threat_modeler/agents/agent_01_input_normalizer.py + parsing/icd_parser.py + narrative_parser.py

### Refines
- PRJ-001 (Unified Input Ingestion), PRJ-027 (ICD Source Compliance Validation), INT-001/002/003 (parser/agent input/output contracts)

### Satisfied By
- Canonical transformation, deterministic ID assignment, unknown boundary marking, and ICD source compliance flagging satisfied by src/threat_modeler/agents/agent_01_input_normalizer.py, src/threat_modeler/parsing/*, and Agent_Subsystem_Design_Specification.md (see 15_End_To_End and Partial_15_Wave backfill rows for deserialise/canonical/input_entry linkages)

### Verified By
- Tests/unit/test_input_ingestion.py, Tests/integration/test_agent_pipeline_completeness.py, browser upload + FQT input cases, 15_End_To_End verification for C02-A01 rows

### Depends On
- 01_Project_Requirements.md, 02_Interface_Requirements.md, Agent_Subsystem_Design_Specification.md, Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md, 15_End_To_End_Traceability_Attributes_Registry.md, and the input/ICD portions of External_Interface_And_Integration_Design_Package.md and Multi_Agent_Interface_Control_Document.md
