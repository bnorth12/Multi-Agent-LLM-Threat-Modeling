# Epic: Event-Driven Run Tracking and Orchestration Backbone

**Epic ID**: EPC-2026-09-EDR-001
**Target Sprint**: Future Sprint Candidate (2026-09 or later)
**Status**: BACKLOG
**Created**: 2026-05-07
**Owner Role**: Technical Lead and Platform Engineer

## Overview

Implement a production-style, event-driven execution backbone so UI sessions can reliably track long-running LLM workflows, HITL gates, and generated artifacts across reloads, retries, and worker restarts.

This epic formalizes:

- Stable tracking identifiers (`session_id`, `run_id`, `stage_id`, `llm_request_id`, `correlation_id`, `gate_id`, `artifact_id`)
- Standard lifecycle events for LLM calls, stage transitions, gates, artifacts, and run outcomes
- Queue-based worker execution and append-only event log
- UI poll/stream read model keyed by `run_id`
- Idempotent handlers to prevent duplicate artifact side effects

## Goals

1. Decouple run execution from the Streamlit request lifecycle.
1. Make run progress and gate state resilient to browser reloads.
1. Provide full causal traceability of every LLM submission and response.
1. Enable safe retry/replay behavior without duplicate artifacts.
1. Establish a clear platform for future scaling and ops visibility.

## Non-Goals

1. Replacing current HITL decision semantics.
1. Reworking domain logic for STRIDE/threat generation.
1. Introducing multi-tenant auth redesign in this epic.

## Child Issues

1. [issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md](issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md)
1. [issue_2026_09_EDR_02_LLM_Call_Event_Instrumentation.md](issue_2026_09_EDR_02_LLM_Call_Event_Instrumentation.md)
1. [issue_2026_09_EDR_03_Execution_Worker_Queue.md](issue_2026_09_EDR_03_Execution_Worker_Queue.md)
1. [issue_2026_09_EDR_04_Event_Log_And_Bus.md](issue_2026_09_EDR_04_Event_Log_And_Bus.md)
1. [issue_2026_09_EDR_05_UI_Run_Event_Stream.md](issue_2026_09_EDR_05_UI_Run_Event_Stream.md)
1. [issue_2026_09_EDR_06_Idempotency_And_Retry_Safety.md](issue_2026_09_EDR_06_Idempotency_And_Retry_Safety.md)
1. [issue_2026_09_EDR_07_E2E_Validation_And_Rollout.md](issue_2026_09_EDR_07_E2E_Validation_And_Rollout.md)

## Event Model Baseline

1. `llm_submitted`
1. `llm_response_received`
1. `artifact_generated`
1. `gate_opened`
1. `gate_resolved`
1. `stage_completed`
1. `run_completed`
1. `run_failed`

## Required Tracking Keys

1. `session_id`
1. `run_id`
1. `stage_id`
1. `llm_request_id`
1. `correlation_id`
1. `gate_id`
1. `artifact_id`

## Dependencies

1. Existing orchestrator and HITL gate checkpoint behavior remain available as integration points.
1. Runtime settings must support selecting an execution backend mode (in-process vs queue worker).
1. Storage location for append-only events must be chosen (local durable file/DB initially, external bus later).

## Exit Criteria

1. Full 9-stage run can be started from UI and observed after browser reload using only `run_id`.
1. Each LLM call has both submit and response events with shared `llm_request_id` and `correlation_id`.
1. Gate transitions are represented as events and recoverable after restart.
1. Artifact writes are idempotent under retry/replay tests.
1. UI displays coherent per-run progress from event stream without relying on volatile session-only state.
