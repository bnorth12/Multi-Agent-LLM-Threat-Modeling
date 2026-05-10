# Conditional Gate State Reporting Requirements

**Amendment to HITL-010 and HITL-011**

Date: 2026-05-08
Status: New Requirement
Related Sprint: 2026-08 (post-fix backlog)

---

## Overview

Conditional HITL gates (Merge Conflict Resolution and Export Consistency) are triggered only when specific error/warning thresholds are met. When these thresholds are not met, the gates automatically close without analyst intervention. The dashboard must clearly report this distinction so analysts can understand whether a gate is:

1. **Awaiting Review** (open, waiting for decision)
2. **Not Triggered** (condition not met, auto-bypassed, no action needed)
3. **Bypassed** (conditional gate skipped, recorded in audit trail)

Currently, both active and skipped conditional gates show as "Pending" in the Run Dashboard, creating ambiguity about whether the analyst should take action.

---

## Requirements

| ID | Name | Requirement Text | Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|---|
| HITL-012 | Conditional Gate Trigger State Tracking | Orchestrator SHALL track and record for each conditional gate (HITL-010, HITL-011) whether the trigger condition was met (triggered=true) or not met (triggered=false) at the point the gate evaluation occurs. This state SHALL be persisted in the run result record. | Clear tracking of trigger state enables deterministic reporting and audit compliance. | Test | Verified by run completion assertions confirming conditional gate trigger state is recorded in result_state for both Merge Conflict Resolution and Export Consistency gates. |
| HITL-013 | Conditional Gate State Enumeration | Conditional gate state in the run record SHALL have one of three explicit values: (1) "Open" when condition is triggered and gate is awaiting analyst decision, (2) "Auto-Bypassed" when condition is not met and gate automatically closes, (3) "Rejected" or "Accepted" after analyst decision. The dashboard SHALL NOT report "Pending" for gates that are auto-bypassed. | Explicit state values prevent ambiguity. Analysts must clearly distinguish gates waiting for review from gates that were auto-closed. | Test | Verified by HITL gate state table tests asserting correct enumeration values after run completion. Dashboard displays "Auto-Bypassed" (not "Pending") for conditional gates when condition not met. |
| HITL-014 | Dashboard Conditional Gate Status Display | The Run Dashboard HITL Gate States table SHALL display conditional gates with status "🟢 Auto-Bypassed" (distinct emoji) when the gate's trigger condition is not met, and SHALL display mandatory gates and triggered conditional gates with status "❓ Open" or "✅ Accepted" or "❌ Rejected" as appropriate. | Clear visual distinction in the dashboard prevents operator confusion about required vs. skipped gates. | Test | Verified by dashboard table after conditional gate auto-bypass, confirming emoji and label distinctly indicate auto-bypass vs. open/accepted/rejected states. |
| HITL-015 | Conditional Gate Trigger Metadata | Conditional gate record in the run result SHALL include trigger_condition_met (boolean) and trigger_reason (string) fields documenting which specific threshold or condition was evaluated and whether it was satisfied. | Audit trail must capture why gates were or were not triggered. | Inspection | Verified by audit record review confirming trigger_condition_met and trigger_reason are present and accurately reflect the gate evaluation logic. |

---

## Implementation Notes

### Affected Gates

- **HITL-010 (Merge Conflict Resolution)**: Triggered if merge_conflict_count >= 5 OR critical_field_conflict_count >= 1 OR conflict_severity_max is "high". Otherwise auto-bypassed.
- **HITL-011 (Export Consistency)**: Triggered if consistency_warning_count > 10 OR any error_count > 0. Otherwise auto-bypassed.

### Code Locations

- Orchestrator gate logic: `src/threat_modeler/orchestration/orchestrator.py` (transition_to_next_gate)
- UI gate state display: `src/threat_modeler/ui/screens/home.py` (HITL Gate States table rendering)
- Session state gate record: `src/threat_modeler/ui/session.py` (hitl_gates schema)

### Gate State Schema Update

```json
{
  "gate_id": "gate_6_merge_conflict_resolution",
  "state": "Auto-Bypassed",
  "triggered": false,
  "trigger_reason": "merge_conflict_count (0) < threshold (5)",
  "triggered_at": null,
  "decided_at": null,
  "decision": null,
  "decision_actor": null,
  "decision_role": null,
  "rationale": null
}
```

---

## Related Issues

- D-S08-019 (dashboard reporting of conditional gates) — resolved by this amendment
- HITL-010, HITL-011 (conditional gate definitions)
- GUI-003A (gate-aware pause visibility)
