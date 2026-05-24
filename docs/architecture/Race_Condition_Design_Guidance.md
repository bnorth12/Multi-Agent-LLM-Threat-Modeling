# Race Condition Design Guidance

Status: Active
Date: 2026-05-22
Owner: Architecture and Runtime Governance

## Purpose

Define architecture-level controls for race-condition prevention across backend runtime, API projection, and frontend polling so state transitions remain causally ordered and operator-safe.

## Scope

- Backend run lifecycle and shared in-memory registries
- API state projection and serialization paths
- Frontend polling, request concurrency, and state application ordering
- HITL gate pause and resume publication semantics

## Design Invariants

1. Publication after data readiness: A state transition SHALL NOT be externally projected before its required payload is available.
1. Single source of authority: Runtime status SHALL be derived from one authoritative state contract per projection boundary.
1. Atomic transition bundles: Status, pause gate, and gate payload fields SHALL transition as one logically consistent bundle.
1. Deterministic monotonicity: State progression SHALL be monotonic for terminal and gate-specific transitions unless an explicit reset action occurs.
1. Stale response suppression: Frontend SHALL discard out-of-date API responses when newer requests have already completed.

## Backend Controls

- Hold registry lock for read snapshots that include status and references used for projection decisions.
- Avoid shallow-copy publication of mutable objects when background threads can mutate nested fields.
- Use explicit transition helpers for status plus pause metadata updates.
- Encode gate publication guards at API boundary, not only at orchestrator trigger points.

## Frontend Controls

- Use request sequencing or cancellation (request token or monotonic request ID) for polled run-state calls.
- Apply poll-state updates only when the response corresponds to current selected run and latest request generation.
- Keep polling effect dependencies minimal to avoid interval churn and overlapping async requests.
- Preserve terminal-state precedence over stale pause metadata.

## Verification Controls

1. Unit tests: transition helpers and projection guards.
1. API integration tests: paused-state publication withheld until required gate payload exists.
1. Timing probe: timestamped poll evidence for key transition milestones.
1. Frontend tests: out-of-order response suppression and terminal-state precedence.
1. Governance review: sprint checklist confirms race-control evidence attached before closure.

## Governance Application Rules

- Any bug involving stale status, missing gate payload at pause, or out-of-order UI transitions SHALL be treated as an architecture correctness defect.
- Issue closure SHALL require both functional fix evidence and race-control verification evidence.
- New runtime features that add asynchronous state transitions SHALL include a race-risk review section in design notes.
