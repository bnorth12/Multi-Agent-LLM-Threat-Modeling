# Issue: EDR-01 — Event Envelope and Identifier Contract

**Issue ID**: EDR-01-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: High

## Overview

Define and implement the canonical event envelope and identifier propagation rules used by all run events.

## Scope

1. Create typed schema for event envelope.
1. Define required vs optional fields and validation rules.
1. Implement helper utilities for ID generation and propagation.
1. Add schema validation tests.

## Required Envelope Fields

1. `event_id`
1. `event_type`
1. `event_version`
1. `occurred_at_utc`
1. `session_id`
1. `run_id`
1. `stage_id`
1. `llm_request_id`
1. `correlation_id`
1. `gate_id`
1. `artifact_id`
1. `payload`

## Acceptance Criteria

1. Event schema is documented and validated at runtime boundaries.
1. Every emitted event includes `run_id` and `correlation_id`.
1. Schema rejects malformed identifiers and missing required fields.
1. Contract examples exist for each event type in epic baseline.

## Out of Scope

1. Worker queue implementation.
1. UI rendering changes.

## Dependencies

1. [issue_2026_09_Event_Driven_Run_Tracking_Epic.md](issue_2026_09_Event_Driven_Run_Tracking_Epic.md)
