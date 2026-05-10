# Issue: EDR-02 — LLM Call Event Instrumentation

**Issue ID**: EDR-02-2026-09
**Epic**: EPC-2026-09-EDR-001
**Status**: BACKLOG
**Created**: 2026-05-07
**Priority**: High

## Overview

Instrument all LLM invocations so each call emits matched submit and response events with durable correlation metadata.

## Scope

1. Emit `llm_submitted` before outbound provider call.
2. Emit `llm_response_received` after provider response or timeout/failure classification.
3. Attach `llm_request_id`, `run_id`, `stage_id`, and `correlation_id` consistently.
4. Capture provider metadata and timing fields in payload.

## Acceptance Criteria

1. For each outbound LLM request, exactly one `llm_submitted` event is emitted.
2. For each completion path, a corresponding `llm_response_received` event is emitted.
3. Submit and response events share `llm_request_id` and `correlation_id`.
4. Timeout and provider error paths still emit response event with structured error payload.

## Out of Scope

1. UI event stream read model.
2. Queue worker orchestration.

## Dependencies

1. [issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md](issue_2026_09_EDR_01_Event_Envelope_And_Identifiers.md)
