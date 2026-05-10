# D-S08-025: Backend Runtime State Authority (Async) and HMI Projection

## Issue Summary

Current UI behavior still relies on Streamlit session-local state for portions of provider and run context. The backend SHALL become the single source of truth for runtime state, and the HMI SHALL only project backend-provided state snapshots.

## Related Requirements

- PRJ-019: Asynchronous Backend State Authority
- GUI-016: Backend-Owned Runtime State Projection
- PRJ-016: Analyst GUI operational consistency

## Severity

High - Architectural integrity and operational correctness issue affecting cross-screen consistency and reload behavior.

## Acceptance Criteria

- [ ] Backend runtime state store exists and is thread-safe.
- [ ] Run lifecycle status is written by async execution path to backend state.
- [ ] HMI screen rendering reads run/provider status from backend state projection.
- [ ] Browser refresh and screen navigation do not require reconfiguration to recover provider/run context.
- [ ] Session state only caches view inputs; it does not own authoritative runtime status.
- [ ] Unit tests validate backend-state restoration and projection behavior.

## Implementation Scope

### Code Changes

- Add backend runtime-state module for process-local authoritative state.
- Route settings persistence and run lifecycle updates through backend state APIs.
- Ensure UI synchronization functions hydrate session from backend projection only.

### Verification

- Start live run, navigate all screens, refresh browser, confirm provider and run state consistency.
- Confirm paused/resumed run status remains coherent on Home, Stage Results, Threat Review.

### Verification Evidence

Command:

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit/test_ui_app_shell.py Tests/unit/test_live_mode_failover_halt.py -q --tb=short
```

Result:

- 109 passed
- Confirms runtime-state projection pathways and live-mode fail-closed behavior remain stable after backend-state alignment changes.

## Notes

- This item is prerequisite architecture for durable event-driven run tracking epic work.

---

Status: In Progress
Assigned: Engineering
Sprint: 2026-08
