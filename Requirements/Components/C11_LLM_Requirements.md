# C11 LLM Provider Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C11-LLM-001|Provider Abstraction|The system SHALL support pluggable LLM provider backends, selectable by configuration.|Provider abstraction enables flexibility and risk management.|Test|Verified by switching provider config and running without code changes.|
|C11-LLM-002|Offline Mode Support|The system SHALL support offline-only operation with no external API calls.|Offline mode is required for classified or air-gapped deployments.|Test|Verified by running in offline mode and confirming no external calls.|
|C11-LLM-003|Provider Policy Enforcement|The system SHALL enforce policy controls on provider selection and usage.|Policy enforcement is required for compliance and risk management.|Test|Verified by policy config tests blocking unauthorized provider use.|
|C11-LLM-004|Live Request Timeout and Retry Budget|The system SHALL apply a configurable timeout and retry budget to live LLM requests, and the default live profile SHALL use a 900 second timeout and 2 attempts unless a higher-level policy overrides those values.|Live provider calls can take substantially longer than offline or cached execution and need explicit budgets to prevent indefinite waiting while still allowing provider retries.|Test|Verified by inspecting runtime defaults and executing live requests that honor the configured timeout and retry budget.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From
- C11-LLM-00x derived from C11-LLM-001 (Live Model Integration Governance) and C11-LLM-004-CAP in Capability_Hierarchy_Baseline.md

### Allocated To
- Allocated to C11-LLM-001 / F-LLM-TRACEABILITY-L1 / F-C11_LLM_004-TRACE-L2 realized in Model_Configuration_Design_Specification.md + src/threat_modeler/llm/openai_compatible_adapter.py + config.py + frontend PipelineConfig surfaces

### Refines
- PRJ-008 (Configurable Model Selection), INT-012/015 (Provider/Model Connection contracts), GUI-012/013/014 (model config GUI)

### Satisfied By
- Provider abstraction, offline mode support, policy enforcement, and live request timeout/retry budget satisfied by src/threat_modeler/llm/openai_compatible_adapter.py (OpenAICompatibleAdapter), src/threat_modeler/config.py, Model_Configuration_Design_Specification.md (see 15_End_To_End R01-003 and S13-005D configuration rows)

### Verified By
- Tests/e2e/test_live_llm_validation.py, Tests/unit/test_openai_compatible_adapter.py, Tests/test_hmi_backend_api.py (connection verification), FQT-002 provider/connection cases, 15_End_To_End verification for C11-LLM rows

### Depends On
- 01_Project_Requirements.md, 02_Interface_Requirements.md, 10_GUI_Requirements.md, Model_Configuration_Design_Specification.md, Runtime_And_Orchestration_Design_Specification.md (consumer of configured providers), 15_End_To_End_Traceability_Attributes_Registry.md, and C11-LLM capability definitions
