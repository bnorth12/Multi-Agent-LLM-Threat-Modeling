# D-S08-020: Implement Conditional Gate State Reporting (HITL-012-014)

## Issue Summary

Implement requirement HITL-012-014 to track and display conditional gate trigger state, enabling the dashboard to distinguish between gates awaiting review and gates auto-bypassed due to unmet conditions.

## Related Requirements

- HITL-012: Conditional Gate Trigger State Tracking
- HITL-013: Conditional Gate State Enumeration
- HITL-014: Dashboard Conditional Gate Status Display
- HITL-015: Conditional Gate Trigger Metadata

## Severity

**Medium** â€” Feature implementation for improved UX clarity. No blocking defects.

## Acceptance Criteria

- [ ] `HitlGateRecord` dataclass includes `triggered` (bool) and `trigger_reason` (str) fields
- [ ] `GateStatus` enum includes explicit "AUTO_BYPASSED" value (distinct from PENDING)
- [ ] `GateEngine.bypass_gate()` accepts optional `trigger_reason` parameter and sets `triggered=False`
- [ ] Conditional gate methods (`evaluate_and_open_merge_conflict_gate`, `evaluate_and_open_export_consistency_gate`) pass trigger_reason to bypass_gate()
- [ ] Dashboard HITL Gate States table renders "ðŸŸ¢ Auto-Bypassed" emoji + label for gates where `status == AUTO_BYPASSED`
- [ ] Dashboard renders "â“ Open" for gates where `status == OPEN` and `triggered == True`
- [ ] Audit log captures trigger_condition_met and trigger_reason for all conditional gates
- [ ] Unit tests verify trigger state tracking for both triggered and non-triggered conditional gates
- [ ] Integration test verifies dashboard renders correct state for conditional gates at run completion

## Implementation Tasks

### 1. Update `src/threat_modeler/hitl/models.py` â€” Add trigger state fields

**Changes:**
- Add `triggered: bool = False` field to `HitlGateRecord`
- Add `trigger_reason: str | None = None` field to `HitlGateRecord`
- Add `AUTO_BYPASSED = "auto_bypassed"` to `GateStatus` enum
- Update `to_dict()` and `from_dict()` methods to handle new fields

**Files:**
- `src/threat_modeler/hitl/models.py` (HitlGateRecord, GateStatus)

### 2. Update `src/threat_modeler/hitl/gate_engine.py` â€” Track trigger state on bypass

**Changes:**
- Modify `bypass_gate(gate_id, trigger_reason=None)` method signature to accept optional trigger_reason
- Set `record.status = GateStatus.AUTO_BYPASSED` when bypassing
- Set `record.triggered = False` and `record.trigger_reason = trigger_reason`
- Ensure bypassed gates have artifact_snapshot = None (no snapshot needed for non-triggered conditional gates)

**Files:**
- `src/threat_modeler/hitl/gate_engine.py` (GateEngine.bypass_gate method)

### 3. Update `src/threat_modeler/hitl/service.py` â€” Pass trigger reason on conditional gate bypass

**Changes:**
- Update `evaluate_and_open_merge_conflict_gate()` to pass trigger_reason on bypass:
  - Reason format: `f"merge_conflict_count ({count}) < threshold ({threshold})"`
- Update `evaluate_and_open_export_consistency_gate()` to pass trigger_reason on bypass:
  - Reason format: `f"all consistency checks passed (warnings: {count}, errors: {count})"`
- Mark triggered gates: `record.triggered = True` before raising GatePausedError

**Files:**
- `src/threat_modeler/hitl/service.py` (evaluate_and_open_merge_conflict_gate, evaluate_and_open_export_consistency_gate)

### 4. Update `src/threat_modeler/ui/screens/home.py` â€” Render conditional gate state in dashboard

