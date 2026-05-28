# Publication Content Policy (v1.0.0)

## 1. Allowed in Published Release Bundle

- Production runtime code snapshot
- User-facing product documentation
- Deployment documentation
- Governance and sign-off artifacts
- Test evidence summaries (counts, status, dates, environments)
- Risk acceptance and deferred scope disclosures

## 2. Not Allowed in Published Release Bundle

- Test framework implementation files
- Detailed test scripts/spec internals
- CI helper internals not needed for runtime operation
- Developer-only harness assets not required by end users/operators

## 3. Evidence Reporting Standard

For each executed validation lane, report:

- lane name
- date/time
- environment
- command class (not full internal implementation)
- result summary (pass/fail/skipped counts)
- link/reference to governance decision record

## 4. Deferred Scope Disclosure Standard

Release notes must include:

- deferred functionality planned for Sprint 2026-13
- deferred functionality planned for Sprint 2026-14
- accepted residual risks still open at publication time
- issue IDs and owner/target sprint for each deferred item
