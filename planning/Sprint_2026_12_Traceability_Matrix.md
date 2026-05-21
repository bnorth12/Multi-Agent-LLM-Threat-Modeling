# Sprint 2026-12 Traceability Matrix

**Sprint**: 2026-12
**Start Date**: 2026-05-19
**End Date**: 2026-05-19
**Status**: CLOSED (Execution complete; final sign-off pending)

---

## Overview

This matrix records requirement-to-implementation-to-test traceability for Sprint 2026-12 web interface and operational API enablement.

**Completion Target**: 100%
**Current Status**: 15/15 requirements implemented and verified (1 item deferred by approved decision record)

---

## Traceability Matrix

| # | Requirement ID | Requirement Name | Issue ID | Issue Status | Assigned To | Test File | Verification Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | S12-REQ-001 | Expose backend operational endpoints (REST-first) | S12-EXEC-001 | Completed | Copilot | Tests/unit/test_operational_api_server.py | ✅ PASS | /config, /prompts, /runs, artifact routes, DELETE /runs/{run_id} |
| 2 | S12-REQ-002 | Publish API contract for frontend integration | S12-EXEC-002 | Completed | Copilot | docs/schemas/Operational_API_Contract_Sprint_2026_12.md | ✅ PASS | Contract includes error semantics and auth behavior |
| 3 | S12-REQ-003 | Standalone React + MUI shell with frame layout | S12-EXEC-003 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py | ✅ PASS | Top/left/main/footer frames validated |
| 4 | S12-REQ-004 | Frontend wiring for runs/config/prompts/artifacts | S12-EXEC-004 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py | ✅ PASS | API client integration and page flows validated |
| 5 | S12-REQ-005 | HITL controls in page and footer pathways | S12-EXEC-005 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py | ✅ PASS | Resume/cancel controls present and actionable |
| 6 | S12-REQ-006 | Auth gate support with bearer handling (staged) | S12-EXEC-006 | Completed | Copilot | Tests/unit/test_operational_api_server.py | ✅ PASS | Includes missing-token, malformed-header, and matching-token coverage |
| 7 | S12-REQ-007 | Browser unauthorized UI guidance | S12-EXEC-007 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py | ✅ PASS | Opt-in auth UI lane passes |
| 8 | S12-REQ-008 | Dependency separation hardening | S12-EXEC-008 | Completed | Copilot | scripts/verify_dependency_boundary.py | ✅ PASS | Runtime manifests exclude test-only packages |
| 9 | S12-REQ-009 | Explicit browser test lanes (shell/full) | S12-EXEC-009 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py; Tests/e2e/test_frontend_react_mui_full_workflow.py | ✅ PASS | Shell lane active and full workflow lane implemented with passing evidence |
| 10 | S12-REQ-010 | Runtime integration hardening for split hosting | S12-EXEC-010 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_shell.py | ✅ PASS | CORS/OPTIONS support and dynamic test port allocation |
| 11 | S12-REQ-011 | Ordered HITL Gate ledger and lifecycle summary | S12-EXEC-011 | Completed | Copilot | frontend/src/components/HITLGateManager.test.tsx | ✅ PASS | All gates shown in pipeline order with Approved/Rejected/Bypassed/Pending summary counts |
| 12 | S12-REQ-012 | Persistent footer status and gate-page monitoring continuity | S12-EXEC-012 | Completed | Copilot | frontend/src/components/HITLGateManager.test.tsx; Tests/test_hmi_backend_api.py | ✅ PASS | Run may be monitored from HITL Gate page; centered footer status text added and resume no longer forces execution tab |
| 13 | S12-REQ-013 | Enforced Gate 0 preflight review with human-readable input summaries | S12-EXEC-013 | Completed | Copilot | Tests/integration/test_avionics_expected_results.py | ✅ PASS | Gate 0 now pauses before Stage 1 and renders preflight intent/integrity checks for approval/rejection |
| 14 | S12-REQ-014 | Mandatory post-Stage-1 normalization review gate before Stage 2 | S12-EXEC-014 | Completed | Copilot | Tests/integration/test_avionics_expected_results.py; frontend/src/components/HITLGateManager.test.tsx | ✅ PASS | New normalization review gate blocks Stage 2 until analyst decision; timeline markers include before/after stage gate positions |
| 15 | S12-REQ-015 | Mermaid artifact reviewer with multi-diagram navigation and split view modes | S12-EXEC-015 | Completed | Copilot | Tests/e2e/test_frontend_react_mui_full_workflow.py; scripts/live_browser_e2e_smoke_react.py | ✅ PASS | Artifacts viewer supports parsed diagram selection, editable source, rendered preview, and `x of n - diagram name` navigator label |

---

## Deferred (Approved)

| Requirement ID | Deferred Item | Rationale | Target Sprint |
|---|---|---|---|
| S12-DEF-001 | GraphQL endpoint implementation | Approved REST-first approach for Sprint 12 | 2026-13 |

---

## Verification Evidence

- Unit/API: `python -m pytest Tests/unit/test_operational_api_server.py -q` -> `9 passed`
- Frontend quality: `npm run lint` and `npm run build` in `frontend/` -> both passed
- Focused frontend behavior: `npm run test -- --run src/components/HITLGateManager.test.tsx` in `frontend/` -> `5 passed`
- Gate enforcement flow: `PYTHONPATH=src python -m pytest Tests/integration/test_avionics_expected_results.py -q` -> `2 passed`
- Artifact reviewer flow: `PYTHONPATH=src .venv\Scripts\python.exe scripts/live_browser_e2e_smoke_react.py` -> `LIVE_BROWSER_SMOKE_OK` with frontend artifact loading and navigation evidence
- Dependency boundary: `python scripts/verify_dependency_boundary.py` -> `DEPENDENCY_BOUNDARY_CHECK_PASSED`
- Browser shell lane: `pytest Tests/e2e/test_frontend_react_mui_shell.py -q -m "llm_live_browser and frontend_shell"` -> `1 passed, 1 skipped`
- Browser auth UI lane: `pytest Tests/e2e/test_frontend_react_mui_shell.py -q -k unauthorized -m "llm_live_browser and frontend_shell"` -> `1 passed, 1 deselected`
- Browser full workflow lane: `pytest Tests/e2e/test_frontend_react_mui_full_workflow.py -q -m "llm_live_browser and frontend_full"` with `FRONTEND_FULL_BROWSER_TESTS=1` -> `1 passed`

---

## Sign-Off

### Technical Lead

**Name**: ________________
**Date**: ________________

- [x] Traceability matrix complete
- [x] Test evidence captured
- [x] Deferred items documented
- [ ] Final approval granted

### Product / Program

**Name**: ________________
**Date**: ________________

- [ ] Sprint closure accepted
- [ ] Carryovers accepted for 2026-13
