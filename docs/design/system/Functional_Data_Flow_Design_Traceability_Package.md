# Functional Data Flow Design Traceability Package

## Purpose

Capture system data flows as functional design artifacts and connect them to capability, function, requirement, architecture, design, implementation, verification, and test evidence.

This package is the design-side authority for data-flow behavior and transformation responsibilities.

## Scope

- End-to-end flow paths across trust boundaries
- Input normalization and source provenance behavior
- State transition and artifact publication flows
- Verification hooks and test artifact linkage

## Functional Data Flow Catalog

| Flow ID | Flow Name | Trigger | Input Sources | Transformations | Output Artifacts | Trust Boundary Crossings | Failure / Gate Conditions | Governing Capability IDs | Governing Function IDs | Governing Requirement IDs |
|---|---|---|---|---|---|---|---|---|---|---|
| DF-G0-001 | Gate 0 Input Integrity Preflight | Run start before Stage 1 | Raw text, structured tables, uploaded files | Input parsing, integrity checks, source provenance checks | Input preflight snapshot and gate decision context | User input boundary to runtime state boundary | Missing source integrity data or incomplete provenance opens Gate 0 hold | C12-HITL-001 | GUI-032, HITL-009, RIC-001, RIC-005 | GUI-032, HITL-009 |
| DF-ORCH-001 | Orchestrator Stage Transition Flow | Stage completion events | Active framework state, gate decisions | Next-stage resolution, checkpoint updates, transition validation | Updated runtime state, stage status projection, downstream prompts | Runtime control boundary between orchestrator and agent stages | Invalid transition or unresolved gate prevents stage advance | C01-ORCH-001 | F-ORCH-STATE-TRANSITIONS | C01-ORCH-001, INT-005 |
| DF-LLM-TRACE-C11_LLM_004 | Live LLM Request Budget and Timeout Flow | Live provider request invocation | Runtime config defaults, provider request payload, retry policy | Timeout enforcement, bounded retries, provider response normalization | LLM call telemetry, runtime status projection, retry outcome logs | Runtime to provider boundary | Timeout exceeded, retry budget exhausted, or provider failure triggers controlled failure path | C11-LLM-001 | F-C11_LLM_004-TRACE-L2 | C11-LLM-004, LLM-004 |

## Traceability Bridge

Use this table to bind each flow to downstream realization artifacts.

| Flow ID | Architecture Reference | Design Reference | Implementation References | Verification References | Test Artifact Metadata Reference |
|---|---|---|---|---|---|
| DF-G0-001 | docs/architecture/HMI_Architecture_Blueprint.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py; src/threat_modeler/hitl/service.py; frontend/src/components/HITLGateManager.tsx | Tests/integration/test_avionics_expected_results.py; Tests/test_hmi_backend_api.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-ORCH-001 | docs/architecture/Multi_Agent_Logical_Decomposition.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py; Tests/integration/test_agent_pipeline_completeness.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| DF-LLM-TRACE-C11_LLM_004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py; src/threat_modeler/config.py | Tests/e2e/test_live_llm_validation.py; Tests/unit/test_openai_compatible_adapter.py | Requirements/15_End_To_End_Traceability_Attributes_Registry.md |

## Review Rule

Each active remediation slice must confirm that every governing flow row has non-empty links in all bridge columns before closeout.

### Closed Slice Evidence

- R01-003 (`C11-LLM-004`) now has a dedicated flow row and bridge entry to enforce end-to-end design traceability coverage.
