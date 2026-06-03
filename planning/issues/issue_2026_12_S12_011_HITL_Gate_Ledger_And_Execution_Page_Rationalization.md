# S12-011: HITL Gate Ledger Refinement and Execution Page Rationalization

Sprint: 2026-12
Requirement ID: GUI-030
Parent Capability ID: C13-UI-001
Parent Function ID: F-GUI-TRACEABILITY-L1
Child Function ID: F-S12-011-GUI_030-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_011_HITL_Gate_Ledger_And_Execution_Page_Rationalization.md
Verification Method: Sprint traceability verification
Status: In Review

## Issue Summary

The React HMI workflow evolved from a split execution-vs-gates model into a gate-centric operational flow. The UI now exposes a persistent execution timeline footer and a unified HITL gate ledger, which makes the standalone execution page largely redundant. This change requires explicit Sprint 2026-12 governance so the implemented behavior is traceable and the remaining execution-page decision is handled intentionally.

## Related Requirements

- GUI-030
- GUI-031

## Severity

High - operator workflow clarity and governance alignment

## Implemented Scope

1. Display all HITL gates in pipeline order on one page.
1. Summarize lifecycle counts for Approved, Rejected, Bypassed, and Pending states.
1. Keep the operator on the HITL Gate page while execution resumes.
1. Provide centered plain-language status text in the persistent footer timeline.
1. Rename navigation label to `HITL Gate` for clarity.

## Open Decision

The standalone execution page currently provides minimal unique value because:

- the footer timeline is visible globally,
- the footer now includes live run-status text,
- the HITL Gate page can be used during active execution and pause/resume workflows.

Execution-page removal or repurposing SHALL be treated as a separate approved decision, not an implicit side effect of the HITL ledger refinement.

## Acceptance Criteria

- [x] HITL Gate page shows all gates in defined order.
- [x] Lifecycle summary counts are displayed for Approved, Rejected, Bypassed, and Pending.
- [x] Footer timeline status text remains visible and centered across pages.
- [x] Resume does not force navigation back to the execution page.
- [ ] Product/program decision recorded for execution-page disposition: retain, repurpose, or remove.
- [ ] Follow-on requirement added if execution page is removed or materially repurposed.

## Verification

- `frontend: npm run test -- --run src/components/HITLGateManager.test.tsx` -> `5 passed`
- `PYTHONPATH=src python -m pytest Tests/test_hmi_backend_api.py Tests/integration/test_hitl_gate_set_2.py Tests/integration/test_avionics_expected_results.py -q` -> `35 passed`

## Status

In Review

## GitHub Tracking

- Repository issue: #65

## Owner Guidance

- Treat the implemented UI changes as Sprint 2026-12 governed scope.
- Do not remove the execution page until the product/program decision is captured and traceability is updated.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md
