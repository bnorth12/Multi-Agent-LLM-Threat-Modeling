# Issue D-S13-024: React Polling Out-of-Order Response Protection

## Issue Summary

Code review identified frontend race-risk in polled run-state loading:

- `loadRunState` applies async results directly to view state.
- Polling and manual refresh paths can overlap requests.
- There is no request generation token or cancellation guard to discard stale responses.

This allows an older response to overwrite a newer state and can reintroduce stale pause or stage data in the UI.

## Related Requirements

- RIC-005
- RHMI-018
- GUI-003B

## Severity

Medium - can transiently misrepresent run state and gate context during active polling.

## Evidence

- `frontend/src/App.tsx`: `loadRunState` sets state without verifying response freshness.
- `frontend/src/App.tsx`: polling effect can dispatch repeated requests while previous requests are still in flight.
- Live run evidence (2026-05-22, run_id `2ba76d34-6930-4e4f-8314-13ccf95b5a00`):
  - Gate 1 UI showed delayed payload population after pause state was already visible.
  - Gate 2 UI initially rendered without full metadata and system information, then filled in later.
  - Pattern is consistent with stale or partial poll responses being rendered before newer complete responses.

## Implemented Scope

1. Add monotonic request generation tracking for run-state fetches.
1. Discard responses that do not match latest generation for selected run.
1. Add tests proving stale responses cannot override newer terminal or gate states.

## Acceptance Criteria

- [ ] Out-of-order `getFullState` responses are ignored.
- [ ] UI reflects latest status and gate payload only.
- [ ] Regression tests cover stale response overwrite scenarios.

## Verification

- `cd frontend; npm run test -- --run src/App.test.tsx --reporter=dot`
- Browser/API simulation with delayed responses verifying newest response wins.
- Live browser/API timing probe asserting UI completeness does not regress between successive poll responses.

## Status

Open
