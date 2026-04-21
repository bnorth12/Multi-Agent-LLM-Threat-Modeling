# C06 Agent 05 Threat Generator Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C06-A05-001|Risk-Triggered Threat Generation|Agent 5 SHALL generate concrete threats for flows meeting configured risk trigger criteria.|Threat generation must be focused on material risk.|Test|Verified by threshold tests generating threats only for qualifying flows.|
|C06-A05-002|Threat Taxonomy Mapping|Agent 5 SHALL attach threat taxonomy references where available, including ATTACK, CAPEC, and CWE identifiers.|Taxonomy mapping supports analyst alignment and interoperability.|Test|Verified by output validation requiring at least one mapped identifier when available in retrieval evidence.|
|C06-A05-003|Likelihood and Impact Scoring|Agent 5 SHALL emit likelihood and impact values for each generated threat.|Threat prioritization requires impact and likelihood values.|Test|Verified by schema and range checks for likelihood and impact fields on each threat.|
