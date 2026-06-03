# Provider Status Verification & Fallback Detection

## Problem

The browser-based UI was falling back to **Local/Fixture** mode instead of maintaining the configured **live LLM provider** (xAI/Grok) across screen navigations. This meant:

- User configures xAI/Grok in Pipeline Configuration screen
- Settings apply successfully (`✅ Settings applied. Provider: xAI/Grok`)
- But when navigating to another screen, it falls back to **Local/Fixture**
- Result: LLM calls don't execute; fixture deterministic data is used instead
- Real LLM errors and actual behavior are masked

## Root Cause Analysis

1. **Session State Serialization Issue**: `RuntimeSettings` dataclass may not persist properly across full page reruns (Streamlit's navigation model)
1. **No Visibility into Fallback**: No indicator showing which provider was active, making it hard to debug
1. **Silent Fallback**: When `settings_override` is not found in session_state, the code falls back to `build_default_settings()` which defaults to fixture mode without warning

## Solution Implemented

### 1. Added Provider Status Indicator (Always Visible)

**Location**: Sidebar under "LLM Provider" metric

```python
def get_current_provider_status() -> tuple[str, str]:
    """Get current provider and detect if using live LLM or local fixture.

    Returns:
        Tuple of (provider_label, status_indicator)
        Examples:
          ("xAI/Grok", "✅ LIVE LLM")
          ("Local/Fixture", "⚪ LOCAL (FIXTURE)")
          ("Unconfigured", "⚪ UNCONFIGURED")
    """
```

**Display Format** (in sidebar):
```
LLM Provider
xAI/Grok          ← Provider name
✅ LIVE LLM        ← Status indicator
```

### 2. Added Verification on Every Screen Change

**Location**: `src/threat_modeler/ui/app.py` after every page render

```python
def verify_provider_not_fallen_back() -> bool:
    """Verify that provider is still configured as live (not fallen back to fixture).

    Logs to console when:
    - Fallback is detected (fixture/offline mode active)
    - Live provider is confirmed (debug output)
    - Settings are missing/invalid
    """
```

**Console Output Examples**:
```
[PROVIDER OK] Screen: Home, Using live provider: xai/grok-4
[PROVIDER OK] Screen: Stage Results, Using live provider: xai/grok-4
[PROVIDER FALLBACK] Screen: Pipeline Configuration, Reason: provider=fixture
[PROVIDER FALLBACK] Screen: Input Entry, Reason: offline_only=True
```

### 3. Enhanced `render_execution_status_badge()`

**Now shows TWO metrics** in sidebar:

| Metric | Shows | Example |
|--------|-------|---------|
| **LLM Provider** | Current provider + live/local status | "xAI/Grok" + "✅ LIVE LLM" |
| **Execution Status** | Execution state + elapsed time | "🟠 PAUSED" + "104s" |

## How It Works

### Screen Navigation Flow

```
User navigates to screen X
         ↓
Page renders
         ↓
App calls: verify_provider_not_fallen_back()
         ↓
If settings_override missing/invalid:
  - Print [PROVIDER FALLBACK] to console
  - get_current_provider_status() returns "⚪ UNCONFIGURED"

If settings_override valid & offline:
  - Print [PROVIDER FALLBACK] with reason
  - get_current_provider_status() returns "⚪ LOCAL (FIXTURE)"

If settings_override valid & live:
  - Print [PROVIDER OK] with details
  - get_current_provider_status() returns "✅ LIVE LLM"
         ↓
Sidebar updates to show current provider status
```

### Real-Time Validation

Every screen change triggers validation:

```python
# In app.py, after rendering the selected page:
_PAGES[selected_page]()                      # Render page content
verify_provider_not_fallen_back()            # Verify provider + log fallback if detected
```

## Testing the Fix

### Manual Test: Verify Provider Persists

1. **Navigate** to Pipeline Configuration
1. **Select** Provider: xAI/Grok
1. **Click** Apply Settings → see `✅ Settings applied. Provider: xAI/Grok`
1. **Check Sidebar** → should show: `xAI/Grok` + `✅ LIVE LLM`
1. **Navigate** to Home screen
1. **Verify Sidebar** → should STILL show: `xAI/Grok` + `✅ LIVE LLM`
1. **Click** on 5+ different screens (Stage Results, Threat Review, Token Usage, etc.)
1. **Verify** provider status remains consistent on all screens

### Console Test: Check Debug Logs

Open browser DevTools (F12) → Console tab, then navigate between screens:

**Expected Output**:
```
[PROVIDER OK] Screen: Home, Using live provider: xai/grok-4
[PROVIDER OK] Screen: Input Entry, Using live provider: xai/grok-4
[PROVIDER OK] Screen: Pipeline Configuration, Using live provider: xai/grok-4
[PROVIDER OK] Screen: Threat Review, Using live provider: xai/grok-4
```

**Fallback Output** (should NOT see):
```
[PROVIDER FALLBACK] Screen: Home, Reason: settings_override not set
[PROVIDER FALLBACK] Screen: Stage Results, Reason: provider=fixture
```

## Files Modified

| File | Changes |
|------|---------|
| `src/threat_modeler/ui/execution.py` | Added `get_current_provider_status()`, `verify_provider_not_fallen_back()`, Enhanced `render_execution_status_badge()` |
| `src/threat_modeler/ui/app.py` | Import verification function, Call `verify_provider_not_fallen_back()` after each page render |

## Known Limitations & Future Improvements

1. **Session State Persistence**: If session is lost (browser tab closed/reloaded), settings_override may not restore. Mitigated by persisting settings to run registry on execution start.

1. **Cross-Tab Sync**: Settings changes in one tab don't auto-sync to another tab. User must refresh to see changes.

1. **Initial Load**: First time loading a paused run may show "Unconfigured" briefly before syncing. Fixed on first navigation.

## Debugging: When to Check Logs

| Symptom | Debug Step |
|---------|-----------|
| Provider shows "⚪ UNCONFIGURED" | Check browser console for `[PROVIDER FALLBACK]` messages |
| Provider shows "⚪ LOCAL (FIXTURE)" but shouldn't | Verify Pipeline Configuration: settings should have offline_only=False, provider=xai |
| LLM calls aren't happening | Check both provider status AND Last Prompt screen for token counts (0=fixture) |
| Settings reset after navigation | Check if `settings_override` is being cleared somewhere unexpected |

## Integration with Token/Prompt Validation

The provider status indicator works with the new `test_live_llm_validation.py` test suite:

1. **Before running tests**: Verify sidebar shows "✅ LIVE LLM"
1. **During test run**: Monitor token usage in Last Prompt screen
1. **After test run**: Check console logs for `[PROVIDER OK]` on every screen

This ensures that:

- ✅ Live LLM is being used (not fixture)
- ✅ Token counts are > 0 (not fixture fallback)
- ✅ Prompts vary by stage (real LLM, not cached)
- ✅ State is consistent across all screens

## Summary

The new provider status verification system provides:

1. **Visibility**: Always see which provider is active via sidebar metric
1. **Verification**: Automatic validation on every screen change
1. **Debugging**: Console logs pinpoint when/why fallback occurs
1. **Confidence**: Verify live LLM is actually being used before relying on results
