# Issue S12-028: Previous Canonical Graph as Optional Run Input for Incremental Enrichment

Sprint: 2026-12
Requirement ID: UNKNOWN-REQ
Parent Capability ID: C16-PRJ-001
Parent Function ID: F-UNKNOWN-TRACEABILITY-L1
Child Function ID: F-S12-028-PRJ_013-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_028_Prior_Canonical_Graph_As_Optional_Run_Input.md
Verification Method: Sprint traceability verification
Status: In Review

Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

There is no way to provide a previous canonical graph as an optional input when starting a
new run for the same system.

The intended behavior for this issue is:

- Analyst starts a new run with new source input (updated ICD/description).
- Analyst optionally supplies a canonical graph exported from a prior run of that system.
- Pipeline treats that prior graph as a baseline, preserves approved prior elements, and
  adds or updates only the newly inferred details from the new run input.
- Analyst reviews the delta (what changed) rather than re-reviewing the entire model.

This is PRJ-013 incremental enrichment in practical terms. The gap today is that neither
the setup wizard nor orchestrator exposes this baseline input path.

### Clarification: What This Change Is and Is Not

- This change IS: optional baseline seeding for a new run of the same system.
- This change IS NOT: replacing normal fresh-run behavior.
- This change IS NOT: blindly overwriting current outputs with old outputs.

## Affected Requirements

- PRJ-013 in Requirements/01_Project_Requirements.md
  (Incremental Enrichment — SHALL support incremental model enrichment without
  destructive overwrite of previously approved data; the mechanism to load a prior
  canonical graph is the missing implementation)
- INT-002 in Requirements/02_Interface_Requirements.md
  (Agent Input Contract — canonical graph payload is an agent input; a prior graph
  loaded as baseline must be injected at the correct stage handoff point)
- HITL-010 in Requirements/03_HITL_Requirements.md
  (Conditional Merge Conflict Resolution Gate — conflicts between incoming data and an
  approved baseline require a gate; this gate's baseline is the prior canonical graph)
- New requirement needed: a GUI requirement specifying the optional prior canonical graph
  input field in the setup wizard or run configuration screen (GUI-039 or equivalent)
- New requirement needed: an interface requirement specifying the baseline graph input
  contract (INT-002 extension or new INT-015)

## Scope

### Setup Wizard Input Field

- The setup wizard (or run configuration screen) includes an optional file upload field
  labeled "Prior Canonical Graph (optional)" that accepts a canonical JSON file exported
  from a previous run of the same system.
- The field is clearly optional — omitting it starts a fresh run from the uploaded
  system description (current behavior).
- When provided, the prior canonical graph is validated against the canonical schema
  before the run is initiated; invalid files are rejected with a clear error message.

### Orchestrator Baseline Injection

- When a prior canonical graph is present, the orchestrator provides it to agent_01
  (input normalizer) or the stage 2 context builder as the baseline canonical graph for
  the new run.
- Agents that support incremental merge (comparing new model output against the baseline)
  use the baseline to preserve approved elements and flag conflicts.
- The HITL-010 Merge Conflict Resolution Gate is triggered when the incoming normalized
  graph conflicts with elements from the baseline.

### Run Metadata

- The run record persists a reference to the prior canonical graph (run ID of the source
  run, or a content hash of the uploaded file) so the enrichment chain is auditable.

### Export

- When a run uses a prior canonical graph baseline, the exported canonical JSON and STIX
  bundle clearly distinguish elements that were carried forward from the baseline from
  elements that are new in the current run (e.g., via a `source` or `provenance` field).

## Acceptance Criteria

- [ ] Setup wizard includes an optional "Prior Canonical Graph" file upload field.
- [ ] Uploading an invalid file surfaces a schema validation error before run initiation.
- [ ] When a prior canonical graph is provided, the orchestrator injects it as the
      baseline at the correct pipeline stage.
- [ ] Previously approved elements from the baseline are preserved in the output
      (not destructively overwritten).
- [ ] New-run output includes carried-forward baseline elements plus net-new/updated
  elements inferred from the new run input.
- [ ] HITL-010 Merge Conflict Gate fires when conflicts are detected between the new
      model output and baseline elements.
- [ ] Run record persists a reference to the prior canonical graph source.
- [ ] Exported artifacts carry provenance fields distinguishing baseline vs. new elements.
- [ ] New GUI requirement (GUI-039) added for the prior canonical graph input field.
- [ ] Traceability matrix updated to link GUI-039 and any new INT requirement to PRJ-013.

## Implementation Notes

- The prior canonical graph input is an optional file upload on the setup wizard,
  parallel to the system description upload that already exists.
- The canonical schema validator already exists; reuse it for baseline validation.
- The orchestrator must be extended to pass the baseline graph through the stage context
  alongside the run input so agents can reference it. Consider a `baseline_canonical`
  field in the stage context alongside the existing `canonical` field.
- The merge conflict detection logic (for HITL-010) should compare baseline element IDs
  against newly generated elements and flag divergences in identity, classification,
  or trust boundary assignment.

## Expected Primary Files

- frontend/src/components/ (setup wizard or run configuration screen — add baseline upload)
- src/threat_modeler/orchestrator.py (baseline injection and conflict detection)
- src/threat_modeler/backend/run_manager.py (persist baseline reference in run record)
- src/threat_modeler/server/api.py (run creation endpoint — accept optional baseline file)
- Requirements/10_GUI_Requirements.md (add GUI-039 prior canonical graph input)
- Requirements/02_Interface_Requirements.md (extend INT-002 or add new INT requirement)
- Requirements/04_Traceability_Matrix.md (link new requirements to PRJ-013)

## Validation Plan

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- manual: export canonical graph from run A, start run B with it as the baseline,
  verify prior elements are preserved, verify conflict gate fires on a modified element,
  verify exported artifacts carry provenance

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active pipeline run is complete.
- This issue should be scoped and estimated carefully — the orchestrator baseline injection
  and conflict detection is a significant new capability. Consider whether it warrants its
  own sprint or a dedicated feature branch.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Parking Lot 2026-99 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_99_Parking_Lot_Skills_Layer_and_Avionics_Specialization.md
