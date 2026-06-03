# Partial 15 Full-Chain Remediation Plan

Generated: 2026-06-02
Source baseline: planning/analysis/reachable_traceability_comparison.md

## Scope

This plan prioritizes remediation for the 15 reachable modules that remain partial against six trace domains:

- requirements
- capabilities
- functions
- architecture
- design
- verification

Current post-backfill baseline for these 15 modules:

- full modules in reachable set: 24/39
- partial modules in reachable set: 15/39
- unmatched modules: 0/39

## Prioritization Method

Priority order is based on:

1. Gap depth: number of missing domains per module
1. Runtime criticality: entrypoint, orchestration/state, API boundary, execution coordination
1. Reuse impact: module supports multiple UI flows or multiple downstream artifacts
1. Overlap potential: existing single relationship can be expanded to multiple requirement/design/verification links

## Prioritized Remediation List

| Priority | Code Module | Existing Domains | Missing Domains | Why Priority Is High | Recommended Next Relationships |
|---|---|---|---|---|---|
| P1 | src/threat_modeler/ui/app.py | architecture, verification | requirements, capabilities, functions, design | Primary UI entrypoint; influences all screen-level behavior and state routing | Add requirement anchors for shell/navigation/runtime-state continuity; add capability/function linkage to UI control-surface functions; add design anchor to runtime orchestration and HMI design package |
| P1 | src/threat_modeler/ui/execution.py | architecture, verification | requirements, capabilities, functions, design | Execution lifecycle adapter for start/resume/cancel/status and gate projections | Add requirement anchors for execution continuity and paused-state behavior; add capability/function mapping to UI traceability and RHMI execution functions; add design anchor to runtime orchestration design |
| P1 | src/threat_modeler/state.py | architecture, capabilities, functions | requirements, design, verification | Shared framework state model; consumed across orchestrator and API projections | Add requirement anchors for state continuity and telemetry recording; add design anchor to state and orchestration spec; add verification anchor to orchestrator/framework unit tests |
| P1 | src/threat_modeler/server/hmi_data.py | architecture, capabilities, functions | requirements, design, verification | Backend-to-HMI payload shaping boundary; affects what operators review | Add requirement anchors for threat/gate serialization and metrics extraction; add design anchor to external interface/integration design; add verification artifacts from HMI API and integration tests |
| P1 | src/threat_modeler/backend/runtime_state.py | architecture, capabilities, functions, verification | requirements, design | Persistent runtime metadata and settings continuity boundary | Add requirement anchors for restart-safe run continuity and provider state persistence; add design anchor to runtime/orchestration design package |
| P2 | src/threat_modeler/models/canonical.py | requirements, architecture, capabilities, functions | design, verification | Canonical model schema is foundational to multiple agents/exports | Add design anchor to canonical model transformation package; add verification links to canonical graph viewer and pipeline completeness tests |
| P2 | src/threat_modeler/backend/prompt_store.py | requirements, architecture, design, capabilities, functions | verification | Prompt persistence impacts deterministic stage prompting | Add verification anchors to prompt baseline and prompt edit-to-execution tests |
| P2 | src/threat_modeler/ui/prompt_store.py | requirements, architecture, capabilities, functions, verification | design | UI prompt persistence bridge should share design authority with backend prompt store | Add design anchor to agent subsystem design specification and prompt lifecycle design section |
| P2 | src/threat_modeler/validation.py | requirements, architecture, design, capabilities, functions | verification | Core validation logic governs acceptance and gate opening | Add verification anchors to validation gates integration tests and any direct unit validation coverage |
| P2 | src/threat_modeler/hitl/models.py | architecture, capabilities, functions | requirements, design, verification | HITL decision record schema supports gate lifecycle and audit log | Add requirement anchors for gate decision persistence and audit trace; add design anchor to HITL runtime spec; add verification anchors to HITL gate integration tests |
| P2 | src/threat_modeler/llm/llm_provider_error.py | architecture, capabilities, functions | requirements, design, verification | Error contract controls provider failure semantics and retry outcomes | Add requirement anchors for LLM error handling behavior; add design anchor to provider boundary spec; add verification to live/provider unit tests |
| P3 | src/threat_modeler/__main__.py | architecture, capabilities, functions | requirements, design, verification | Thin runtime entrypoint but governance-critical for launch contract | Add requirement/design/verification anchors for startup contract and API server launch behavior |
| P3 | src/threat_modeler/agents/deserialise.py | architecture, capabilities, functions | requirements, design, verification | Data reconstruction helper; lower direct user-surface impact | Add requirement anchors for canonical reconstruction integrity; add design anchor to data transformation flow; add verification to parser/canonical tests |
| P3 | src/threat_modeler/ui/debug.py | architecture, capabilities, functions | requirements, design, verification | Diagnostic utility surface; useful but lower release-criticality | Add requirement anchors for diagnostics visibility policy; add design/verification references to HMI diagnostics behavior |
| P3 | src/threat_modeler/ui/theme.py | architecture, capabilities, functions, verification | requirements, design | Presentation-level module with narrower risk footprint | Add requirement anchors for operator display continuity/theming; add design anchor to UI presentation design notes |