**Changes:**
- In HITL Gate States table rendering logic, check `gate.status == GateStatus.AUTO_BYPASSED`
- Render with emoji "ðŸŸ¢" and label "Auto-Bypassed" instead of "â¬œ Pending"
- For open gates (status == OPEN), render "â“ Open"
- For resolved gates (ACCEPTED_AS_IS, ACCEPTED_CHANGES), render "âœ… Accepted" or "âŒ Rejected"

**Files:**
- `src/threat_modeler/ui/screens/home.py` (HITL Gate States table rendering)

### 5. Update Session State Schema â€” Capture trigger metadata

**Changes:**
- Ensure `session_state["hitl_gates"]` records include triggered and trigger_reason fields
- Verify sync_execution_state_to_session() preserves these fields when copying from registry

**Files:**
- `src/threat_modeler/ui/session.py` (hitl_gates schema or initialization)

### 6. Add Unit Tests â€” Gate trigger state tracking

**File:** `Tests/unit/test_hitl_gate_trigger_state.py` (new)

**Test cases:**
- `test_conditional_gate_not_triggered_sets_auto_bypassed_status` â€” verify gate status = AUTO_BYPASSED when condition not met
- `test_conditional_gate_not_triggered_sets_trigger_reason` â€” verify trigger_reason is populated with explanation
- `test_conditional_gate_triggered_sets_open_status` â€” verify gate status = OPEN when condition is met
- `test_conditional_gate_triggered_flag_true_when_opened` â€” verify triggered = True when gate opens
- `test_auto_bypassed_gate_no_artifact_snapshot` â€” verify bypassed gates don't capture snapshot
- `test_gate_record_to_dict_includes_trigger_fields` â€” verify serialization includes triggered and trigger_reason
- `test_gate_record_from_dict_restores_trigger_fields` â€” verify deserialization restores trigger state

### 7. Add Integration Test â€” Dashboard rendering of conditional gates

**File:** `Tests/integration/test_hitl_dashboard_conditional_gates.py` (new)

**Test case:**
- `test_dashboard_displays_auto_bypassed_for_non_triggered_conditional_gate` â€” run pipeline, verify dashboard shows "ðŸŸ¢ Auto-Bypassed" for gates where condition not met

## Code Locations Summary

| File | Change Type | Details |
|------|-------------|---------|
| `src/threat_modeler/hitl/models.py` | Modify | Add triggered, trigger_reason fields; add AUTO_BYPASSED status |
| `src/threat_modeler/hitl/gate_engine.py` | Modify | Update bypass_gate() to set AUTO_BYPASSED status and trigger_reason |
| `src/threat_modeler/hitl/service.py` | Modify | Pass trigger_reason to bypass_gate() calls in conditional gate methods |
| `src/threat_modeler/ui/screens/home.py` | Modify | Render ðŸŸ¢ Auto-Bypassed for AUTO_BYPASSED gates in dashboard table |
| `src/threat_modeler/ui/session.py` | Review | Verify hitl_gates schema captures triggered and trigger_reason |
| `Tests/unit/test_hitl_gate_trigger_state.py` | New | Unit tests for trigger state tracking |
| `Tests/integration/test_hitl_dashboard_conditional_gates.py` | New | Integration test for dashboard rendering |

## Notes

- This is a pure UX/reporting improvement with no impact on pipeline logic
- Backward compatibility: existing bypassed gates (from prior runs) will have triggered=None or False by default
- No changes needed to orchestrator or stage execution logic
- Conditional gate trigger rules already exist in hitl_trigger_rules_default.json; this work only improves reporting

## Sprint Assignment

2026-08 (post-fix backlog) or 2026-09 (future sprint)

---

**Status**: Open
**Assigned**: TBD
**Blocked By**: None
**Blocks**: None
## Closure Evidence Template

Use this block for future closure updates.

- Resolution date:
- Implementation commit or PR:
- Verification command(s):
- Verification result summary (include pass counts):
- Evidence artifact path(s):
- Reviewer or approver initials:

