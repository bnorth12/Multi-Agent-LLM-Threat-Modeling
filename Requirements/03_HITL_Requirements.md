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
|HITL-012|Gate 0 Data Readiness Guard|Threat Modeler SHALL delay opening Gate 0 until preflight input integrity artifacts are ready for review payload construction, and SHALL fail with explicit timeout diagnostics when readiness is not achieved within policy bounds.|A readiness guard prevents race conditions where Gate 0 opens with incomplete or missing preflight evidence.|Test|Verified by orchestrator tests that wait for preflight readiness before opening Gate 0 and raise deterministic timeout errors when readiness never becomes true.|

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
|Gate 0 Readiness Guard (HITL-012)|preflight_snapshot_ready, preflight_required_sections_present, readiness_wait_elapsed_seconds|Allow Gate 0 trigger only when preflight_snapshot_ready is true AND required sections are present; fail if readiness wait exceeds configured timeout.|Prevent gate activation with incomplete data. Emit explicit readiness timeout failure and stop run progression.|
|Conditional Merge Conflict Resolution (HITL-010)|merge_conflict_count, approved_artifact_conflict_count, critical_field_conflict_count, conflict_severity_max|Trigger if approved_artifact_conflict_count >= 1 OR critical_field_conflict_count >= 1 OR conflict_severity_max is high OR merge_conflict_count >= 5.|Pause immediately after context merge. Require conflict resolution with rationale. Allow save draft. Resume only after accept as is or accept changes. If not triggered, bypass gate and log decision.|
|Conditional Export Consistency (HITL-011)|canonical_stix_error_count, canonical_report_error_count, diagram_reference_error_count, consistency_warning_count|Trigger if canonical_stix_error_count > 0 OR canonical_report_error_count > 0 OR diagram_reference_error_count > 0 OR consistency_warning_count > 10.|Pause before publication. Present consistency findings and diffs. Allow review, edit, save draft, accept as is, accept changes, reject. Resume publication only after accept as is or accept changes. If not triggered, bypass gate and log decision.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- HITL-001, HITL-009, HITL-012, and the conditional gates (HITL-010, HITL-011) derived from C12-HITL-001 (Human-in-the-Loop Governance) in docs/architecture/Capability_Hierarchy_Baseline.md and the L1/L2 HITL functions (F-HITL-TRACEABILITY-L1, F-HITL-GATE-CONTROL)

### Allocated To

- Allocated to C12-HITL-001 and realized in docs/design/software/Runtime_And_Orchestration_Design_Specification.md (gate integration, decision enforcement, conditional triggers) + src/threat_modeler/hitl/service.py and hitl/models.py, plus frontend gate surfaces (HITLGateManager.tsx)

### Refines

- The detailed conditional gate tables and default triggers here refine the higher-level HITL requirements in 03_HITL_Requirements.md (self) and project-level PRJ-006 (HITL Governance), PRJ-014 (Selective Re-Run), PRJ-028 (Orchestrator Gate Enforcement)
- Component-level C12_HITL_Requirements.md and C12_HITL_Audit_Service_Requirements.md provide further elaboration of the gate behaviors and audit side

### Satisfied By

- Gate 0 Input Integrity, Gate 0 Readiness Guard, Conditional Merge Conflict Resolution, and Conditional Export Consistency (plus the general pause/resume/reject with rationale) satisfied by:
  - Runtime_And_Orchestration_Design_Specification.md (orchestrator gate enforcement, state persistence for decisions)
  - src/threat_modeler/hitl/service.py (HitlService, decision recording, resume from checkpoint)
  - src/threat_modeler/hitl/models.py (gate models)
  - frontend/src/components/HITLGateManager.tsx and related UI for decision surfaces
  - 15_End_To_End rows (e.g., S12-034 for VS-010 / HITL gate control, multiple S13-005D gate projection rows) list the exact design + impl + verification

### Verified By

- Tests/integration/test_hitl_gate_set_2.py, Tests/integration/test_validation_gates.py (causal ordering, decision persistence, conditional triggers)
- Tests/test_hmi_backend_api.py and UI shell tests for gate UI flows
- FQT-004 (mandatory gates), FQT-005 (reject/recovery), FQT-006 (conditional gates)
- 15_End_To_End verification artifacts + Test Artifact IDs for HITL/C12 rows
- Governance outputs (independent reviews, sprint execution summaries) that evaluate gate compliance and evidence durability

### Depends On

- 01_Project_Requirements.md (PRJ-006, PRJ-014, PRJ-028, PRJ-029 for liveness at gates)
- 10_GUI_Requirements.md (GUI-032 and related gate control surfaces)
- 13_Runtime_State_And_Input_Contract_Requirements.md (state for gate context and projections)
- Runtime_And_Orchestration_Design_Specification.md and Prompt_Store_And_Runtime_State_Persistence_Design_Specification.md (for checkpoint/decision durability)
- 15_End_To_End_Traceability_Attributes_Registry.md (the governed chain for all HITL legs)
- C12-HITL capability and component requirements (C12_HITL_Requirements.md)
- 05_Verification_Strategy.md (race-condition and gate verification methods, VS-010)
- 18_Traceability_Governance_Operating_Model.md (HITL requirements are central to "Verification" upward and "Implementation" downward relationships, plus evidence substantiation for decisions)
