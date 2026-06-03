# Requirement Taxonomy

Date: 2026-05-29
Status: Canonical

## Purpose

Define the canonical requirement types used across the repository so requirements, issues, planning artifacts, and traceability matrices use the same classification model.

## Canonical Types

| Type | Meaning | Typical Examples |
|---|---|---|
| Functional | Describes behavior the system or a subsystem must perform. | Run orchestration, analysis steps, exports, UI actions, data transformations. |
| Nonfunctional | Describes a quality attribute or systemic constraint on the solution. | Performance, reliability, availability, usability, observability, security quality targets. |
| Policy | Describes a governance, procedural, compliance, or operating-mode rule. | Approval rules, retention rules, release policy, authentication policy, review policy. |
| Design constraint | Describes a mandated architectural, technology, lifecycle, or implementation constraint. | Required runtime, framework, deployment model, decomposition rule, state ownership rule. |
| Interface requirement | Describes a boundary contract, schema, payload, protocol, handshake, or data-handoff rule. | API contracts, event payloads, ICD mappings, stage I/O schemas, cross-boundary flows. |
| Capability-derived requirement | Describes a requirement decomposed directly from a mission capability or user capability statement. | Capability-to-function decomposition, scenario-derived behavior, mission flow coverage. |

## Classification Rules

1. Every requirement SHALL have exactly one primary type.
1. If a requirement clearly contains multiple unrelated behaviors, split it into separate requirements instead of overloading one row.
1. If a requirement mixes behavior with a boundary contract, classify the row by the dominant contract and move the remaining behavior into a separate requirement when possible.
1. If no existing type fits, propose a new type before sprint commitment rather than silently overloading another class.
1. Requirement rationale text SHOULD explain why the selected type is correct when the classification is not obvious.

## Repository Guidance

- Requirement files SHOULD label each row with a type field or type column.
- Sprint traceability matrices SHOULD carry the same type so planning and verification stay aligned.
- Mixed or ambiguous requirement statements SHOULD be normalized before implementation starts.

## Verification Artifact Mapping

Each requirement type MUST map to at least one primary verification artifact, even when that artifact is not a traditional executable test.

| Type | Primary verification artifact(s) | Notes |
|---|---|---|
| Functional | Unit, integration, or end-to-end test file; execution log; screenshot when UI-facing. | Prefer executable evidence that proves the behavior. |
| Nonfunctional | Benchmark report, load test, observability report, static analysis report, or measured evidence package. | Use the smallest artifact that objectively proves the quality attribute. |
| Policy | Governance policy document, enforcement implementation, policy validation report, or compliance checklist evidence. | Policies are usually verified by showing the rule, the enforcement mechanism, and a traceable review record. |
| Design constraint | Architecture/design detail, design review note, conformance test, or analysis package showing the constraint is enforced by the implementation. | For design constraints, show both the constraint and the implementation that realizes it. |
| Interface requirement | Contract file, schema, ICD, API spec, integration test, or protocol validation evidence. | Boundary requirements should verify the contract and at least one caller/callee path. |
| Capability-derived requirement | Decomposition matrix, scenario traceability record, function map, or downstream functional verification artifact. | This type often traces through a function set before reaching implementation evidence. |

## Verification Selection Rules

1. Every requirement record SHOULD name one primary verification artifact and may list supporting artifacts.
1. If the primary artifact is not a test file, the rationale SHOULD explain why the alternate artifact is the best proof of compliance.
1. Policy requirements are not expected to rely on unit tests alone; they SHOULD reference the policy document plus the enforcement path or review evidence.
1. Design constraints are not complete until the design artifact and the implementation artifact both show the constraint is honored.
1. Interface requirements SHOULD show the contract and at least one verification artifact proving the contract is respected across the boundary.

## Change Control

Any new requirement type or taxonomy refinement must be reflected in this file, the requirements policy, and the affected planning templates before the change is treated as canonical.
