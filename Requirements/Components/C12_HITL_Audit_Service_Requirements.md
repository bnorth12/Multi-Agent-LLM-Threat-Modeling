# C12 HITL and Audit Service Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C12-HITL-001|Configured Gate Pausing|HITL Service SHALL pause execution at configured approval gates and await explicit analyst decision.|Controlled pauses are required for governance checkpoints.|Demonstration|Verified by workflow execution showing pause behavior at configured gate stages.|
|C12-HITL-002|Role-Constrained Actions|HITL Service SHALL support approve, reject, edit, and re-run actions at each gate according to role permissions.|Role constraints enforce separation of duties.|Test|Verified by role-matrix tests for each gate action outcome.|
|C12-HITL-003|Edit Diff Logging|Audit Service SHALL record before-and-after diffs for all analyst edits.|Diff logs provide accountability and forensic detail.|Test|Verified by edit action tests producing persisted before-and-after diff records.|
|C12-HITL-004|Protected Approved Artifacts|Audit Service SHALL prevent silent mutation of approved artifacts outside tracked workflows.|Silent mutation breaks trust in release artifacts.|Test|Verified by unauthorized mutation tests returning denied operation and immutable history retention.|
