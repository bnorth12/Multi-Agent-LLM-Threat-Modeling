# C12 HITL Governance Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C12-HITL-001|Gate Workflow Implementation|The system SHALL implement HITL gates at all required decision points (input integrity, scope, boundary, STRIDE, threat, mitigation, release).|Gates are required for analyst control and governance.|Demonstration|Verified by walkthrough pausing at each required gate.|
|C12-HITL-002|Role-Based Permissions|The system SHALL enforce role-based permissions for all HITL actions.|Role-based control is required for separation of duties.|Test|Verified by permission tests for each role and action.|
|C12-HITL-003|Audit Trail Completeness|The system SHALL record a complete audit trail for all HITL actions, including rationale and before/after state.|Auditability is required for compliance and forensics.|Inspection|Verified by audit log review.|
|C12-HITL-004|Override Rationale Enforcement|The system SHALL require rationale for all analyst overrides at gates.|Rationale is required for traceability and review.|Test|Verified by UI/API validation rejecting overrides without rationale.|
|C12-HITL-005|Conditional Gate Trigger Policy|The system SHALL evaluate configured trigger rules for conditional Merge Conflict Resolution and Export Consistency gates.|Conditional gates are required only when risk or consistency conditions are met.|Test|Verified by trigger-rule tests that raise gates only when configured thresholds or conditions are met.|

## Conditional Trigger Defaults

Unless policy configuration overrides these values, the following defaults apply.

|Gate|Default Trigger Inputs|Default Threshold|Required Behavior|
|---|---|---|---|
|Input Integrity Gate (Gate 0)|parse_error_count, required_field_missing_count, schema_validation_pass_rate, source_provenance_complete|Trigger if parse_error_count > 0 OR required_field_missing_count > 0 OR schema_validation_pass_rate < 1.00 OR source_provenance_complete is false.|Pause before context merge and require explicit analyst decision before continuing.|
|Conditional Merge Conflict Resolution Gate|merge_conflict_count, approved_artifact_conflict_count, critical_field_conflict_count, conflict_severity_max|Trigger if approved_artifact_conflict_count >= 1 OR critical_field_conflict_count >= 1 OR conflict_severity_max is high OR merge_conflict_count >= 5.|Pause after context merge, require resolution and rationale, and block advancement until accepted.|
|Conditional Export Consistency Gate|canonical_stix_error_count, canonical_report_error_count, diagram_reference_error_count, consistency_warning_count|Trigger if canonical_stix_error_count > 0 OR canonical_report_error_count > 0 OR diagram_reference_error_count > 0 OR consistency_warning_count > 10.|Pause before publication and block release until accepted decision is recorded.|
