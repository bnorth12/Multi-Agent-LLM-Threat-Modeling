# Issue: EDR-05 — UI Run Event Stream and Read Model

**Issue ID**: EDR-05-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: Medium

## Overview

Build a UI poll/stream layer that reads run events by `run_id` and renders coherent progress, gate state, and artifact availability without volatile-only session coupling.

## Scope

1. Add run timeline query endpoint or adapter by `run_id`.
2. Implement UI read model projection from event stream.
3. Display latest stage, gate status, and artifact events.
4. Support reload recovery using query/session run locator.

## Acceptance Criteria

1. Reloading the browser preserves run visibility when `run_id` is known.
2. Sidebar and main-content status remain synchronized from same read model source.
3. Threat Review and Stage Results derive from emitted events and latest snapshot.
4. UI can render `run_failed` payload details without direct thread-state dependency.

## Out of Scope

1. Full redesign of existing screen layouts.
2. Historical analytics dashboards.

## Dependencies

1. [issue_2026_09_EDR_03_Execution_Worker_Queue.md](issue_2026_09_EDR_03_Execution_Worker_Queue.md)
2. [issue_2026_09_EDR_04_Event_Log_And_Bus.md](issue_2026_09_EDR_04_Event_Log_And_Bus.md)
