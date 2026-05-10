# Issue: EDR-06 — Idempotent Handlers and Retry Safety

**Issue ID**: EDR-06-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: High

## Overview

Make event handlers and artifact writers idempotent so retry/replay paths do not produce duplicate outputs or inconsistent gate state.

## Scope

1. Define idempotency keys for artifact and gate side effects.
2. Implement dedupe guards for repeated event delivery.
3. Add safe retry semantics for transient failures.
4. Validate behavior under at-least-once delivery assumptions.

## Acceptance Criteria

1. Duplicate `artifact_generated` events do not create duplicate artifacts.
2. Replayed `gate_opened` and `gate_resolved` events converge to correct latest state.
3. Retry logic avoids data corruption and preserves traceability.
4. Integration tests cover duplicate and out-of-order event scenarios.

## Out of Scope

1. Exactly-once distributed guarantees.
2. External ledger or immutable audit platform integration.

## Dependencies

1. [issue_2026_09_EDR_04_Event_Log_And_Bus.md](issue_2026_09_EDR_04_Event_Log_And_Bus.md)
