# Issue: EDR-03 — Queue-Based Execution Worker

**Issue ID**: EDR-03-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: High

## Overview

Introduce worker-queue execution so run processing is detached from Streamlit UI process lifecycle.

## Scope

1. Add run submission API that enqueues a `run_id` job.
2. Implement worker loop that executes staged orchestration for queued jobs.
3. Emit run lifecycle events (`stage_completed`, `run_completed`, `run_failed`).
4. Persist worker heartbeat and run status snapshots for operations visibility.

## Acceptance Criteria

1. UI start action enqueues run and returns immediately.
2. Worker picks up and executes job independently of UI reruns.
3. Run status remains available when browser reloads.
4. Failure events include structured error payload and stage context.

## Out of Scope

1. Production external queue platform migration.
2. Multi-region worker distribution.

## Dependencies

1. [issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md](issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md)
2. [issue_2026_09_EDR_04_Event_Log_And_Bus.md](issue_2026_09_EDR_04_Event_Log_And_Bus.md)
