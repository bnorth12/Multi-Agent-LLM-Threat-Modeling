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
