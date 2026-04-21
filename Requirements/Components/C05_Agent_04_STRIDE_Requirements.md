# C05 Agent 04 STRIDE Requirements

| ID | Name | Requirement Text | Requirement Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|---|
| C05-A04-001 | STRIDE Score Assignment | Agent 4 SHALL assign STRIDE severity scores for each data flow using the configured scoring scale. | Quantified scoring is required for consistent risk ranking. | Test | Verified by STRIDE fixture tests with expected score outputs. |
| C05-A04-002 | Score Justification Output | Agent 4 SHALL provide concise justification text for each STRIDE dimension score. | Justification supports analyst review and calibration. | Inspection | Verified by artifact review confirming six STRIDE justification fields per flow. |
| C05-A04-003 | Override Preservation | Agent 4 SHALL preserve analyst-overridden scores and associated rationale metadata. | Human overrides must remain traceable and stable across reruns. | Test | Verified by override and rerun test confirming overridden values and rationale persistence. |
