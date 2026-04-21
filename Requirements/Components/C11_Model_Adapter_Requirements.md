# C11 Model Adapter Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C11-LLM-001|Runtime Model Selection|Model Adapter SHALL select active model provider and model name from runtime configuration.|Runtime selection avoids code churn and improves portability.|Test|Verified by configuration-switch tests selecting different providers and models without code changes.|
|C11-LLM-002|Policy-Constrained Allowlists|Model Adapter SHALL support policy-constrained model allowlists by deployment mode.|Policy controls are required for security and compliance.|Test|Verified by policy tests permitting allowlisted models and rejecting non-allowlisted models.|
|C11-LLM-003|Extensible Provider Integration|Model Adapter SHALL support future provider additions without agent contract changes.|Extensibility reduces future integration cost.|Analysis|Verified by architecture review showing adapter extension points and unchanged agent interface contracts.|
