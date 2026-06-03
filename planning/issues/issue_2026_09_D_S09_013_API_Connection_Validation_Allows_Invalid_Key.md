# D-S09-013: API Connection Validation Accepts Invalid API Keys

## Issue Summary

During manual UI validation, the Pipeline Configuration connection validation accepted an intentionally invalid API key. This indicates the "Validate Connection" flow is not performing a real provider-authenticated request and is therefore not proving endpoint/auth validity.

## Related Requirements

- GUI-014
- GUI-013

## Severity

High - false-positive validation allows misconfigured credentials to proceed into execution, causing avoidable run-time failures.

## Reproduction

1. Open `Pipeline Configuration` screen.
1. Select a live provider (xAI/Grok).
1. Enter an invalid API key value.
1. Click `Validate Connection`.
1. Observe validation result incorrectly indicates success.

## Expected Behavior

`Validate Connection` SHALL execute a real provider request using the configured endpoint, model, and API key.

- If authentication fails (401/403 or equivalent), validation SHALL return failure.
- If endpoint is unreachable/invalid, validation SHALL return failure.
- Validation SHALL only return success on a positive authenticated response.

## Scope

1. Implement an active provider ping/test request in connection validation path.
1. Require provider-authenticated response for success.
1. Return clear user-readable failure causes (invalid key, unreachable endpoint, timeout, provider error).
1. Add automated test coverage for invalid-key failure path and valid-key success path.

## Acceptance Criteria

- [ ] Invalid API key fails validation with explicit auth error message.
- [ ] Reachable endpoint + valid key passes validation.
- [ ] Unreachable endpoint fails validation with transport error message.
- [ ] GUI blocks run initiation when connection validation fails (unless explicit offline override is used).
- [ ] Automated tests cover both success and failure paths.

## Status

Deferred

## Deferral Rationale (2026-05-10)

- Manual smoke run uncovered this during RC flow.
- Current sprint priority remains completion of pending manual RC campaign and stabilization items already in-flight.
- Issue is documented and queued for next implementation slice before final release sign-off.
