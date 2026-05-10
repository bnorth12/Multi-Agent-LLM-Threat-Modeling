# Issue: EDR-04 — Append-Only Event Log and Bus Abstraction

**Issue ID**: EDR-04-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: High

## Overview

Implement an append-only event store with a bus abstraction so producers and consumers can evolve without tight coupling.

## Scope

1. Create durable append-only event writer.
2. Add ordered event read APIs by `run_id` and sequence.
3. Define bus abstraction for publish/subscribe or poll semantics.
4. Support replay for diagnostics and recovery.

## Acceptance Criteria

1. Events are durably written before downstream side effects are committed.
2. Consumers can read all events for one `run_id` in deterministic order.
3. Event replay can reconstruct run timeline end-to-end.
4. Storage adapter is swappable without changing event producers.

## Out of Scope

1. Final cloud message bus selection.
2. Long-term data retention policy automation.

## Dependencies

1. [issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md](issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md)
