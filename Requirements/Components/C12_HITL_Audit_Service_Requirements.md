# C12 HITL and Audit Service Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C12-HITL-001|Configured Gate Pausing|HITL Service SHALL pause execution at configured approval gates and await explicit analyst decision.|Controlled pauses are required for governance checkpoints.|Demonstration|Verified by workflow execution showing pause behavior at configured gate stages.|
|C12-HITL-002|Role-Constrained Actions|HITL Service SHALL support approve, reject, edit, and re-run actions at each gate according to role permissions.|Role constraints enforce separation of duties.|Test|Verified by role-matrix tests for each gate action outcome.|
|C12-HITL-003|Edit Diff Logging|Audit Service SHALL record before-and-after diffs for all analyst edits.|Diff logs provide accountability and forensic detail.|Test|Verified by edit action tests producing persisted before-and-after diff records.|
|C12-HITL-004|Protected Approved Artifacts|Audit Service SHALL prevent silent mutation of approved artifacts outside tracked workflows.|Silent mutation breaks trust in release artifacts.|Test|Verified by unauthorized mutation tests returning denied operation and immutable history retention.|
|C12-HITL-005|Conditional Gate Trigger Logging|HITL Service SHALL persist trigger-evaluation evidence when conditional gates are raised or bypassed.|Trigger evidence is required to justify conditional gate behavior during audits.|Test|Verified by tests asserting persisted trigger evaluation records for raised and bypassed conditional gates.|
|C12-HITL-006|Input Integrity Decision Capture|Audit Service SHALL capture analyst decision records for Gate 0 input integrity review before context merge.|Source integrity decisions must be traceable to trusted downstream outputs.|Inspection|Verified by audit review showing Gate 0 decision records linked to source artifact versions.|
