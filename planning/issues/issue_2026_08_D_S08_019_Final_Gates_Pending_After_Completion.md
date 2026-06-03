# D-S08-019: Final HITL Gates Remain Pending After Pipeline Completion

**Status: RESOLVED (Working as Designed)**
**Resolution Date**: 2026-05-08
**Resolution Type**: UX Improvement (New Requirement HITL-012-014)

## Defect Summary

During live browser E2E run (`run_id=299dbd96-ed91-4bf8-94de-9fedbc6da2b3`), all 9 pipeline stages completed successfully (ðŸŸ¢ COMPLETED) but the final HITL gate states displayed an inconsistency:

- Gate 6 (`gate_6_merge_conflict_resolution`) â€” â¬œ Pending
- Gate 7 (`gate_7_export_consistency`) â€” â¬œ Pending

While gates 0â€“5 were correctly transitioned to Accepted_As_Is or Bypassed status.

## Severity

**Low** â€” UX clarity issue, not a pipeline logic defect. Gates 6 and 7 are **conditional gates** that only trigger when specific error/conflict thresholds are met. In this test run, no conflicts or consistency warnings were detected, so the gates were never triggered. They correctly remained in a non-interactive state. The issue is that the dashboard reported them as "Pending" instead of explicitly marking them as "Auto-Bypassed" or "Not Triggered".

## Resolution

**Root Cause:** Conditional gates (HITL-010, HITL-011) lack explicit state reporting to distinguish between:

- **Open** â€” condition triggered, awaiting analyst decision
- **Auto-Bypassed** â€” condition not met, gate automatically closed, no action needed

**Disposition:** Working as designed. The gates function correctly. New requirement HITL-012-014 has been created to improve dashboard reporting of conditional gate state.

**UX Improvement:**

- Implement gate trigger state tracking (triggered: true/false)
- Update dashboard to display "ðŸŸ¢ Auto-Bypassed" for conditional gates when not triggered
- Add trigger_reason field to gate record for audit trail

**Implementation Target:** Future sprint (post-S08)

## Verification Evidence

### Test Command

```powershell
.venv\Scripts\pytest.exe Tests/ -v
```

### Result

- Full sprint regression remained passing while defect was dispositioned as working-as-designed.
- Follow-on implementation is tracked in D-S08-020.

## Reproduction

1. Configure xAI/Grok-4 provider in Streamlit Pipeline Configuration.
1. Upload ICD file (`icd_avionics_v1.csv`) and system name in Input Entry.
1. Click "â–¶ Start Threat Model Run".
1. Approve and resume through gates 1â€“5 via Threat Review screen.
1. Monitor Run Dashboard (Home screen) for completion.
1. Observe: All 9 stages show âœ… Complete, pipeline status = "Pipeline completed successfully", but gate_6 and gate_7 still show â¬œ Pending in HITL Gate States table.

## Expected Behavior

One of:

- **Option A (Most likely)**: Gates 6 and 7 should auto-bypass or auto-approve during pipeline completion if they are not user-decision gates (similar to gate_0).
- **Option B**: Pipeline should not transition to "completed successfully" until all gates are resolved.
- **Option C**: Gates 6 and 7 should never appear in the pipeline flow for this fixture if they are not applicable to the scenario.

## Observed Behavior

Gates 6 and 7 remain in Pending state indefinitely after run completion, creating a misleading dashboard state where the user expects either a gate decision prompt or auto-closure.

## Root Cause Hypothesis

The gate state persistence logic in `src/threat_modeler/ui/execution.py` or the orchestrator's gate transition logic may not be updating the final two gate states when the pipeline reaches completion. This could be:

- Missing gate auto-bypass logic for non-interactive gates at end-of-pipeline.
- Incomplete state sync between orchestrator completion event and UI gate state table.

## Impact

- User confusion on Run Dashboard (unclear whether run is truly complete or awaiting further action).
- No functional impact on exported artifacts (stages completed, export working).
- Potential blocker for automated E2E validation if tests assert "all gates resolved before completion".

## Related Issues

- [D-S08-004](issue_2026_08_D_S08_004_HITL_Pause_Handling_UX.md) (previous HITL pause handling issues)
- [D-S08-010](issue_2026_08_D_S08_010_Navigation_Content_Sync.md) (state sync issues)

## Investigation Checklist

- [ ] Confirm gates 6 and 7 are valid gates for this pipeline or if they should be conditionally skipped.
- [ ] Trace orchestrator's `transition_to_next_gate()` logic to verify gate advancement at completion boundary.
- [ ] Review gate auto-bypass logic (similar to gate_0) to see why gates 6 and 7 don't auto-resolve.
- [ ] Check `sync_execution_state_to_session()` in UI layer to confirm gate state snapshot is captured at run completion, not stale.
- [ ] Add explicit test case: `test_e2e_all_gates_resolved_at_completion` to verify final gate states are not Pending after run completion.

## Notes

- Run ID: `299dbd96-ed91-4bf8-94de-9fedbc6da2b3`
- System: Avionics Data Bus Network
- ICD: icd_avionics_v1.csv
- Provider: xAI / Grok-4
- Date: 2026-05-08
- Elapsed: 29737s (full run with human-in-the-loop gate approvals)

---

**Status**: Open
**Assigned**: TBD
**Sprint**: 2026-08 (post-sprint backlog or future refinement)

## Closure Evidence Template

Use this block for future closure updates.

- Resolution date:
- Implementation commit or PR:
- Verification command(s):
- Verification result summary (include pass counts):
- Evidence artifact path(s):
- Reviewer or approver initials:
