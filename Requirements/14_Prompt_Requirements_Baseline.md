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

_None recorded._ <!-- [Cap-ID or Req-ID] — rationale -->

### Allocated To

_None recorded._ <!-- [Req-ID] in [artifact path] -->

### Refines

_None recorded._ <!-- [Req-ID] refines [Req-ID] — rationale -->

### Satisfied By

_None recorded._ <!-- [Function-ID or design element] in [artifact path] -->

### Verified By

_None recorded._ <!-- [Tests/path/test.py] :: [test case or Req-ID] -->

### Depends On

_None recorded._ <!-- [Req-ID] — dependency rationale -->
