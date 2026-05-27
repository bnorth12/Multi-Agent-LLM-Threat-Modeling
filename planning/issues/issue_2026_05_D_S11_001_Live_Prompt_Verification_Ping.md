# D-S11-001: Connection Verify Must Perform Live Prompt Ping

## Issue Summary

Pipeline Configuration "Verify LLM Connection" must prove real provider connectivity and authentication by executing a live prompt ping, not only structural input checks.

## Related Requirements

- RHMI-009
- GUI-014
- GUI-013

## Problem Statement

Structural validation can report a false positive when the endpoint is reachable but credentials are invalid, model routing is misconfigured, or provider responses are empty. This causes immediate run failures after a successful verify step and degrades operator trust.

## Required Behavior

1. Verify SHALL perform a real prompt round-trip through the configured provider path.
2. Verify SHALL use run-scoped key material from runtime settings (`model.api_key`) and SHALL NOT rely on process environment secrets.
3. Verify SHALL fail with a clear message on auth failure, transport failure, timeout, provider error, or empty provider response.
4. Verify SHALL pass only when provider responds successfully with non-empty output.

## Scope

1. Backend `/config/verify` uses runtime settings and runs a minimal prompt ping request.
2. Frontend verification payload includes `model.api_key` in runtime settings.
3. Runtime settings and API responses redact `model.api_key` from persisted/returned metadata.
4. Streamlit and React verification semantics remain aligned.

## Acceptance Criteria

- [ ] Invalid key returns verify failure with explicit provider/auth message.
- [ ] Valid key and reachable endpoint return verify success.
- [ ] Unreachable endpoint returns verify failure with transport/timeout message.
- [ ] Empty provider response returns verify failure.
- [ ] Run creation is blocked in UI unless verify succeeded or explicit offline override is selected.
- [ ] Automated tests cover success and representative failure paths.

## Verification Plan

- Backend API tests: `/config/verify` success and failure paths with mocked provider responses.
- UI functional test: verify gate before applying live settings.
- Live smoke evidence: one successful verify + run start sequence.

## Status

Planned

## Notes

- This issue supersedes the deferred gap documented in `issue_2026_09_D_S09_013_API_Connection_Validation_Allows_Invalid_Key.md` with current sprint implementation scope and acceptance language.
