# Test Execution Summary — Sprint 2026-10

## 1. Scope

Records automated validation evidence for LangGraph native orchestration refactor and CAV browser-upload workflow updates.

## 2. Automated Validation Commands

Baseline non-live (known environment-dependent exclusions):

```bash
python -m pytest Tests/unit/ --ignore=Tests/unit/test_chroma_adapter.py --ignore=Tests/unit/test_live_mode_failover_halt.py -q --tb=short -m "not llm_live"
```

Targeted updated tests:

```bash
python -m pytest Tests/unit/test_orchestrator.py Tests/unit/test_live_mode_failover_halt.py -q --tb=short
```

Integration and e2e (non-live marker path):

```bash
python -m pytest Tests/integration Tests/e2e -q --tb=short -m "not llm_live and not llm_live_browser"
```

Visible-browser CAV upload validation (opt-in):

```bash
RUN_VISIBLE_BROWSER_TESTS=1 pytest Tests/e2e/test_browser_cav_markdown_upload.py -v -m llm_live_browser -s
```

## 3. Results

- Pending local execution update in this sprint branch.
- Commands above are the required evidence set for S10 closeout.

## 4. Notes

- Browser test is intentionally opt-in and launches Chromium with `headless=False`.
- Live provider verification remains gated by environment credentials and connection validation setup.
