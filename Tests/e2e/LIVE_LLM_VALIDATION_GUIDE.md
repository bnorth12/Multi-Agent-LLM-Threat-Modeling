# Live LLM Validation Guide

This guide explains how to validate that the browser-based threat model run is executing against the **live LLM** (not fixtures) with token/prompt tracking for each gate.

## Overview

The validation framework has two components:

1. **test_live_llm_validation.py** - Unit/integration tests that hook into the adapter to intercept LLM calls
2. **test_browser_run_validation.py** - Browser-based validation with gate-by-gate token tracking
3. **test_browser_cav_markdown_upload.py** - Visible-browser upload validation for CAV fixture + markdown files

Governance note:

- Treat this guide as controlled-live lane execution only.
- CI-safe pipelines should exclude `llm_live` and `llm_live_browser` markers.

## How to Use: Manual Validation During Browser Run

### Step 1: Start the Browser Run (VISIBLE)

```bash
# Install browser-test dependencies (includes Streamlit test harness)
pip install -r Tests/requirements_e2e.txt

# Terminal 1: Start Streamlit test harness with browser auto-open
streamlit run src/threat_modeler/ui/app.py --logger.level=debug
```

The browser will open to `http://localhost:8501` showing the UI live.

### Step 2: Navigate Through Input Entry

1. Open **Input Entry** screen
2. Enter system name: `Test System`
3. Paste architecture text (or upload file)
4. Provide validation - should show: `✅ xai / grok-4 — live LLM calls will be made`
5. Click **▶ Start Threat Model Run**

### Step 3: Monitor Token Usage at Each Gate

#### At Gate 1 (Scope Confirmation)

1. **Home** screen shows: `Stage Progress` with stages 1-2 complete
2. Navigate to **Last Prompt** to see the actual prompt sent to LLM
3. Check for:
   - ✅ Prompt contains actual system architecture
   - ✅ Model shows: `grok-4` or `grok-4-multi-agent`
   - ✅ Token usage shows non-zero values (e.g., `Prompt: 45 | Completion: 120`)

#### Token Usage Capture (Last Prompt Screen)

The **Last Prompt** screen shows:
```
Model: grok-4
Provider: xai
Prompt:
[System message]
[User question about system architecture]

Token Usage:
Prompt Tokens: 45
Completion Tokens: 120
Total: 165
```

**Expected token ranges per gate:**
- Gate 1 (Scope): 50-300 tokens
- Gate 2 (Boundary): 200-1000 tokens
- Gate 3 (STRIDE): 500-2000 tokens
- Gate 4 (Threats): 300-1500 tokens
- Gate 5 (Mitigations): 200-1200 tokens

### Step 4: Identify Fixture Fallback (Negative Test)

**If you see these indicators, fixture fallback occurred:**
- Token Usage: `Prompt: 0 | Completion: 0`
- Model shows: `fixture_grok_v1` or similar
- Prompt contains pre-canned responses (not based on your system)
- Runtime is instant (< 1 second per stage)

### Step 5: Gate-by-Gate Validation Checklist

| Gate | Expected Behavior | Validation |
|------|---|---|
| **Gate 1** | Input validation, LLM confirms system name parsed | ✓ Tokens > 0, prompt has system info, no errors |
| **Gate 2** | Context enrichment, LLM builds hierarchical graph | ✓ Tokens > 200, prompt mentions subsystems |
| **Gate 3** | Trust boundary analysis, LLM identifies crossings | ✓ Tokens > 500, prompt contains "boundary" or "trust" |
| **Resume** | LLM continues from pause, no state loss | ✓ Consistent token tracking, no "RuntimeError" alerts |

## How to Use: Automated Validation Tests

### Run Live LLM Validation Tests

```bash
# Test 1: Verify live provider used (not fixtures)
pytest Tests/e2e/test_live_llm_validation.py::TestLiveLLMValidation::test_live_llm_not_fixture_fallback -v -m llm_live -s

# Test 2: Validate Gate 1 has LLM calls with tokens
pytest Tests/e2e/test_live_llm_validation.py::TestLiveLLMValidation::test_gate_1_has_llm_calls_with_tokens -v -m llm_live -s

# Test 3: Validate Gate 3 substantial tokens
pytest Tests/e2e/test_live_llm_validation.py::TestLiveLLMValidation::test_gate_3_stride_validation_with_substantial_tokens -v -m llm_live -s

# Test 4: Validate prompts vary by stage
pytest Tests/e2e/test_live_llm_validation.py::TestLiveLLMValidation::test_prompt_content_varies_by_stage -v -m llm_live -s
```

### Run Browser Run Validation

```bash
# Validate gate-by-gate token usage within expected ranges
pytest Tests/e2e/test_browser_run_validation.py::TestBrowserRunValidation -v -m llm_live_browser -s

# Shows JSON report in: ./test_reports/live_llm_validation_*.json
```

### Run Visible Browser CAV Upload Validation

```bash
# Windows (PowerShell)
$env:RUN_VISIBLE_BROWSER_TESTS="1"

# macOS/Linux
# export RUN_VISIBLE_BROWSER_TESTS=1

pytest Tests/e2e/test_browser_cav_markdown_upload.py -v -m llm_live_browser -s
```

This test opens a visible Chromium window (`headless=False`), loads the Input Entry
screen, uploads:

- `Tests/fixtures/inputs/icd/icd_charlie_v1.xlsx`
- `Tests/fixtures/inputs/descriptions/description_cav.md`
- `Tests/fixtures/inputs/descriptions/description_avionics.md`

and verifies file names are rendered by the UI upload list.

## Interpreting Results

