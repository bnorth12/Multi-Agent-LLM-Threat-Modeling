# C01 Orchestrator and State Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|C01-ORCH-001|Explicit Stage Routing|LangGraph Orchestrator SHALL route execution through all enabled agents using explicit next-state transitions.|Explicit routing prevents ambiguous control flow.|Test|Verified by orchestration tests asserting expected transition sequence for configured pipeline.|
|C01-ORCH-002|Checkpoint Persistence|LangGraph Orchestrator SHALL persist checkpoints after each stage transition.|Checkpoints enable restart and audit continuity.|Test|Verified by stage restart tests recovering from persisted checkpoints.|
|C01-ORCH-003|Execution Mode Governance|Pipeline configuration SHALL support both `linear` and `langgraph-compatible` execution modes. Release and validation profiles SHALL use `langgraph-compatible`, while `linear` mode SHALL be treated as a compatibility mode for controlled scenarios.|Mode governance keeps runtime behavior explicit and auditable during migration and release operations.|Inspection|Verified by configuration reference review and release test evidence showing `execution_mode=langgraph-compatible` for governed validation runs.|
|C01-ORCH-004|Gate Decision Enforcement|Orchestrator SHALL pause execution at each HITL gate, persist the gate context and decision state, and resume only after an explicit approved decision is recorded.|The orchestrator must enforce human approval as a hard control point rather than treating gates as advisory prompts.|Test|Verified by gate pause/resume tests confirming paused state, persisted decisions, and controlled continuation after approval.|
|C01-ORCH-005|Canonical Handoff Integrity|Orchestrator SHALL pass each approved stage output to the next enabled agent as a canonical handoff record that preserves correlation identifier, source stage, compliance metadata, and approved version reference.|Downstream agents require an exact and auditable upstream artifact so the multi-agent workflow remains deterministic and traceable.|Test|Verified by pipeline execution traces confirming each downstream stage consumes the prior approved canonical output and emits consistent handoff metadata.|
|C01-STATE-001|Versioned Snapshots|State Store SHALL version canonical graph snapshots per run and per stage.|Versioning supports traceability and rollback analysis.|Inspection|Verified by storage inspection showing stage-indexed version history.|
|C01-STATE-002|Baseline Preservation|State Store SHALL preserve analyst-approved baselines as non-editable history entries.|Approved baselines must remain immutable for governance.|Test|Verified by mutation attempts against approved baseline returning authorization or immutability errors.|
|C01-STATE-003|Validation Blocker|Validation Layer SHALL block stage handoff on schema failure and emit structured error records.|Blocking prevents propagation of invalid state.|Test|Verified by schema-failure injection producing halted flow and structured error object.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From
- C01-ORCH-00x and C01-STATE-00x derived from C01-ORCH-001 (Orchestration and Stage Control) and C01-ORCH-002-CAP / C01-ORCH-003-CAP in Capability_Hierarchy_Baseline.md

### Allocated To
- Allocated to C01-ORCH-001 / F-ORCH-TRACEABILITY-L1 / F-ORCH-STATE-TRANSITIONS and realized in Runtime_And_Orchestration_Design_Specification.md + src/threat_modeler/orchestrator.py (FrameworkOrchestrator, LangGraph path, checkpoint, gate enforcement, canonical handoff) + backend/run_manager.py + state.py

### Refines
- PRJ-023 (LangGraph), PRJ-028 (orchestrator gate/resume), PRJ-026 (handoff integrity), INT-005 (stage events), and the corresponding project-level requirements

### Satisfied By
- Explicit stage routing, checkpoint persistence, execution mode governance, gate decision enforcement, canonical handoff integrity, versioned snapshots, baseline preservation, and validation blocker satisfied by src/threat_modeler/orchestrator.py, src/threat_modeler/backend/run_manager.py, src/threat_modeler/state.py, and Runtime_And_Orchestration_Design_Specification.md (see 15_End_To_End S12-033, S13-001, S13-004, S13-005* RIC/ ORCH rows)

### Verified By
- Tests/unit/test_framework_orchestrator_langgraph.py, Tests/integration/test_agent_pipeline_completeness.py, Tests/integration/test_validation_gates.py, FQT gate and pipeline cases, 15_End_To_End verification artifacts for C01-ORCH / C01-STATE rows, and governance surface coverage checks

### Depends On
- 01_Project_Requirements.md (PRJ-023/026/028), 13_Runtime_State_And_Input_Contract_Requirements.md, 03_HITL_Requirements.md, Capability_Hierarchy_Baseline.md, Function_Hierarchy_Registry.md, Runtime_And_Orchestration_Design_Specification.md, 15_End_To_End_Traceability_Attributes_Registry.md, and 18_Traceability_Governance_Operating_Model.md (orchestration is a primary example of "Implementation" and "Verification" relationships)
