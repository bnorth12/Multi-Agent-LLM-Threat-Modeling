# C02 Agent 01 Input Normalizer Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C02-A01-001|Canonical Transformation|Agent 1 SHALL transform raw text and table inputs into canonical graph structures without introducing unsupported fields.|Reliable normalization is foundational for all downstream stages.|Test|Verified by parser tests against canonical schema and unsupported-field rejection checks.|
|C02-A01-002|Deterministic ID Assignment|Agent 1 SHALL assign deterministic identifiers to new systems, subsystems, components, and data flows.|Stable IDs are required for merge, diff, and rerun consistency.|Test|Verified by repeated identical input runs producing identical IDs.|
|C02-A01-003|Unknown Boundary Marking|Agent 1 SHALL mark unknown trust-boundary status explicitly when source data is insufficient.|Unknown state is safer than implicit false confidence.|Inspection|Verified by artifact review on sparse input showing explicit unknown boundary flags.|
|C02-A01-004|ICD Source Compliance Flagging|Agent 1 SHALL preserve source provenance for ICD spreadsheet rows and narrative documents and SHALL emit structured compliance flags when required fields, interface references, or source mappings are missing or inconsistent.|Downstream stages and orchestrator gates need a machine-readable compliance record for ICD-derived inputs.|Test|Verified by invalid-input tests and browser upload evidence showing compliance errors are surfaced before downstream handoff.|
