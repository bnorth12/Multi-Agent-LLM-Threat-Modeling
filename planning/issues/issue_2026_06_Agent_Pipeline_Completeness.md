# Issue: Sprint 2026-06 Agent Pipeline Completeness

## Sprint
2026-06

## GitHub Issue
GH #18

## Owner Role
Orchestrator Engineer and Technical Lead

## Description
Deliver an operational stage registry with all nine agents implemented, a configurable LLM provider
adapter (xAI/Grok), a hybrid execution strategy (fixture-driven for automated tests, real LLM calls for
sprint validation), and contract-safe execution across all configured stages.

## Scope

### LLM Provider Adapter
- Add `src/threat_modeler/llm/` package with `xai_adapter.py` implementing the xAI Grok API
  (OpenAI-compatible endpoint at `https://api.x.ai/v1`).
- API key loaded from `XAI_API_KEY` environment variable; never hard-coded.
- `ModelSelection.provider == "xai"` activates real LLM calls.
- `ModelSelection.provider == "unconfigured"` or `offline_only=True` activates fixture mode.
- Adapter interface: `complete(system_prompt: str, user_message: str) -> str`.

### Agent Implementations
- Implement concrete agent classes for all nine stages in `src/threat_modeler/agents/`:
  - `agent_01_input_normalizer.py` — normalises parsed state tables and raw_text
  - `agent_02_context_builder.py` — builds hierarchical context graph
  - `agent_03_trust_boundary_validator.py` — identifies and scores trust boundaries
  - `agent_04_stride_scorer.py` — applies STRIDE categories
  - `agent_05_threat_generator.py` — generates concrete threats
  - `agent_06_stix_packager.py` — packages STIX objects
  - `agent_07_mitigation_generator.py` — maps mitigations to threats
  - `agent_08_diagram_generator.py` — emits Mermaid diagram source
  - `agent_09_report_writer.py` — generates markdown report
- Each agent: loads system prompt from `docs/agents/agent_XX_*.txt`.
- Fixture mode: returns deterministic canned output from `Tests/fixtures/agents/`.
- LLM mode: sends prompt + serialised state to Grok, deserialises response back to state.
- All nine agents registered in `build_default_agents()`.

### Stage Registry and Transitions
- Operational registry maps stage IDs `agent_01` through `agent_09` to agent instances.
- Deterministic transition sequence enforced by `PipelineSettings.enabled_stage_ids`.
- Contract validation (CanonicalGraphValidator) runs at every stage boundary.

## Acceptance Criteria
- `build_default_agents()` returns entries for `agent_01` through `agent_09`.
- Golden-path fixture run executes all nine configured stages and produces a non-empty canonical graph.
- Contract validation check runs and passes at every stage transition in the fixture run.
- A stage that produces an invalid state causes a `ValidationHaltError` before the next stage executes.
- With `XAI_API_KEY` set and `provider="xai"`, `agent_01` sends a real prompt to Grok and the response
  is deserialised into `FrameworkState` without error (sprint validation gate — not part of automated CI).
- Fixture mode and LLM mode are selected solely by `ModelSelection` configuration; no code changes required.
- Agent prompts are loaded from `docs/agents/` at runtime; prompt files are not bundled in agent classes.

## Requirement Links
- PRJ-003
- PRJ-004
- PRJ-005
- PRJ-008

## Dependencies
None (first implementation issue in S06 sequence).

## Implementation Notes
- xAI Grok API is OpenAI-SDK-compatible. Use `openai` Python package pointed at `https://api.x.ai/v1`.
- Fixture output files live in `Tests/fixtures/agents/agent_XX_output.json`.
- Prompt files already exist in `docs/agents/`; agents should read them with `Path(__file__).parent`.

## Status
- [ ] Not started
- [ ] In progress
- [x] Completed

## Completion Evidence
- Date: 2026-05-04
- Initials: BN
- All nine agent classes implemented in `src/threat_modeler/agents/` (agent_01 through agent_09).
- `build_default_agents()` returns all nine entries; registry verified by unit tests.
- xAI adapter in `src/threat_modeler/llm/xai_adapter.py`; fixture adapter used by default.
- Fixture-mode golden-path run exercises all nine stages in CI (240 tests passing).
- `ValidationHaltError` raised on invalid stage output — verified by negative-path integration test.
- Agent prompts loaded from `docs/agents/` at runtime; no prompt text in agent classes.
- CI test run: 240 passed, 1 deselected (llm_live), 0 failures.
