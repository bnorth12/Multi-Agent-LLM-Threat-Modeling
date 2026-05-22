# S12-012: Runtime Monitoring Status Continuity

## Issue Summary

Sprint 2026-12 monitoring continuity kept operators on the HITL Gate page with persistent
footer status text, but the React HMI lost two operator-facing runtime cues that were still
needed during active execution:

- visible watchdog telemetry showing heartbeat age versus timeout near the execution timeline
- an animated running-state indicator in the header while a stage is actively running

Without those cues, operators could monitor status text but had a weaker signal for live
pipeline liveness and heartbeat staleness during ongoing runs.

## Related Requirements

- GUI-031
- RHMI-005
- S12-REQ-012

## Severity

Medium - reduced runtime monitoring clarity during active execution

## Implemented Scope

1. Restore a compact watchdog telemetry badge in persistent execution-status chrome next to the timeline.
1. Restore an animated running-state indicator in the header while a stage is actively running.
1. Preserve centered plain-language execution status text and HITL-page monitoring continuity.
1. Add focused React component coverage for runtime-status presentation behavior.

## Acceptance Criteria

- [x] Operators remain on the HITL Gate page while runs continue or resume.
- [x] The execution timeline area shows watchdog heartbeat age versus timeout when telemetry exists.
- [x] The header shows an animated running-state indicator while a stage is actively running.
- [x] Runtime-status surfaces remain coherent for running, paused, rejected, and completed states.
- [x] Sprint 2026-12 governance docs updated with requirement and traceability coverage.

## Verification

- `frontend: npm run test -- --run src/App.test.tsx src/components/ExecutionProgress.test.tsx src/components/HITLGateManager.test.tsx`
- `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q`
- Browser verification of active-run header cue and timeline watchdog telemetry.

## Status

In Review

## GitHub Tracking

- Repository issue: #63

## Owner Guidance

- Keep runtime-status cues compact so they remain visible without pushing operators away from
  the gate ledger or artifact workflow.
- If future work adds richer liveness diagnostics beyond heartbeat age/timeout and stage-running
  indication, split that scope into a follow-on issue instead of silently expanding S12-012.
