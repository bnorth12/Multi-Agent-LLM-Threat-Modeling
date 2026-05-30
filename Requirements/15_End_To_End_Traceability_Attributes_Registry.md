# End To End Traceability Attributes Registry

## Purpose

Define and capture the metadata attributes required to trace each governed item through:

capability -> function -> requirement -> architecture -> design -> implementation -> verification -> test artifacts -> source code and other system artifacts.

## Registry Rules

- Every active sprint slice must add or update registry rows for touched IDs.
- Attribute values must be concrete and auditable; avoid placeholders at closeout.
- If any required attribute is missing, mark the row as process-failure and create remediation action(s).

## Required Attribute Set

| Attribute Group | Required Attributes |
|---|---|
| Identity | Slice ID, Capability ID, Function ID, Requirement ID |
| Architecture / Design | Architecture Artifact, Design Artifact, Data-Flow ID |
| Implementation | Source File Path, Symbol / Component, Change Scope |
| Verification | Verification Artifact, Verification Method, Result Status |
| Test Metadata | Test Artifact ID, Test Level, Environment, Last Evidence Timestamp |
| Governance | Owner, Review Gate, Disposition Path, Missing Legs |

## Registry Table

| Slice ID | Capability ID | Function ID | Requirement ID | Architecture Artifact | Design Artifact | Data-Flow ID | Source File Path | Symbol / Component | Verification Artifact | Test Artifact ID | Test Level | Evidence Timestamp | Disposition Path | Missing Legs | Process Failure | Remediation Action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S12-013 | C12-HITL-001 | GUI-032 | GUI-032 | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-G0-001 | src/threat_modeler/orchestrator.py | FrameworkOrchestrator | Tests/integration/test_avionics_expected_results.py | TST-S12-013-G0 | Integration | 2026-05-30T00:00:00 | implementation-first reconciliation | none | no | none |
| S12-033 | C01-ORCH-001 | F-ORCH-STATE-TRANSITIONS | C01-ORCH-001 | docs/architecture/Multi_Agent_Logical_Decomposition.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-ORCH-001 | src/threat_modeler/orchestrator.py | FrameworkOrchestrator | Tests/unit/test_framework_orchestrator_langgraph.py | TST-S12-033-ORCH | Unit | 2026-05-30T00:00:00 | architecture-first | function, implementation, verification | yes | Populate missing legs from disposition remediation actions |
| R01-003 | C11-LLM-001 | F-C11_LLM_004-TRACE-L2 | C11-LLM-004 | docs/architecture/Capability_Hierarchy_Baseline.md; docs/architecture/Function_Hierarchy_Registry.md; docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-LLM-TRACE-C11_LLM_004 | src/threat_modeler/llm/openai_compatible_adapter.py | OpenAICompatibleAdapter | Tests/e2e/test_live_llm_validation.py | TST-R01-003-LLM | E2E | 2026-05-30T14:45:00 | implementation-first reconciliation | none | no | none |
