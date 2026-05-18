# End-to-End Tests

Purpose:

- Validate complete runs from input fixtures to final artifacts.

Typical outputs validated:

- canonical graph
- stix bundle
- mermaid diagrams
- final report

Each scenario should document:

- source fixture set
- requirement IDs
- expected artifact checks
- browser automation requirements (if scenario requires live visible-browser validation)

## Lane and Marker Policy

- CI-safe lane uses: `-m "not llm_live and not llm_live_browser"`
- Controlled-live lane uses: `-m llm_live` or `-m llm_live_browser`
- `llm_live_browser` scenarios are opt-in and require `RUN_VISIBLE_BROWSER_TESTS=1`

Release evidence policy:

- Any release claim about live-provider correctness or browser upload behavior must include controlled-live evidence from this directory.
