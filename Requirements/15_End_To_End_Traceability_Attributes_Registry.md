# End To End Traceability Attributes Registry

## Purpose

Define the core, durable requirement-to-evidence trace registry for release and audit decisions.

This core registry intentionally excludes planning-era or remediation-history-only rows.
Historical reconciliation and transient remediation chains are preserved in:

- Requirements/appendices/15_End_To_End_Traceability_Attributes_Registry_Historical_Remediation_Appendix.md

## How To Read This Registry

Interpret each row left-to-right as one complete governed chain:

capability -> function -> requirement -> architecture -> design -> implementation -> verification

Example chain:

- Capability: C01-ORCH-001
- Function: F-ORCH-STATE-TRANSITIONS
- Requirement: C01-ORCH-001
- Implementation: src/threat_modeler/orchestrator.py
- Verification: Tests/unit/test_framework_orchestrator_langgraph.py

If a row does not include stable architecture, stable design, source implementation, and test verification anchors, it belongs in the historical appendix until promoted.

## Function Family Definitions

- Orchestration family (C01-ORCH-001): governs deterministic run sequencing, state transition integrity, and checkpoint continuity.
- LLM family (C11-LLM-001): governs live provider behavior, timeout/retry controls, and normalized provider error semantics.
- HITL family (C12-HITL-001): governs pause/resume/reject gate control and decision evidence durability.
- UI family (C13-UI-001): governs operator interaction surfaces, status projection, and action trace continuity.
- Integration family (C15-INT-001): governs interface and schema contracts between runtime/state and external/internal consumers.
- Delivery/runtime family (C16-PRJ-001): governs artifact continuity and release-facing runtime behavior.
- Administration controls family (C18-ADM-001): governs automated policy checks for branch/PR/checklist/release governance.

## Core Registry Rules

- Core rows must reference canonical IDs only; no wildcard IDs are allowed.
- Core rows must include stable architecture and design artifacts.
- Core rows must include source implementation anchors (not planning issue files).
- Core rows must include executable verification/test anchors.
- Rows failing any core rule move to the historical appendix until corrected.

## Core Required Attribute Set

| Attribute Group | Required Attributes |
|---|---|
| Identity | Slice ID, Capability ID, Function ID, Requirement ID |
| Architecture / Design | Architecture Artifact, Design Artifact, Data-Flow ID |
| Implementation | Source File Path, Symbol / Component |
| Verification | Verification Artifact, Test Artifact ID, Test Level, Evidence Timestamp |
| Governance | Disposition Path, Missing Legs, Process Failure, Remediation Action |

## Promotion Checklist (Appendix -> Core)

Use this checklist to promote a row from the historical appendix into the core registry.
All items must pass.

1. Identity is canonical: Slice ID, capability, function, and requirement IDs are valid and non-placeholder.
1. Architecture and design anchors are stable: no planning-only or temporary artifact references.
1. Implementation anchor is source-based: source file path and symbol/component are concrete and current.
1. Verification is executable: at least one stable test artifact validates the implemented behavior.
1. Governance fields are clean: Missing Legs is `none`, Process Failure is `no`, Remediation Action is `none`.
1. One-line rationale is written: concise statement explains why the row is audit-relevant in the core set.

## Core Registry Table

