# Runtime State and Input Contract Requirements

Date: 2026-05-22
Status: Active
Scope: Runtime execution state authority, Gate 0 readiness sequencing, input parsing parity, and prompt/schema alignment controls.

Related requirements:

- HITL-009 through HITL-011
- GUI-032
- RHMI-005, RHMI-017

| ID | Name | Requirement Text | Requirement Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|---|
| RIC-001 | Gate 0 Data Readiness Before Trigger | The orchestrator SHALL NOT open Gate 0 until preflight input integrity data is present and minimally complete for gate review payload construction. If readiness is not achieved within the configured wait window, execution SHALL fail with an explicit readiness timeout error. | Opening Gate 0 before input data is ready creates race conditions and empty or misleading review artifacts. | Unit test + integration test | Verified by orchestrator tests that Gate 0 waits for readiness and fails with deterministic timeout when readiness is never met. |
| RIC-002 | Terminal Cancelled State Authority | The runtime run manager SHALL treat user cancellation as a first-class terminal CANCELLED status for active and paused runs, SHALL clear pause metadata at cancellation time, and SHALL prevent paused overlays from superseding terminal status in API/UI projections. | Operators must distinguish intentional cancellation from runtime failure and must never see stale paused status after cancel. | Unit test + frontend component test | Verified by backend cancellation tests and React status rendering tests asserting cancelled precedence over stale gate metadata. |
| RIC-003 | Input Parsing Contract Parity | Frontend submission preprocessing SHALL preserve parse parity with backend expectations by placing parsed table data into structured state and excluding raw binary spreadsheet payloads from free-text fields. | Parsing contract drift causes Stage 1 and downstream model behavior divergence even when submissions appear successful. | Integration test + smoke workflow | Verified by avionics and React submission smoke tests showing parsed table payload availability and binary injection prevention. |
| RIC-004 | Prompt Expected-Output and Schema Drift Detection | Prompt expected-output declarations SHALL remain aligned with enforced JSON/schema contracts; mismatch conditions SHALL be detected by validation and surfaced as actionable defects before release sign-off. | Prompt/schema drift creates silent semantic failures and non-deterministic downstream artifact quality. | Schema validation + regression test + review checklist | Verified by schema contract checks and release review evidence documenting prompt expected-output alignment results. |
| RIC-005 | State Publication Ordering Invariant | Runtime state publication SHALL enforce a deterministic ordering invariant for Gate 0: paused status and pause_gate metadata SHALL NOT be externally projected until the corresponding Gate 0 preflight artifact payload is present in checkpoint-backed gate state. This invariant SHALL be treated as an architecture contract and SHALL be enforced by API projection and run-lifecycle tests. | Race prevention here is a correctness and architecture concern, not a performance optimization. Operators and automation require causally ordered state publication to avoid false pause signals and governance drift. | API integration test + lifecycle unit test + timing probe governance check | Verified by regression tests asserting paused projection is withheld until Gate 0 preflight payload is present, plus governance timing-probe evidence attached to sprint execution records. |

## Verification Evidence Targets

- Tests/unit/test_framework_orchestrator_langgraph.py
- Tests/unit/test_run_manager.py
- Tests/test_hmi_backend_api.py
- frontend/src/App.test.tsx
- Tests/integration/test_avionics_expected_results.py
- docs/schemas/*.json

## Traceability Seeds

- Issue: D-S13-022
- Planned matrix row owner: Sprint governance lead

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- RIC-00x / runtime state and input contract requirements derived from C01-ORCH-001 (orchestration and stage control), C13-UI-001 (UI control surface and state visibility), C15-INT-001 (interface contracts), and C16-PRJ-001 (runtime reliability) in Capability_Hierarchy_Baseline.md
- Strong linkage to C01-STATE-00x L2 capabilities and F-ORCH-TRACEABILITY-L1 / F-UI-TRACEABILITY-L1 functions

### Allocated To

- RIC-001 and related state/input contracts allocated to C01-ORCH-001 / C13-UI-001 and realized in Runtime_And_Orchestration_Design_Specification.md, backend/run_manager.py, state.py, and the UI projection components (ExecutionProgress, ArtifactsViewer, TokenUsageView, etc.)

### Refines

- 01_Project_Requirements.md (PRJ-019 asynchronous backend state, PRJ-023 LangGraph, PRJ-025 non-Streamlit runtime) and 10_GUI_Requirements.md (state projection and input surfaces) are refined by the detailed runtime state and input contract statements here
- Component orchestrator and UI state requirements further refine these

### Satisfied By

- Runtime state authority, async projection, gate context persistence, and input contract enforcement satisfied by src/threat_modeler/backend/run_manager.py, src/threat_modeler/state.py (FrameworkState), src/threat_modeler/orchestrator.py, src/threat_modeler/ui/screens/* (execution, input_entry, stage_results, token_usage, artifacts viewer), frontend/src/components/ExecutionProgress.tsx, ArtifactsViewer.tsx, PipelineConfig.tsx, and Runtime_And_Orchestration_Design_Specification.md
- 15_End_To_End rows (S13-005B/C/D, S12-020, S13-004, S13-005* RIC/GUI projection rows) cite Runtime_And_Orchestration_Design_Specification.md + run_manager + backend state + UI components as the design + implementation for these contracts
- Prompt and snapshot persistence (Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md) support the durable state side

### Verified By

- Tests/integration/test_validation_gates.py, Tests/test_hmi_backend_api.py, Tests/unit/test_ui_app_shell.py, Tests/integration/test_agent_pipeline_completeness.py (state projection, gate ordering, input contract, async runtime behavior)
- FQT cases that exercise input entry, gate state, stage results, token telemetry, and snapshot/restore (FQT-003, FQT-004/005, FQT-007, FQT-008, FQT-010)
- 15_End_To_End verification artifacts and Test Artifact IDs for the RIC / state-projection rows
- Governance surface coverage and sprint traceability verifiers

### Depends On

- 01_Project_Requirements.md (PRJ-019/023/025/028/029 state, LangGraph, liveness, gate enforcement), 03_HITL_Requirements.md (gate state), 10_GUI_Requirements.md (UI state surfaces)
- Runtime_And_Orchestration_Design_Specification.md (primary design authority), Canonical_Graph_Lifecycle_And_Validation_Design_Specification.md, Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md
- 15_End_To_End_Traceability_Attributes_Registry.md (the governed record of state/input legs)
- C01-ORCH-001 / C13-UI-001 / C15-INT-001 capabilities and their L2/L3 functions
- 05_Verification_Strategy.md and FQT for the verification methods applied to runtime contracts
- 18_Traceability_Governance_Operating_Model.md (RIC requirements are a primary example of "Architecture satisfaction" upward from design to requirement and "Implementation" downward)