## Overlap Expansion Analysis

This section captures where at least one relationship already exists and additional relationships should be attached to the same module for multi-link parity.

### A. Requirement Overlap Expansion Candidates

| Code Module | Existing Relationship Present | Additional Requirement Relationships Recommended | Rationale |
|---|---|---|---|
| src/threat_modeler/ui/app.py | architecture, verification | SCR-002, SCR-003, SCR-004, SCR-007, SCR-008, SCR-014 | Entrypoint orchestrates navigation and execution views already mapped in downstream screens |
| src/threat_modeler/ui/execution.py | architecture, verification | RHMI-016, GUI-031, GUI-032, SCR-007, SCR-014 | Execution state sync and gate/status projection overlap with existing run-manager and HITL requirement families |
| src/threat_modeler/state.py | architecture, capabilities, functions | ORCH-001, INT-005, SCR-014, RHMI-016 | Framework state holds continuity, telemetry, and prompt/run traces |
| src/threat_modeler/server/hmi_data.py | architecture, capabilities, functions | SCR-004, GUI-032, RHMI-005, RHMI-016 | Threat and gate payload serialization maps to existing HMI and HITL behavior requirements |
| src/threat_modeler/backend/runtime_state.py | architecture, capabilities, functions, verification | RHMI-016, SCR-007, SCR-014 | Runtime state persistence overlaps restart-safe retrieval and execution continuity behavior |

### B. Architecture / Function Overlap Expansion Candidates

| Code Module | Existing Relationship Present | Additional Architecture/Function Relationships Recommended | Rationale |
|---|---|---|---|
| src/threat_modeler/ui/app.py | architecture | Add explicit function-family link to F-UI-TRACEABILITY-L1 and L2 UI decomposition rows used by screen modules | Entrypoint currently implied via screen modules, not explicitly allocated |
| src/threat_modeler/ui/execution.py | architecture | Add explicit function-family link to execution continuity and paused-state projection rows | Module is central bridge for execution status and run-id URL/session coupling |
| src/threat_modeler/state.py | capabilities/functions | Add explicit architecture allocation row to state persistence and orchestration boundary | Architectural placement is implicit, should be explicit for state authority |
| src/threat_modeler/server/hmi_data.py | capabilities/functions | Add explicit architecture allocation row for API/HMI transformation boundary | Prevent ambiguity between API handler and HMI payload serializer responsibilities |

### C. Design Overlap Expansion Candidates

| Code Module | Existing Relationship Present | Additional Design Relationships Recommended | Rationale |
|---|---|---|---|
| src/threat_modeler/ui/prompt_store.py | requirements, verification | Add design linkage mirroring backend prompt store design authority | UI and backend prompt stores are paired components |
| src/threat_modeler/backend/runtime_state.py | verification | Add runtime state continuity design linkage | Persistence mechanics require design-level control descriptions |
| src/threat_modeler/models/canonical.py | requirements | Add canonical model design linkage and data-flow transformation mapping | Canonical schema is used across agents and exports |
| src/threat_modeler/state.py | capabilities/functions | Add state model design linkage under orchestration design package | Shared state assumptions should be design-controlled |

### D. Verification Overlap Expansion Candidates

| Code Module | Existing Relationship Present | Additional Verification Relationships Recommended | Rationale |
|---|---|---|---|
| src/threat_modeler/backend/prompt_store.py | requirements, design | Add prompt lifecycle verification artifacts already used by UI prompt editor paths | Ensures backend and UI prompt-store changes are co-verified |
| src/threat_modeler/validation.py | requirements, design | Add validation-gates verification artifact linkage | Validation logic should map directly to gate validation tests |
| src/threat_modeler/models/canonical.py | requirements | Add canonical graph and pipeline verification artifacts | Canonical model correctness should be test-anchored |
| src/threat_modeler/hitl/models.py | capabilities/functions | Add HITL gate set verification artifacts | Decision/audit model behavior should be coupled to HITL integration tests |
| src/threat_modeler/llm/llm_provider_error.py | capabilities/functions | Add provider adapter unit/live verification anchors | Error semantics should be validated where retries/timeouts are tested |

## Quantified Remediation Backlog for Partial 15

- P1 modules: 5
- P2 modules: 7
- P3 modules: 3

Estimated relationship additions to move partial 15 toward full-chain parity:

- Requirement relationships: 11 to 15 additions
- Architecture/function explicit allocations: 4 to 6 additions
- Design relationships: 8 to 10 additions
- Verification relationships: 9 to 12 additions

## Execution Sequence Recommendation

1. Close P1 modules first (ui/app, ui/execution, state, server/hmi_data, backend/runtime_state).
1. Close paired-store and canonical/validation modules (backend.prompt_store, ui.prompt_store, models.canonical, validation).
1. Close remaining contract/helper modules (hitl.models, llm_provider_error, agents.deserialise, ui.debug, ui.theme, __main__).
1. Re-run planning/analysis/reachable_traceability_comparison.md after each wave and recalculate full/partial counts.