| Slice ID | Capability ID | Function ID | Requirement ID | Architecture Artifact | Design Artifact | Data-Flow ID | Source File Path | Symbol / Component | Verification Artifact | Test Artifact ID | Test Level | Evidence Timestamp | Disposition Path | Missing Legs | Process Failure | Remediation Action | Audit Rationale |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S12-033 | C01-ORCH-001 | F-ORCH-STATE-TRANSITIONS | C01-ORCH-001 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-ORCH-001 | src/threat_modeler/orchestrator.py | FrameworkOrchestrator | Tests/unit/test_framework_orchestrator_langgraph.py | TST-S12-033-ORCH | Unit | 2026-05-31T22:21:19 | architecture-first | none | no | none | Core orchestration state-transition control path with direct unit verification. |
| R01-003 | C11-LLM-001 | F-C11_LLM_004-TRACE-L2 | C11-LLM-004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-LLM-TRACE-C11_LLM_004 | src/threat_modeler/llm/openai_compatible_adapter.py | OpenAICompatibleAdapter | Tests/e2e/test_live_llm_validation.py | TST-R01-003-LLM | E2E | 2026-05-31T22:21:19 | implementation-first reconciliation | none | no | none | Critical live-LLM behavior and retry governance path validated end-to-end. |
| S12-034 | C12-HITL-001 | F-HITL-GATE-CONTROL | VS-010 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-HITL-010 | src/threat_modeler/hitl/service.py | HITL Gate Control | Tests/integration/test_hitl_gate_set_2.py; Tests/test_hmi_backend_api.py | TST-VS-010 | Governance | 2026-05-31T23:31:50 | architecture-first reconciliation | none | no | none | HITL pause/resume/reject gate behavior is a primary governed decision boundary. |
| S12-013 | C13-UI-001 | F-S12-013-GUI_032-L2 | GUI-032 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-S12-013-GUI_032 | frontend/src/components/HITLGateManager.tsx | F-S12-013-GUI_032-L2 | Tests/integration/test_avionics_expected_results.py | TST-S12-013-GUI_032 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | UI gate-control surface directly affects governed operator interventions. |
| S12-017 | C13-UI-001 | F-S12-017-RHMI_016-L2 | RHMI-016 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-S12-017-RHMI_016 | frontend/src/App.test.tsx | F-S12-017-RHMI_016-L2 | Tests/e2e/test_frontend_react_mui_full_workflow.py | TST-S12-017-RHMI_016 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Restart and run-continuity UI behavior is release-critical for operator trust. |
| S12-020 | C16-PRJ-001 | F-S12-020-GUI_015-L2 | INT-005 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md | DF-S12-020-INT_005 | frontend/src/components/TokenUsageView.tsx | F-S12-020-GUI_015-L2 | Tests/integration/test_validation_gates.py | TST-S12-020-INT_005 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Telemetry and interface continuity are needed for governed runtime observability. |
| S12-022 | C16-PRJ-001 | F-S12-022-GUI_020-L2 | GUI-020 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-S12-022-GUI_020 | frontend/src/App.test.tsx | F-S12-022-GUI_020-L2 | Tests/integration/test_canonical_graph_viewer.py | TST-S12-022-GUI_020 | Governance | 2026-05-31T23:31:50 | architecture-first reconciliation | none | no | none | Diagram-view interaction is a key evidence consumption path for reviewers. |
| S12-025 | C16-PRJ-001 | F-S12-025-INT_011-L2 | INT-011 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Agent_Subsystem_Design_Specification.md | DF-S12-025-INT_011 | frontend/src/App.tsx | F-S12-025-INT_011-L2 | Tests/integration/test_results_export_quick_preview.py | TST-S12-025-INT_011 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Export/report path ties governed outputs to user-facing evidence artifacts. |
| S12-026 | C16-PRJ-001 | F-S12-026-GUI_006-L2 | INT-010 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Agent_Subsystem_Design_Specification.md | DF-S12-026-INT_010 | frontend/src/App.tsx | F-S12-026-GUI_006-L2 | Tests/integration/test_results_export_quick_preview.py | TST-S12-026-INT_010 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Export-panel behavior materially impacts release evidence completeness. |
| S12-027 | C16-PRJ-001 | F-S12-027-INT_008-L2 | INT-008 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-S12-027-INT_008 | frontend/src/App.tsx | F-S12-027-INT_008-L2 | Tests/integration/test_results_export_quick_preview.py | TST-S12-027-INT_008 | Governance | 2026-05-31T23:31:50 | architecture-first reconciliation | none | no | none | Mitigation-view and export coupling is a core governance review surface. |
| S12-028 | C16-PRJ-001 | F-S12-028-PRJ_013-L2 | INT-002 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Agent_Subsystem_Design_Specification.md | DF-S12-028-INT_002 | frontend/src/components | F-S12-028-PRJ_013-L2 | Tests/unit/test_input_ingestion.py | TST-S12-028-INT_002 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Prior-graph input continuity protects deterministic rerun and recovery workflows. |
| S12-029 | C16-PRJ-001 | F-S12-029-GUI_005-L2 | INT-008 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md | DF-S12-029-INT_008 | frontend/src/App.tsx | F-S12-029-GUI_005-L2 | Tests/integration/test_results_export_quick_preview.py | TST-S12-029-INT_008 | Governance | 2026-05-31T23:31:50 | architecture-first reconciliation | none | no | none | Threat-review viewer split is safety-critical for accurate operator decisions. |
| S12-030 | C16-PRJ-001 | F-S12-030-GUI_003-L2 | GUI-006 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | DF-S12-030-GUI_006 | frontend/src/App.tsx | F-S12-030-GUI_003-L2 | Tests/Formal_Qualification_Test_Plan.md | TST-S12-030-GUI_006 | Governance | 2026-05-31T23:24:46 | architecture-first reconciliation | none | no | none | Header/navigation consolidation affects discoverability of governed artifacts. |
| S13-001 | C01-ORCH-001 | F-S13-001-ORCH_001-L2 | INT-005 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md | DF-S13-001-INT_005 | frontend/src/components/TokenUsageView.tsx | F-S13-001-ORCH_001-L2 | Tests/integration/test_validation_gates.py | TST-S13-001-INT_005 | Governance | 2026-05-31T23:24:46 | architecture-first remediation | none | no | none | Sprint baseline orchestration alignment is foundational for future governance slices. |
| S13-002 | C18-ADM-001 | F-ADM-GOV-CONTROLS-L2 | ADM-001 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-ADM-001 | scripts/verify_administration_controls.py | verify_administration_controls.evaluate_controls | Tests/unit/test_administration_controls.py | TST-S13-002-ADM-001 | Unit | 2026-05-31T22:21:19 | architecture-first remediation | none | no | none | Administration policy checks enforce branch/PR planning governance integrity. |
| S13-002 | C18-ADM-001 | F-ADM-GOV-CONTROLS-L2 | ADM-004 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-ADM-001 | scripts/verify_administration_controls.py | verify_administration_controls.evaluate_controls | Tests/unit/test_administration_controls.py | TST-S13-002-ADM-004 | Unit | 2026-05-31T22:21:19 | architecture-first remediation | none | no | none | Checklist and gate compliance is required for controlled release readiness. |
| S13-004 | C01-ORCH-001 | F-S13-001-ORCH_001-L2 | PRJ-005 | docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | docs/design/software/Runtime_And_Orchestration_Design_Specification.md | DF-ORCH-001 | src/threat_modeler/backend/run_manager.py | F-S13-001-ORCH_001-L2 | scripts/verify_architecture_design_surface_coverage.py | TST-S13-004-PRJ-005 | Governance | 2026-05-31T22:21:19 | architecture-first remediation | none | no | none | Architecture-design surface coverage is a release gate for trace integrity. |

## Historical Remediation Appendix

The complete prior registry snapshot, including remediation-history rows and planning-era reconciliation chains, is preserved at:

- Requirements/appendices/15_End_To_End_Traceability_Attributes_Registry_Historical_Remediation_Appendix.md
