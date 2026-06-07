# Prompt Requirements Baseline

Date: 2026-05-22
Status: Active Baseline v1.0
Owner: Prompt Governance and Verification

## Purpose

Define minimum prompt-governance requirements that preserve behavioral specificity while allowing prompt structure and phrasing to evolve with model interfaces over time.

## Scope

- Runtime default prompts in backend prompt store
- Runtime default prompts in UI prompt store
- Expected output artifacts paired with each prompt
- Prompt contract and governance tests

## Baseline Requirements

### SHALL Requirements (Enforced by Tests)

| ID | Requirement Text | Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|
| PRM-001 | Each agent default record SHALL provide prompt text and expected_output as separate fields. | Keeps behavior instructions decoupled from format exemplars. | Automated unit test | Prompt store records expose distinct prompt and expected_output values for every agent. |
| PRM-002 | Backend and UI default prompt contracts SHALL remain synchronized for prompt and expected_output values for all agent IDs. | Prevents runtime/editor drift and inconsistent behavior across all execution contexts. | Automated unit test | Default prompt and expected_output values match for every agent ID across both stores. |
| PRM-003 | Structured prompt agents SHALL include minimum sections: Purpose, Inputs, Outputs, System Prompt, Rules. | Ensures minimum behavioral verbosity and operator-auditable scope. | Automated unit test | Required sections are present in agent prompts selected for structured baseline enforcement. |
| PRM-004 | Structured prompt agents SHALL maintain minimum prompt verbosity threshold (>= 400 characters). | Avoids under-specified prompts that degrade behavior determinism. | Automated unit test | Enforced prompt length threshold is met for structured agents. |
| PRM-005 | Canonical graph agents SHALL use expected_output payloads that include full top-level canonical shape with interfaces examples. | Protects schema continuity and prevents partial-shape regressions. | Automated unit test | Required top-level keys and interface examples are present in canonical expected_output payloads. |

### SHOULD Requirements (Reviewed for Maturity)

| ID | Requirement Text | Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|
| PRM-S01 | All agents SHOULD migrate to the structured section format over time. | Consistent authoring model improves maintainability and review quality. | Governance review | Non-structured prompts are tracked and prioritized for migration. |
| PRM-S02 | Prompt text SHOULD remain separate from large one-shot examples and output schema blocks. | Reduces prompt bloat and lowers change-coupling between behavior and examples. | Governance review | Examples and schemas are externalized where feasible; exceptions are documented. |
| PRM-S03 | Agents SHOULD include explicit ambiguity handling and failure-handling guidance. | Improves resilience under partial or low-confidence model outputs. | Governance review | Prompt guidance includes conservative fallback behavior. |
| PRM-S04 | Prompt changes SHOULD include impact notes and verification evidence before merge. | Supports safe evolution and audit traceability. | Change review | Prompt PRs include rationale, risk notes, and test evidence. |

## Structured Baseline Agent Set

- agent_01
- agent_02
- agent_03
- agent_04
- agent_05
- agent_06
- agent_07
- agent_08
- agent_09

## Traceability to Verification

- Tests/unit/test_prompt_requirements_baseline.py
- Tests/unit/test_agent_prompt_contracts.py

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- Prompt requirements (PRM-*, SCR-010/011, PRJ-018, PRJ-030) derived from C13-UI-001 (prompt response correlation, prompt editor surfaces) and C01-ORCH-001 / C16-PRJ-001 (prompt configuration management within governance and runtime integrity) plus C18-ADM for auditability of prompt changes
- Strong linkage to F-UI-TRACEABILITY-L1 and F-PRJ-TRACEABILITY-L1 / prompt configuration L3 functions (F330/F331/F332)

### Allocated To

- Prompt baseline and versioned edit/revert/audit requirements allocated to C13-UI-001 and the prompt editor + version history UI surfaces, plus backend prompt store authority (Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md)

### Refines

- PRJ-018 (Agent Prompt Configurability) and PRJ-030 (Prompt Store Authority and Fail-Closed Loading) from 01_Project_Requirements.md are elaborated here with version history, GUI edit/revert, and authoritative backend loading rules
- SCR-010/011 (prompt temperature and related) refine the prompt store for governance-controlled tuning

### Satisfied By

- Prompt store structure, version retention, authoritative backend loading (no silent file fallback), GUI edit/save/revert with history, and recovery of prompt state satisfied by src/threat_modeler/backend/prompt_store.py, src/threat_modeler/ui/screens/prompt_editor.py, frontend prompt-related components, and Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md
- 15_End_To_End and S13-005* rows (GUI-010 prompt version history, GUI-017 live-to-fixture, RIC prompt-related state) cite the prompt store + editor + Runtime_And_Orchestration design as the anchors
- Cross-ref to Agent_Subsystem_Design_Specification.md (agents consume versioned prompts from the authoritative store)

### Verified By

- Prompt edit/version/revert tests in UI shell and integration suites (Tests/unit/test_ui_app_shell.py, Tests/test_hmi_backend_api.py, Tests/integration/test_results_export_quick_preview.py)
- FQT-009 (prompt edit, save, version history, revert)
- Governance audit and independent review checks for prompt provenance in evidence packages (PRJ-007/021, C18-ADM)
- 15_End_To_End verification artifacts for prompt-related rows

### Depends On

- 01_Project_Requirements.md (PRJ-018, PRJ-007, PRJ-021, PRJ-030), 10_GUI_Requirements.md (GUI prompt surfaces), 13_Runtime_State (state + prompt persistence linkage)
- Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md (primary design authority) and Runtime_And_Orchestration_Design_Specification.md
- Agent_Subsystem_Design_Specification.md (consumption of versioned prompts)
- 15_End_To_End_Traceability_Attributes_Registry.md (prompt legs)
- 05_Verification_Strategy.md and FQT for demonstration of prompt configurability and auditability
- 18_Traceability_Governance_Operating_Model.md (prompt requirements illustrate "Implementation" from design to requirement and "Evidence production" for version history in release artifacts)
- C13-UI-001 and supporting governance capabilities for the UI + audit surfaces
