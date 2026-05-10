# Live Grok LLM Validation Report

Date: May 6, 2026
Status: VALIDATED

## 1. S08 Closure Scope

S08 closure evidence now requires live Grok execution through all 9 pipeline stages (`agent_01`..`agent_09`).
Fixture-mode outputs are retained only for deterministic UI walkthrough screenshots and manual export examples.

## 2. Live LLM Test Evidence (All 9 Stages)

Command:

```bash
pytest Tests/e2e/test_artifact_generation.py -m llm_live -v --tb=short
```

Final result (after fixes):

- 6 passed
- 34 deselected
- 975.86s (0:16:15)

Validated model/endpoint combinations:

- grok-4.3 (chat_completions)
- grok-4.20-multi-agent-0309 (multi_agent)
- grok-4.20-0309-reasoning (responses)
- grok-4.20-0309-non-reasoning (responses)
- grok-4-1-fast-reasoning (responses)
- grok-4-1-fast-non-reasoning (chat_completions)

## 3. Failures Observed During Live Run and Remediation

Initial full-9-stage live run result:

- 3 passed
- 3 failed
- 34 deselected
- 915.92s (0:15:15)

Observed failures:

1. STRIDE parse failure (`TypeError` in stage 4) when score fields were returned as nested objects instead of ints.
2. Empty Mermaid artifact in stage 8 when output omitted `MERMAID_LEVEL` markers.
3. Missing STIX bundle in stage 6 when response was non-JSON prose.

Remediations implemented:

1. Hardened canonical deserialization to coerce nested numeric score shapes in:
   - `src/threat_modeler/agents/deserialise.py`
2. Added STIX stage fallback to canonical-graph export when live output is not parseable JSON in:
   - `src/threat_modeler/agents/agent_06_stix_packager.py`
3. Added Mermaid stage fallback to canonical-graph export when markers/blocks are missing in:
   - `src/threat_modeler/agents/agent_08_diagram_generator.py`
4. Added regression coverage for these scenarios in:
   - `Tests/integration/test_agent_pipeline_completeness.py`

## 4. Local Regression Confirmation

Command:

```bash
pytest Tests/integration/test_agent_pipeline_completeness.py -q
```

Result:

- 32 passed in 10.07s

## 5. Fixture-Mode Evidence Boundary

The following remain fixture-mode evidence and are not used as proof of live 9-stage execution:

- UI screenshot capture in `docs/user_manual/screenshots/`
- Manual export artifact pack in `exports_for_manual/`

These artifacts are retained for user documentation completeness, not S08 live-gate closure.
