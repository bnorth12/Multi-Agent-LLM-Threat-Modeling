# Software Version Description (SVD): v1.0.0

Date: 2026-05-27
Status: Draft

## 1. Product Identification

- Product Name: Multi-Agent LLM Threat Modeler
- Version: v1.0.0 (release-candidate baseline package)
- Baseline commit reference: `5813ef4de2b506b2b8bcef3761d02065747ab88a`
- Release container: `Releases/v1.0.0`

## 2. Version Scope

This version captures the standalone GUI/backend baseline and governance packaging controls required for release candidate publication.

Included:
- Production runtime code snapshot
- User/deployment documentation set (to be finalized in `documentation/`)
- Governance records and sign-off controls
- Validation evidence summaries

Excluded from publication package:
- Test framework internals and test implementation details
- Developer-only harness internals not required for runtime operation

## 3. Configuration Items

Primary configuration-item groups:
- Runtime/backend code and service orchestration
- Frontend React HMI runtime artifacts
- Requirements and traceability governance artifacts
- Release governance and evidence package records

## 4. Validation Baseline

Current clean-room validation status:
- Python unit/integration: PASS
- Dependency boundary check: PASS
- Frontend lint/build: FAIL (existing lint/type issues pending remediation)

Release publication precondition:
- Frontend lint/build clean-room lane must pass after remediation.

## 5. Known Open Items and Accepted Risks

Accepted risk posture:
- #88 accepted provisionally as non-blocking for RC progression; remains open for full hardening closure.

Open carryover/deferred issue inventory at drafting time:
- #65, #67, #72, #73, #74, #75, #76, #77, #78, #81, #82, #83, #84, #85, #87, #88

## 6. Planned Follow-On Scope References

- Sprint 2026-13 planning: `planning/Sprint_2026_13_Skills_Layer_and_Avionics_Specialization.md`
- Sprint 2026-14 concept candidates: `planning/Sprint_2026_14_Concept_Review_Threat_Model_Abstractions_and_Compositional_Flows.md`

## 7. Approval and Control

This SVD becomes authoritative for v1.0.0 publication only after final sign-off checklist completion and release manager approval.
