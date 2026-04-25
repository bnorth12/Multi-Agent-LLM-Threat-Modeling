# C12 HITL Governance Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C12-HITL-001|Gate Workflow Implementation|The system SHALL implement HITL gates at all required decision points (scope, boundary, STRIDE, threat, mitigation, release).|Gates are required for analyst control and governance.|Demonstration|Verified by walkthrough pausing at each gate.|
|C12-HITL-002|Role-Based Permissions|The system SHALL enforce role-based permissions for all HITL actions.|Role-based control is required for separation of duties.|Test|Verified by permission tests for each role and action.|
|C12-HITL-003|Audit Trail Completeness|The system SHALL record a complete audit trail for all HITL actions, including rationale and before/after state.|Auditability is required for compliance and forensics.|Inspection|Verified by audit log review.|
|C12-HITL-004|Override Rationale Enforcement|The system SHALL require rationale for all analyst overrides at gates.|Rationale is required for traceability and review.|Test|Verified by UI/API validation rejecting overrides without rationale.|
