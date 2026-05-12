# S10-003: CAV Browser Live Validation Workflow

## Issue Summary

Add automated visible-browser coverage for CAV fixture upload workflow (ICD + markdown narratives) and document execution instructions.

## Related Requirements

- PRJ-016
- PRJ-024
- VS-009

## Acceptance Criteria

- [x] Add CAV markdown fixture for upload workflow.
- [x] Add opt-in visible-browser test that uploads CAV files in Input Entry UI.
- [x] Update live validation guide with the new command and expectations.

## Status

Resolved

## Implementation Notes

- Added fixture: `Tests/fixtures/inputs/descriptions/description_cav.md`
- Added e2e automation: `Tests/e2e/test_browser_cav_markdown_upload.py`
- Updated guide: `Tests/e2e/LIVE_LLM_VALIDATION_GUIDE.md`

## Closure Notes

Test is intentionally opt-in and requires `RUN_VISIBLE_BROWSER_TESTS=1`; browser launches in visible mode (`headless=False`).
