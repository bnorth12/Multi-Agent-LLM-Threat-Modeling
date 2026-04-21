# Issue Draft: Implement Parser Normalization to Canonical Graph

## Title

Implement parser normalization from raw inputs to typed canonical graph

## Problem Statement

The current parser seam in `src/threat_modeler/parsing/input_normalizer.py` returns a placeholder dictionary that does not produce a typed `CanonicalThreatModelGraph`. This blocks reliable stage-1 ingestion, weakens schema contract continuity, and prevents realistic end-to-end pipeline behavior.

## Goal

Implement parser normalization that converts `ParserInput` payloads into a schema-aligned typed `CanonicalThreatModelGraph` artifact suitable for Agent 1 output and downstream validation.

## Scope

In scope:

- Implement normalization logic in `ParserInterface.normalize`
- Return a typed canonical graph model (or strict schema-aligned payload mapped to the typed model)
- Derive deterministic placeholder IDs where source IDs are missing
- Map raw text and table input into initial canonical graph structures
- Ensure produced artifacts are compatible with schema-backed validation
- Add focused tests for parser normalization behavior

Out of scope:

- Advanced NLP extraction quality improvements
- Retrieval integration for parser enrichment
- Full confidence scoring and policy reasoning
- HITL persistence changes

## Primary Files Likely Affected

- `src/threat_modeler/parsing/input_normalizer.py`
- `src/threat_modeler/models/canonical.py`
- `src/threat_modeler/agents/agent_01_input_normalizer.py`
- `Tests/` parser-focused tests

## Acceptance Criteria

- Parser normalization produces canonical graph artifacts aligned with `docs/schemas/canonical_graph.schema.json`.
- Output can be consumed by existing orchestrator and validation seams without compatibility hacks.
- Deterministic IDs are generated for required entities when source data omits IDs.
- Normalization supports both raw text-only and table-inclusive inputs.
- Tests cover successful normalization and malformed input handling.

## Requirement Linkage

- PRJ-001
- PRJ-002
- PRJ-004
- CMP-A01-001
- CMP-A01-002
- CMP-A01-003
- INT-001
- INT-002
- INT-003

## Verification Approach

- Unit tests for parser input-to-canonical output mapping
- Validation check against schema-backed validator
- Inspection of generated IDs and required-field population

## Risks and Notes

- Parser output shape must stay aligned with schema-backed validation to avoid hidden contract drift.
- Deterministic ID rules should be documented and stable for rerun consistency.
- Scope should prioritize correctness and contract compliance over extraction sophistication.

## Definition of Done

- Parser normalization produces schema-aligned canonical artifacts.
- Tests cover key normalization paths and error handling.
- Integration with existing Agent 1 and validator seams remains stable.
