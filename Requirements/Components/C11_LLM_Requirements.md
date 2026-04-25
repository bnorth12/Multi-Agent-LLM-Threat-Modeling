# C11 LLM Provider Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C11-LLM-001|Provider Abstraction|The system SHALL support pluggable LLM provider backends, selectable by configuration.|Provider abstraction enables flexibility and risk management.|Test|Verified by switching provider config and running without code changes.|
|C11-LLM-002|Offline Mode Support|The system SHALL support offline-only operation with no external API calls.|Offline mode is required for classified or air-gapped deployments.|Test|Verified by running in offline mode and confirming no external calls.|
|C11-LLM-003|Provider Policy Enforcement|The system SHALL enforce policy controls on provider selection and usage.|Policy enforcement is required for compliance and risk management.|Test|Verified by policy config tests blocking unauthorized provider use.|