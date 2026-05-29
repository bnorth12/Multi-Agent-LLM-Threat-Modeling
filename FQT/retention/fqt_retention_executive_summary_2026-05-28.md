# FQT Retention Executive Summary

Source manifest: `FQT/retention/fqt_retention_manifest_2026-05-28.json`

Generated from manifest timestamp: 2026-05-28T23:37:40

## High-Level Totals

- Total run folders evaluated: 64
- Keep full: 19
- Summarize-only: 45

## Signature Rollup

| Signature | Total | Keep Full | Summarize-Only |
|---|---:|---:|---:|
| FAIL_OTHER_FROM_FAILURE_EVIDENCE | 22 | 2 | 20 |
| FAIL_UI_TIMEOUT_VERIFIED | 3 | 2 | 1 |
| NO_REPORT_EMPTY | 7 | 2 | 5 |
| NO_REPORT_SCREENSHOTS_ONLY | 6 | 2 | 4 |
| NO_REPORT_UNKNOWN | 17 | 2 | 15 |
| SUCCESS | 9 | 9 | 0 |

## Governance Notes

- Successful runs are retained in full for release confidence evidence.
- Duplicate failures are reduced to pointer-backed archived evidence to control noise without losing traceability.
- Canonical first/last examples per signature remain in active evidence scope.
