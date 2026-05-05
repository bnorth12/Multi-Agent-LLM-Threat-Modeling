# Issue: Sprint 2026-06 Artifact Generation and E2E Validation

## Sprint
2026-06

## GitHub Issue
GH #21

## Owner Role
Test Lead and Orchestrator Engineer

## Description
Implement the four export artifact types (canonical JSON, STIX 2.1, Mermaid, markdown report) and
validate full workflow behavior with golden-path and negative-path end-to-end tests. Sprint validation
includes one real LLM call via Grok to confirm prompt-to-response formatting works end to end.

## Scope

### Exporters
- `src/threat_modeler/exports/json_exporter.py` — serialises canonical graph to JSON.
- `src/threat_modeler/exports/stix_exporter.py` — maps canonical graph threats to STIX 2.1 objects.
- `src/threat_modeler/exports/mermaid_exporter.py` — emits Mermaid diagram source from graph.
- `src/threat_modeler/exports/report_exporter.py` — renders markdown report from agent_09 output.
- Exporter registry in `src/threat_modeler/exports/__init__.py`.

### E2E Tests (fixture mode)
- Golden-path: full pipeline run using fixture-mode agents; assert all four artifact classes are
  present and non-empty in final state.
- Negative-path: induce a stage failure; assert `ValidationHaltError` is raised and no downstream
  artifacts are written.
- Both tests are automated and run in CI without an LLM API key.

### Grok Sprint Validation Gate (manual, not CI)
- One E2E test marked `@pytest.mark.llm_live` that calls real Grok API (`provider="xai"`).
- Runs `agent_01` through at minimum `agent_02` with a sample input fixture.
- Validates response deserialises into `FrameworkState` without error.
- Evidence of this run is required for sprint closeout (recorded in test execution summary).

## Acceptance Criteria
- One complete fixture-mode run emits non-empty artifacts for all four classes: JSON, STIX, Mermaid,
  and markdown.
- E2E tests validate artifact structure and presence; tests pass in CI.
- Negative-path E2E test demonstrates safe halt before downstream artifacts are produced.
- With `provider="xai"` and `XAI_API_KEY` set, the `@pytest.mark.llm_live` test passes and
  response data is deserialised into valid `FrameworkState` (sprint validation gate evidence).
- All four exporters are importable from `src.threat_modeler.exports`.

## Requirement Links
- PRJ-005
- PRJ-011
- INT-010
- INT-011

## Dependencies
- S06-01 (Agent Pipeline Completeness) — pipeline must be operational for E2E tests to run.
- S06-03 (Retrieval Evidence Linkage) — JSON exporter must include `source_ids`/`confidence` fields.

## Implementation Notes
- STIX 2.1 mapping: each threat becomes a `threat-actor` or `attack-pattern` STIX object; mitigations
  become `course-of-action` objects. Use `stix2` Python library.
- Mermaid exporter output is a string; no rendering validation required in this sprint.
- `@pytest.mark.llm_live` tests are excluded from default pytest run
  (add `-m "not llm_live"` to CI config).

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- Four exporters delivered: `json_exporter.py`, `stix_exporter.py`, `mermaid_exporter.py`, `report_exporter.py`; all importable from `src.threat_modeler.exports`.
- Golden-path E2E test `Tests/e2e/test_artifact_generation.py` asserts non-empty artifacts for all four classes.
- Negative-path E2E test asserts `ValidationHaltError` before downstream artifacts are produced.
- `@pytest.mark.llm_live` test present and correctly excluded from CI (`-m "not llm_live"`).
- CI test run: 240 passed, 1 deselected (llm_live), 0 failures.