### Success Indicators ✅

```
✓ Live LLM Call Report
  Total calls: 4
  Total tokens: 1850
  Fixture fallback detected: False

  Call 1: grok-4, /chat/completions, Tokens: 165 (prompt: 45 | completion: 120)
  Call 2: grok-4, /chat/completions, Tokens: 560 (prompt: 150 | completion: 410)
  Call 3: grok-4, /chat/completions, Tokens: 1125 (prompt: 450 | completion: 675)
```

### Failure Indicators ❌

```
✗ Fixture Fallback Detected
  Token usage: 0 (should be > 0)
  Model: fixture_grok_v1 (should be grok-4)
  Provider: fixture (should be xai)

✗ Zero Token Usage
  Indicates adapter never reached live provider
  Check: env THREAT_MODELER_LLM_PROVIDER=xai
```

## Real Example: Full Gate Progression

### Step-by-Step with Token Tracking

```
1. GATE 1 (Scope Confirmation)
   ✅ Home shows: Stages 1-2 Complete
   ✅ Last Prompt shows: Model=grok-4, Tokens=165
   ✅ Threat Review: Gate 1 · Status: Open
   👉 Action: Click "Approve Gate"

2. GATE 2 (Boundary Approval)
   ✅ Home shows: Stages 1-2 Complete, 3 Running
   ✅ Last Prompt shows: Model=grok-4, Tokens=560
   ✅ Stage Results: agent_02 → Complete
   ✅ Threat Review: Gate 2 · Status: Open
   ✅ No stale error messages
   👉 Action: Click "Approve Gate"

3. GATE 3 (STRIDE Calibration)
   ✅ Home shows: Stages 1-3 Complete, 4 Running
   ✅ Last Prompt shows: Model=grok-4, Tokens=1125
   ✅ Stage Results: agent_03 → Complete
   ✅ Threat Review: Gate 3 · Status: Open
   ✅ State aligned across all screens
   ✅ Cumulative tokens: 1850
```

## Environment Configuration

For the tests to run against live LLM:

```bash
# Required (Windows PowerShell)
$env:THREAT_MODELER_LLM_PROVIDER="xai"
$env:THREAT_MODELER_LLM_MODEL="grok-4"
$env:THREAT_MODELER_LLM_API_KEY="<your_xai_api_key>"

# Required (macOS/Linux)
# export THREAT_MODELER_LLM_PROVIDER=xai
# export THREAT_MODELER_LLM_MODEL=grok-4
# export THREAT_MODELER_LLM_API_KEY=<your_xai_api_key>

# Optional (project config overrides these)
$env:THREAT_MODELER_LLM_TIMEOUT_SECONDS="300"
$env:THREAT_MODELER_LLM_MAX_ATTEMPTS="5"

# Optional live-test harness heartbeat (seconds)
$env:THREAT_MODELER_LIVE_TEST_HEARTBEAT_SECONDS="15"
```

## Project-Level Configuration (Preferred)

Instead of env vars, use Pipeline Configuration screen in UI:

1. Navigate to **Pipeline Configuration**
2. Under "Live Request Reliability":
   - Request timeout per attempt: 300 seconds
   - Max retry attempts: 5
3. Save (persisted to run registry)

### Heartbeat During Long LLM Calls

When live calls are slow, the live validation harness prints periodic heartbeat messages while waiting for provider output, for example:

```text
[live-llm heartbeat] waiting for provider response (model=grok-4, mode=chat_completions, elapsed=15s)
```

This indicates the request is still in progress and has not silently fallen back to fixture mode.

## Debugging: Token Usage Not Showing?

### Check 1: Provider Configured
```python
# In app.py or test
from threat_modeler.config import build_default_settings
settings = build_default_settings()
assert settings.provider.provider_type == "live"  # Should be "live"
```

### Check 2: Adapter Created with Config
```python
# Should show timeout/max_attempts from settings
adapter = _build_live_adapter(settings.model)
print(f"Adapter timeout: {adapter._timeout_seconds}")  # Should be 180
print(f"Adapter retries: {adapter._max_attempts}")     # Should be 3
```

### Check 3: Monitor LLM Calls
```bash
# Add debug logging
streamlit run src/threat_modeler/ui/app.py --logger.level=debug 2>&1 | grep -E "grok|token|xai"
```

## Common Issues & Solutions

| Issue | Cause | Fix |
|-------|-------|-----|
| Zero token usage | Fixture fallback | Check `THREAT_MODELER_LLM_PROVIDER=xai` env var |
| "RuntimeError: timeout" | Timeout too short | Increase timeout/retries (recommended 300s and 5 attempts) |
| Long wait with no heartbeat | Heartbeat interval not set | Set `THREAT_MODELER_LIVE_TEST_HEARTBEAT_SECONDS=15` (or similar) |
| State inconsistency | Stale error carryover | Ensure latest code with state cleanup |
| Model shows "fixture_grok" | Provider not recognized | Clear env, restart Streamlit |

## Next Steps

After validating:

1. ✅ Gate 1-3 execute with live LLM (token > 0)
2. ✅ Prompts vary by stage
3. ✅ State stays aligned across Home/Stage Results/Threat Review
4. ✅ No fixture fallback detected

You can be confident the system is working correctly against live LLM with proper timeout/retry configuration.

## Files

- `test_live_llm_validation.py` - Core LLM validation tests
- `test_browser_run_validation.py` - Browser/UI validation with token tracking
- `test_browser_cav_markdown_upload.py` - Visible browser CAV markdown upload automation
- `test_reports/` - JSON reports from validation runs
- `.../Last Prompt` screen - Real-time token usage during browser run
