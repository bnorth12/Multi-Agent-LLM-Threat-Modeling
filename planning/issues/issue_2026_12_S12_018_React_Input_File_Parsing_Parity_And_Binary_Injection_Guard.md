# Issue S12-018: React Input File Parsing Parity and Binary Injection Guard

Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-018-RHMI_017-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_018_React_Input_File_Parsing_Parity_And_Binary_Injection_Guard.md
Verification Method: Sprint traceability verification
Status: In Review

Status: In Review
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

Full UAS suite runs in the React HMI showed severe downstream data sparsity because CSV/XLSX
uploads were not being normalized into structured `tables` payloads. Spreadsheet uploads could
be forwarded as raw text bytes into `raw_text`, reducing Agent 01 parse fidelity and weakening
Context Builder, Trust Boundary, STRIDE, and Threat outputs.

## Root Cause

- `frontend/src/App.tsx` previously composed `initial_state.raw_text` from `file.text()` for all file types.
- `.xlsx` content is not safe as plain text input and should be parsed into tabular rows.
- React path diverged from Streamlit ingestion behavior (`ui/screens/input_entry.py`) that parses
  CSV/XLSX into table rows.

## Remediation

- Added CSV/XLSX parsing in React run-creation flow using `xlsx`.
- Added `initial_state.tables` population for parsed rows.
- Preserved narrative-file ingestion in `initial_state.raw_text`.
- Updated API client typing to include optional `tables` payload.

## Acceptance Criteria

- CSV/XLSX uploads are represented as structured rows in `initial_state.tables`.
- Spreadsheet binary bytes are not inserted into `initial_state.raw_text`.
- Full UAS suite run restores expected data richness in trust boundaries, STRIDE, and threats.
- Sprint traceability and execution-log artifacts reference this defect and fix.

## Verification

- `frontend: npm install`
- `frontend: npm run test -- --run src/components/HITLGateManager.test.tsx`
- `Tests/test_hmi_backend_api.py` (explicit sprint verification evidence reference)
- Manual full UAS suite run in React wizard and review of downstream artifacts/screens

## Requirements and Traceability

- RHMI-017 in `Requirements/11_React_HMI_Refactor_Requirements.md`
- S12-REQ-018 in `planning/Sprint_2026_12_Traceability_Matrix.md`

## Changed Files

- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/package.json`
- `Requirements/11_React_HMI_Refactor_Requirements.md`
- `Requirements/12_React_HMI_Traceability_To_Tests.md`
- `planning/Sprint_2026_12_Traceability_Matrix.md`
- `planning/Sprint_2026_12_Execution_Log.md`
- `planning/issues/Sprint_2026_12_Issue_Tracker.md`
