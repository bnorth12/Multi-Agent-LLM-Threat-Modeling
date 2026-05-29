# Release Notes: v1.0.0

Date: 2026-05-27
Status: Publication candidate package
Release Type: Release Candidate baseline package

## 1. Release Summary

v1.0.0 captures the post-Sprint-2026-12 standalone GUI/backend baseline, with governance-managed accepted risks and deferred scope explicitly documented.

This document is prepared for controlled release governance sign-off and publication approval.

## 2. Included in This Release Snapshot

- Production baseline from RC prep branch rooted at commit `5813ef4de2b506b2b8bcef3761d02065747ab88a`
- Updated release governance policy and evidence summaries under `Releases/v1.0.0`
- Clean-room validation evidence summary (results-focused)

## 3. Validation Evidence Summary (Publishable)

- Python unit/integration clean-room lane: PASS (`500 passed`)
- Dependency boundary validation: PASS (`DEPENDENCY_BOUNDARY_CHECK_PASSED`)
- Frontend lint/build clean-room lane: PASS (lint warnings only, build successful)

Important publication rule:

- Evidence results are publishable.
- Test framework implementation internals are not publishable.

## 4. Accepted Risks and Non-Blocking Residuals

- #88 (Sprint 2026-13 D-S13-022): provisionally accepted as non-blocking for RC progression; remains open for full hardening closure.

## 5. Deferred and Missing Functionality Disclosure

All entries in this section are release-time statements as of 2026-05-27.
They are historical release-governance context, not a live status board.

### 5.1 Open Deferred/Carryover Issues (Current)

- #65, #67, #72, #73, #74, #75, #76, #77, #78, #81, #82, #83, #84, #85, #87, #88

### 5.2 Sprint 2026-13 Planned Scope References

Reference planning source:

- Sprint 2026-13 skills-layer and avionics-specialization planning record (governance archive)

Key S13 planning themes:

- Skills layer architecture and registry
- Risk-analysis modular skills
- Avionics and domain-boundary specialization skills
- Governance-controlled migration from hardcoded logic to skill interfaces

### 5.3 Sprint 2026-14 Concept Candidates

Reference planning source:

- Sprint 2026-14 concept review planning record for threat-model abstractions and compositional flows (governance archive)

Documented concept candidates:

- S14-001 through S14-009 (SoS hierarchy, compositional flows, abstraction tagging, OSI/link semantics, threat propagation, hierarchical visualization, cross-layer trust boundaries, protocol-wrapper anchoring, RAG bootstrap)

## 6. Packaging and Documentation Governance

v1.0.0 package structure (version-locked):

- `Releases/v1.0.0/code_snapshot`
- `Releases/v1.0.0/documentation`

Required for publication:

- Updated user manual (markdown)
- Updated user manual (HTML)
- Updated deployment guide
- Updated release notes
- Release decision record

## 7. Publish Gate Status

Current recommendation: GO

Remaining actions before publication:

- Complete final human approvals and signatures in the governance checklist.
