# Capability Hierarchy Baseline

## Purpose

Define the authoritative capability hierarchy used as the root architecture artifact for end-to-end traceability.

This document is the capability-side authority for:

- L0 mission capability intent
- L1 capability partitioning
- L2 capability refinements used by remediation slices
- stable parent-child relationships consumed by function and traceability artifacts

## Governance Rules

- Capability IDs are immutable after publication.
- Every L2 capability must map to at least one function ID in `Function_Hierarchy_Registry.md`.
- Every active remediation slice must reference a capability ID from this hierarchy.
- Every capability row must identify requirement hierarchy, architecture/design authority, implementation anchor, and verification artifact path.

## Capability Hierarchy

| Level | Capability ID | Parent Capability ID | Capability Name | Capability Intent | Governing Requirement Anchors | Hierarchical Requirement Artifact | Architecture and Design Authority | Implementation Anchor | Verification and Artifact Anchor |
|---|---|---|---|---|---|---|---|---|---|
| L0 | CAP-L0-THREAT-MODELER | none | Multi-Agent Threat Modeling Mission | Produce governed, auditable threat-model outputs from structured and unstructured sources. | PRJ-001, PRJ-003, PRJ-005 | Requirements/04_Traceability_Matrix.md | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/integration/test_agent_pipeline_completeness.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | C01-ORCH-001 | CAP-L0-THREAT-MODELER | Orchestration and Stage Control | Govern deterministic stage advancement, state continuity, and controlled transition behavior. | C01-ORCH-001, ORCH-001, ORCH-002, ORCH-003 | Requirements/04_Traceability_Matrix.md | docs/architecture/Multi_Agent_Logical_Decomposition.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/orchestrator.py | Tests/unit/test_framework_orchestrator_langgraph.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | C11-LLM-001 | CAP-L0-THREAT-MODELER | Live Model Integration Governance | Control live-model request behavior, timeout budgets, retries, and fail-closed safeguards. | C11-LLM-004, LLM-004 | Requirements/14_Sprint_2026_12_Transitional_Requirement_Registry.md; Requirements/15_End_To_End_Traceability_Attributes_Registry.md | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py | Tests/e2e/test_live_llm_validation.py; Tests/unit/test_openai_compatible_adapter.py |
| L1 | C12-HITL-001 | CAP-L0-THREAT-MODELER | Human-in-the-Loop Governance | Enforce analyst gate intervention, pause/resume controls, and decision accountability. | HITL-001, HITL-009, HITL-012, GUI-032 | Requirements/03_HITL_Requirements.md; Requirements/04_Traceability_Matrix.md | docs/architecture/HMI_Architecture_Blueprint.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | src/threat_modeler/hitl/service.py | Tests/integration/test_hitl_gate_set_2.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | C13-UI-001 | CAP-L0-THREAT-MODELER | User Interface Control Surface | Provide governed runtime controls, status visibility, and action boundaries for analysts. | GUI-002, GUI-003, GUI-012, GUI-032 | Requirements/10_GUI_Requirements.md; Requirements/12_React_HMI_Traceability_To_Tests.md | docs/architecture/HMI_Architecture_Blueprint.md; docs/design/software/Agent_Subsystem_Design_Specification.md | frontend/src/components/HITLGateManager.tsx | Tests/e2e/test_browser_run_validation.py; Tests/integration/test_markdown_viewer_editor.py |
| L1 | C14-VER-001 | CAP-L0-THREAT-MODELER | Verification and Validation Governance | Ensure verification evidence, execution records, and qualification trace continuity. | VS-009, SCR-014 | Requirements/05_Verification_Strategy.md | docs/architecture/Multi_Agent_Function_And_Interface_Requirements_Matrix.md; docs/design/software/Export_And_Evidence_Packaging_Design_Specification.md | scripts/verify_sprint_traceability.py | planning/Test_Execution_Summary_Sprint_2026_01.md; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | C15-INT-001 | CAP-L0-THREAT-MODELER | Integration and Interface Integrity | Maintain interface contracts, boundary validation, and integration consistency. | INT-001, INT-002, INT-005, INT-009 | Requirements/02_Interface_Requirements.md | docs/architecture/Multi_Agent_Interface_Control_Document.md; docs/design/system/External_Interface_And_Integration_Design_Package.md | src/threat_modeler/config.py | Tests/integration/test_validation_gates.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L1 | C16-PRJ-001 | CAP-L0-THREAT-MODELER | Product Delivery and Runtime Reliability | Maintain project-level runtime reliability, orchestration integrity, and release readiness controls. | PRJ-001, PRJ-002, PRJ-011, PRJ-023, PRJ-030 | Requirements/01_Project_Requirements.md | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/software/Runtime_And_Orchestration_Design_Specification.md | scripts/governance_autoflow.py | independent_reviews/latest/independent_review_2026-01_pre-push.json |
| L1 | C17-SCR-001 | CAP-L0-THREAT-MODELER | Security and Compliance Runtime Controls | Enforce runtime and evidence controls required for security and compliance operation. | SCR-014 | Requirements/04_Traceability_Matrix.md | docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md; docs/design/system/System_Deployment_And_Operating_Modes_Design.md | src/threat_modeler/backend/run_manager.py | Tests/unit/test_token_usage_runtime.py; Requirements/15_End_To_End_Traceability_Attributes_Registry.md |
| L2 | C11-LLM-004-CAP | C11-LLM-001 | Live LLM Timeout and Retry Capability | Constrain live provider invocation with deterministic timeout and bounded retry governance. | C11-LLM-004, LLM-004 | Requirements/14_Sprint_2026_12_Transitional_Requirement_Registry.md | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md; docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | src/threat_modeler/llm/openai_compatible_adapter.py | Tests/e2e/test_live_llm_validation.py; planning/issues/issue_2026_01_R01-003_C11_LLM_004_Architecture_Traceability_Remediation.md |

## Traceability Entry Criteria

Before a new requirement can be declared traceable, confirm:

- requirement ID maps to a capability row in this file
- capability row links to at least one function in `Function_Hierarchy_Registry.md`
- downstream architecture/design/implementation references are populated in `Requirements/15_End_To_End_Traceability_Attributes_Registry.md`
