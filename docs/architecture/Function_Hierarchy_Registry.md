# Function Hierarchy Registry

## Purpose

Define the authoritative hierarchical function catalog used by architecture, design, and remediation traceability artifacts.

This document is the function-side root artifact that bridges capability hierarchy to implementation and verification evidence.

## Governance Rules

- Function IDs are stable and cannot be repurposed across capabilities.
- L2 and deeper functions must include at least one implementation and verification anchor.
- Remediation slices must reference function IDs defined in this registry.
- Every function row must bind to requirement hierarchy artifacts and architecture/design authority references.

## Function Hierarchy

| Function Level | Function ID | Parent Capability ID | Parent Function ID | Function Name | Functional Intent | Requirement IDs | Architecture and Design Authority | Implementation Anchor | Verification and Artifact Anchor |
|---|---|---|---|---|---|---|---|---|---|
| L0 | F-L0-MISSION-001 | CAP-L0-THREAT-MODELER | none | Governed Threat Model Production | Produce complete, governed threat-model outputs from validated source inputs. | PRJ-001, PRJ-003, PRJ-005 | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/integration/test_agent_pipeline_completeness.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | F-ORCH-TRACEABILITY-L1 | C01-ORCH-001 | F-L0-MISSION-001 | Orchestration Traceability Control | Ensure stage transitions, checkpoints, and run progression remain auditable. | C01-ORCH-001, ORCH-001, ORCH-002, ORCH-003 | docs/architecture/Multi_Agent_Logical_Decomposition.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | F-LLM-TRACEABILITY-L1 | C11-LLM-001 | F-L0-MISSION-001 | LLM Runtime Traceability Control | Govern LLM invocation behavior and runtime trace continuity for live mode. | C11-LLM-004, LLM-004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py | Tests/e2e/test_live_llm_validation.py; planning/issues/issue_2026_01_R01-003_C11_LLM_004_Architecture_Traceability_Remediation.md |
| L1 | F-HITL-TRACEABILITY-L1 | C12-HITL-001 | F-L0-MISSION-001 | HITL Decision Traceability Control | Enforce pause/resume/reject control with decision evidence preservation. | HITL-001, HITL-009, HITL-012, GUI-032 | docs/architecture/HMI_Architecture_Blueprint.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/hitl/service.py | Tests/integration/test_hitl_gate_set_2.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | F-UI-TRACEABILITY-L1 | C13-UI-001 | F-L0-MISSION-001 | UI Interaction Traceability Control | Maintain deterministic UI action surfaces and runtime state visibility. | GUI-002, GUI-003, GUI-012, GUI-032 | docs/architecture/HMI_Architecture_Blueprint.md; docs/design/software/Agent_Subsystem_Design_Specification.md | frontend/src/components/HITLGateManager.tsx | Tests/e2e/test_browser_run_validation.py; Tests/integration/test_markdown_viewer_editor.py |
| L1 | F-VER-TRACEABILITY-L1 | C14-VER-001 | F-L0-MISSION-001 | Verification Coverage Control | Maintain coverage continuity from requirement to test artifacts. | VS-009, SCR-014 | docs/architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md; docs/design/software/Export_And_Evidence_Packaging_Design_Specification.md | scripts/verify_sprint_traceability.py | Tests/integration/test_validation_gates.py; planning/Test_Execution_Summary_Sprint_2026_01.md |
| L1 | F-INT-TRACEABILITY-L1 | C15-INT-001 | F-L0-MISSION-001 | Interface Contract Traceability Control | Ensure integration boundary behavior remains contract-compliant and auditable. | INT-001, INT-002, INT-005, INT-009 | docs/architecture/Multi_Agent_Interface_Control_Document.md; docs/design/system/External_Interface_And_Integration_Design_Package.md | src/threat_modeler/config.py | Tests/integration/test_validation_gates.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | F-PRJ-TRACEABILITY-L1 | C16-PRJ-001 | F-L0-MISSION-001 | Delivery and Runtime Traceability Control | Govern delivery-path quality and runtime integrity across sprint execution. | PRJ-001, PRJ-002, PRJ-011, PRJ-023, PRJ-030 | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | scripts/governance_autoflow.py | independent_reviews/latest/independent_review_2026-01_pre-push.json; planning/Sprint_2026_01_Final_Validation_Summary.md |
| L1 | F-SCR-TRACEABILITY-L1 | C17-SCR-001 | F-L0-MISSION-001 | Security Runtime Traceability Control | Maintain security-sensitive runtime and evidence controls for compliance. | SCR-014 | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/system/System_Deployment_And_Operating_Modes_Design.md | src/threat_modeler/backend/run_manager.py | Tests/unit/test_token_usage_runtime.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L2 | F-C11_LLM_004-TRACE-L2 | C11-LLM-001 | F-LLM-TRACEABILITY-L1 | LLM Timeout and Retry Enforcement | Enforce timeout/retry constraints and controlled failure behavior for live model requests. | C11-LLM-004, LLM-004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py | Tests/e2e/test_live_llm_validation.py; Tests/unit/test_openai_compatible_adapter.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L2 | F-ORCH-STATE-TRANSITIONS | C01-ORCH-001 | F-ORCH-TRACEABILITY-L1 | Stage Transition Enforcement | Advance run state through deterministic stage graph transitions. | C01-ORCH-001, INT-005 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L2 | F-HITL-GATE-CONTROL | C12-HITL-001 | F-HITL-TRACEABILITY-L1 | HITL Gate Control | Execute governed pause/resume/reject transitions at gate boundaries. | HITL-009, GUI-032 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/hitl/service.py | Tests/integration/test_hitl_gate_set_2.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |

## Root Traceability References

- Capability hierarchy root: `Capability_Hierarchy_Baseline.md`
- Architecture allocation and requirement binding: `Capability_Function_Architecture_Traceability_Matrix.md`
- Functional decomposition detail: `Multi_Agent_Functional_Decomposition.md`
- End-to-end chain registry: `../../Requirements/15_End_To_End_Traceability_Attributes_Registry.md`
