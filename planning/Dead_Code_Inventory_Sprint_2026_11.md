# Dead Code Inventory Sprint 2026-11

Date: 2026-05-14
Status: Draft for implementation
Purpose: Record dead and unreachable code candidates after LangGraph migration, with explicit remove/deprecate decisions and rationale.

## 1. Decision Categories

- Remove: No production dependency and no governance need to retain.
- Deprecate: Still used for compatibility/testing; remove only after replacement criteria are met.
- Retain: Active production behavior.

## 2. Inventory and Decisions

| ID | File | Symbol or Area | Current Evidence | Decision | Rationale | Exit Criteria |
|---|---|---|---|---|---|---|
| DCI-001 | src/threat_modeler/orchestrator.py | StateGraph compatibility wrapper class | Referenced by Tests/unit/test_orchestrator.py only; production path uses FrameworkOrchestrator run_planned_stages | Deprecate | Wrapper still anchors legacy tests; immediate removal would invalidate current unit coverage before replacement tests land | Replace legacy tests with FrameworkOrchestrator LangGraph-native tests, then remove wrapper |
| DCI-002 | src/threat_modeler/orchestrator.py | build_default_state_graph | Referenced by Tests/unit/test_orchestrator.py only | Deprecate | Same compatibility test dependency as DCI-001 | Remove after test migration and traceability update |
| DCI-003 | src/threat_modeler/orchestrator.py | agent_01_input_normalizer stub | Used only by compatibility graph builder | Remove | Stub does not represent production agent execution and provides no runtime governance value | Remove with DCI-001 and DCI-002 cleanup PR |
| DCI-004 | src/threat_modeler/orchestrator.py | agent_02_context_builder stub | Used only by compatibility graph builder | Remove | Stub does not represent production agent execution and provides no runtime governance value | Remove with DCI-001 and DCI-002 cleanup PR |
| DCI-005 | src/threat_modeler/orchestrator.py | linear branch in run_planned_stages | Reachable when execution_mode is linear; config default currently linear | Deprecate | Branch remains operational compatibility mode; not dead but migration-targeted for governance hardening | Keep until execution mode governance decision finalizes default path and release profile enforcement |

## 3. Additional Drift Items (Documentation/Traceability)

These are not dead code, but they create unreachable or misleading governance references and must be corrected in parallel:

| ID | File | Issue | Decision |
|---|---|---|---|
| DCI-DOC-001 | Requirements/HITL-012-014_Conditional_Gate_State_Reporting.md | Stale path reference to src/threat_modeler/orchestration/orchestrator.py | Remove stale path; point to src/threat_modeler/orchestrator.py |
| DCI-DOC-002 | Tests/unit/test_orchestrator.py | File scope currently validates compatibility wrapper only | Deprecate current scope; replace with LangGraph-native unit coverage |

## 4. Planned Removal and Deprecation Sequence

1. Land new LangGraph-native orchestrator unit tests and delegation integration tests.
1. Mark compatibility APIs as deprecated in orchestrator module notes.
1. Remove compatibility stubs and legacy graph builder.
1. Remove compatibility wrapper class after coverage parity and traceability update.
1. Close DCI items with evidence in sprint execution summary.

## 5. Required Evidence for Closure

- Test evidence showing replacement coverage before compatibility removals.
- Traceability matrix update removing legacy-only references.
- Changelog/release notes entry documenting deprecation and removals.
- No regression in unit, integration, and CI-safe e2e lane.
