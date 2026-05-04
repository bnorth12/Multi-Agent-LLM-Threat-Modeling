# HITL Requirements

Implementation options reference:

- see 09_HITL_Framework_Options.md

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|HITL-001|Scope Confirmation Gate|Threat Modeler SHALL provide Scope Confirmation Gate after context merge completion.|Early confirmation prevents downstream work on invalid scope.|Demonstration|Verified by run walkthrough pausing at scope gate after context merge stage.|
|HITL-002|Boundary Approval Gate|Threat Modeler SHALL provide Trust Boundary Approval Gate after trust-boundary validation.|Boundary errors drive major threat-model inaccuracies.|Demonstration|Verified by trust-boundary stage pause requiring analyst approval.|
|HITL-003|STRIDE Calibration Gate|Threat Modeler SHALL provide STRIDE Calibration Gate after STRIDE scoring.|Analyst calibration is needed for mission-context accuracy.|Demonstration|Verified by post-STRIDE review screen supporting approve and override actions.|
|HITL-004|Threat Plausibility Gate|Threat Modeler SHALL provide Threat Plausibility Gate after threat generation.|Threat quality requires analyst validation before mitigation mapping.|Demonstration|Verified by threat review gate with approve and reject paths.|
|HITL-005|Mitigation Adequacy Gate|Threat Modeler SHALL provide Mitigation Adequacy Gate after mitigation generation.|Control mappings must be reviewed for applicability and residual risk.|Demonstration|Verified by mitigation gate requiring analyst decision before release stages.|
|HITL-006|Final Release Gate|Threat Modeler SHALL provide Final Release Gate before report and STIX publication.|Final publication requires explicit accountable approval.|Demonstration|Verified by final gate requirement prior to export operations.|
|HITL-007|Override Rationale Capture|Threat Modeler SHALL require rationale entry for analyst overrides at all gates.|Rationale is necessary for audit and future review.|Test|Verified by UI/API validation rejecting override actions without rationale text.|
|HITL-008|Signed Decision Records|Threat Modeler SHALL preserve gate decisions as signed run records.|Signed records provide non-repudiation for governance.|Inspection|Verified by audit artifact review showing signed gate decision entries per run.|
|HITL-009|Input Integrity Gate (Gate 0)|Threat Modeler SHALL provide Input Integrity Gate before context merge to validate parsed ICD spreadsheets and narrative source documents.|Early source validation prevents downstream analysis on malformed or mis-mapped data.|Demonstration|Verified by run walkthrough pausing at Gate 0 and requiring analyst decision before context merge execution.|
|HITL-010|Conditional Merge Conflict Resolution Gate|Threat Modeler SHALL provide a conditional Merge Conflict Resolution Gate after context merge when incoming data conflicts with approved baseline artifacts.|Conflict-driven review prevents silent overwrite of previously approved models.|Test|Verified by conflict scenario tests that trigger a gate requiring analyst resolution before continuation.|
|HITL-011|Conditional Export Consistency Gate|Threat Modeler SHALL provide a conditional Export Consistency Gate before publication when canonical JSON, STIX, diagram, or report consistency checks fail or warning thresholds are exceeded.|Conditional release checks prevent publication of inconsistent output bundles.|Test|Verified by export consistency tests that trigger a gate and require analyst approval before publication.|

## Trigger Rule Table (Implementation Defaults)

The following defaults are required unless overridden by policy configuration.

Machine-readable config contract:

- docs/schemas/hitl_trigger_rules.schema.json

Tiny JSON schema snippet:

```json
{
  "type": "object",
  "required": ["version", "gates"],
  "properties": {
    "version": {"type": "string"},
    "gates": {
      "type": "object",
      "required": ["input_integrity", "merge_conflict_resolution", "export_consistency"]
    }
  }
}
```

Minimal config example:

```json
{
	"version": "1.0",
	"gates": {
		"input_integrity": {
			"enabled": true,
			"thresholds": {
				"parse_error_count_gt": 0,
				"required_field_missing_count_gt": 0,
				"schema_validation_pass_rate_lt": 1.0,
				"source_provenance_complete_required": true
			}
		}
	}
}
```

|Gate|Inputs|Threshold or Condition|Expected Gate Behavior|
|---|---|---|---|
|Gate 0 Input Integrity (HITL-009)|parse_error_count, required_field_missing_count, schema_validation_pass_rate, source_provenance_complete|Trigger if parse_error_count > 0 OR required_field_missing_count > 0 OR schema_validation_pass_rate < 1.00 OR source_provenance_complete is false.|Pause before context merge. Allow review, edit, save draft, accept as is, accept changes, reject. Block stage advancement until accept as is or accept changes.|
|Conditional Merge Conflict Resolution (HITL-010)|merge_conflict_count, approved_artifact_conflict_count, critical_field_conflict_count, conflict_severity_max|Trigger if approved_artifact_conflict_count >= 1 OR critical_field_conflict_count >= 1 OR conflict_severity_max is high OR merge_conflict_count >= 5.|Pause immediately after context merge. Require conflict resolution with rationale. Allow save draft. Resume only after accept as is or accept changes. If not triggered, bypass gate and log decision.|
|Conditional Export Consistency (HITL-011)|canonical_stix_error_count, canonical_report_error_count, diagram_reference_error_count, consistency_warning_count|Trigger if canonical_stix_error_count > 0 OR canonical_report_error_count > 0 OR diagram_reference_error_count > 0 OR consistency_warning_count > 10.|Pause before publication. Present consistency findings and diffs. Allow review, edit, save draft, accept as is, accept changes, reject. Resume publication only after accept as is or accept changes. If not triggered, bypass gate and log decision.|
