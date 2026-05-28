# v1.0.0 Release Snapshot Container

Purpose: version-lock all production release artifacts as a point-in-time snapshot for governance, auditability, and repeatability.

## Folder Contracts

- `code_snapshot/`
  - Production code snapshot only.
  - Exclude test framework internals and test suite implementation details.

- `documentation/`
  - Updated user manual (markdown)
  - Updated user manual (HTML)
  - Updated deployment guide
  - Release notes with deferred/missing functionality disclosures

- `governance/`
  - Final sign-off checklist and approval record
  - Software version descriptions and component version inventory
  - Accepted risk register and deferred-scope register (S13/S14 references)

- `evidence/`
  - Test evidence summaries (results only)
  - Validation decision records
  - Environment and command-class audit trail

## Required Release Principle

Publish evidence outcomes, not test framework internals.
