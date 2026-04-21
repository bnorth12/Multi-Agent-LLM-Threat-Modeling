# C01 Orchestrator and State Requirements

| ID | Name | Requirement Text | Requirement Rationale | Verification Method | Verification Statement |
|---|---|---|---|---|---|
| C01-ORCH-001 | Explicit Stage Routing | LangGraph Orchestrator SHALL route execution through all enabled agents using explicit next-state transitions. | Explicit routing prevents ambiguous control flow. | Test | Verified by orchestration tests asserting expected transition sequence for configured pipeline. |
| C01-ORCH-002 | Checkpoint Persistence | LangGraph Orchestrator SHALL persist checkpoints after each stage transition. | Checkpoints enable restart and audit continuity. | Test | Verified by stage restart tests recovering from persisted checkpoints. |
| C01-STATE-001 | Versioned Snapshots | State Store SHALL version canonical graph snapshots per run and per stage. | Versioning supports traceability and rollback analysis. | Inspection | Verified by storage inspection showing stage-indexed version history. |
| C01-STATE-002 | Baseline Preservation | State Store SHALL preserve analyst-approved baselines as non-editable history entries. | Approved baselines must remain immutable for governance. | Test | Verified by mutation attempts against approved baseline returning authorization or immutability errors. |
| C01-STATE-003 | Validation Blocker | Validation Layer SHALL block stage handoff on schema failure and emit structured error records. | Blocking prevents propagation of invalid state. | Test | Verified by schema-failure injection producing halted flow and structured error object. |
