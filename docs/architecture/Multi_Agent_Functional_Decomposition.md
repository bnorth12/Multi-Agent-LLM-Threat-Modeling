# Multi-Agent Threat Modeler Functional Decomposition

## 1. Functional Decomposition Strategy

This decomposition defines functions from mission level to implementable activity level.

- Every functional requirement must be represented by one or more functions at some level of the decomposition.
- Functions are linked by explicit data flows, and those flows become the basis for interface and ICD definition.
- ICDs describe the logical and physical paths that data flows take across the architecture.
- Interface functions are a distinct class of functions that live at boundary crossings between components, systems, users, and external dependencies.
- Interface functions are often the place where a functional requirement becomes a concrete boundary contract, transformation, validation, or handshake.

- `L0`: mission function
- `L1`: mission subfunctions
- `L2`: system service functions
- `L3`: stage and governance functions
- `L4`: operational activities and checks

## 2. L0-L2 Decomposition

| Level | ID | Function Name | Function Description |
|---|---|---|---|
| L0 | M0 | Threat Model Production Mission | Produce governed canonical threat model artifacts from source inputs. |
| L1 | M1 | Source Ingestion and Normalization | Accept and normalize narrative and ICD source inputs. |
| L1 | M2 | Canonical Graph Lifecycle Management | Build, enrich, validate, and version canonical graph state. |
| L1 | M3 | Threat Analysis and Synthesis | Score STRIDE, generate threats, and derive mitigations. |
| L1 | M4 | Artifact Packaging and Export | Produce STIX, Mermaid, report, and canonical exports. |
| L1 | M5 | Governance and Runtime Integrity | Enforce HITL gates, run control, and auditability. |
| L2 | F210 | Input Payload Validation | Validate required source fields and structural expectations. |
| L2 | F220 | Canonical Initialization | Construct initial canonical graph from normalized input. |
| L2 | F230 | Context Enrichment | Add hierarchy and context for downstream threat analysis. |
| L2 | F240 | Trust Boundary Validation | Validate interface boundaries and crossing assertions. |
| L2 | F250 | STRIDE Scoring | Assign STRIDE vectors and rationale per interface/flow. |
| L2 | F260 | Threat Construction | Build concrete threats tied to canonical entities. |
| L2 | F270 | Mitigation Construction | Generate mitigations linked to threats and residual risk. |
| L2 | F280 | STIX Packaging | Transform canonical threat entities into STIX 2.1 bundle. |
| L2 | F290 | Diagram Construction | Build architecture and threat visualization diagrams. |
| L2 | F300 | Report Composition | Write analyst-facing final report and summaries. |
| L2 | F310 | Gate Decision Enforcement | Pause, approve, reject, and resume through HITL control. |
| L2 | F320 | Run State Management | Manage asynchronous run lifecycle and health telemetry. |
| L2 | F330 | Prompt Configuration Management | Maintain editable prompts with version history and rollback. |
| L2 | F340 | Snapshot and Evidence Management | Persist run snapshots and release evidence artifacts. |

## 3. L3 Functional Decomposition (Stage and Governance)

### 3.1 Agent Pipeline Functions

| L3 ID | Parent | Function Name | Implementing Stage/Service |
|---|---|---|---|
| F221 | F220 | Normalize source model | Agent 01 |
| F231 | F230 | Build hierarchical context | Agent 02 |
| F241 | F240 | Validate trust boundaries | Agent 03 |
| F251 | F250 | Score STRIDE categories | Agent 04 |
| F261 | F260 | Generate concrete threats | Agent 05 |
| F281 | F280 | Package STIX bundle | Agent 06 |
| F271 | F270 | Generate mitigations | Agent 07 |
| F291 | F290 | Generate Mermaid diagrams | Agent 08 |
| F301 | F300 | Compose human report | Agent 09 |

### 3.2 Governance and Control Functions

| L3 ID | Parent | Function Name | Implementing Service |
|---|---|---|---|
| F311 | F310 | Open gate with payload context | Gate controller + UI |
| F312 | F310 | Capture approve/reject rationale | HITL decision interface |
| F313 | F310 | Resume from approved checkpoint | Orchestrator runtime |
| F321 | F320 | Track run status and stage progression | Backend run manager |
| F322 | F320 | Detect liveness degradation and fail closed | Runtime integrity controls |
| F331 | F330 | Load prompts from backend authority | Prompt store backend |
| F332 | F330 | Persist prompt version history | Prompt store backend |
| F341 | F340 | Export complete run snapshot | Snapshot manager |
| F342 | F340 | Restore snapshot into runtime state | Snapshot manager |

## 4. L4 Operational Activities

Representative L4 activities used for verification and operations:

- Validate ICD table columns and semantic fields.
- Validate narrative source completeness and provenance.
- Assert canonical graph schema compliance at each stage boundary.
- Assert entity ID continuity across stage handoffs.
- Enforce gate pause before downstream stage execution.
- Record gate actor, action, rationale, and timestamp.
- Validate export artifact integrity and schema conformance.
- Capture run diagnostics: status, stage, gate, heartbeat, elapsed time.

## 5. Function Allocation to Canonical Graph Lifecycle

Function groups by data interaction pattern:

- Graph construction functions: F220, F230, F240
- Graph analysis functions: F250, F260, F270
- Graph transformation functions: F280, F290, F300
- Graph governance functions: F310, F320, F340
- Graph configuration and control functions: F330

## 6. Verification Anchors

Primary requirement anchors for functional coverage:

- PRJ-001 Unified Input Ingestion; PRJ-002 Canonical Graph Authority; PRJ-003 Deterministic Pipeline; PRJ-004 Stage Validation Gate; PRJ-005 Full Threat Workflow.
- PRJ-006 HITL Governance; PRJ-014 Selective Re-Run; PRJ-015 Fail-Safe Halting; PRJ-019 Asynchronous Backend State Authority; PRJ-020 Live-Mode Integrity Halt on Provider Degradation.
- PRJ-023 LangGraph Native Orchestration; PRJ-026 Inter-Agent Handoff Integrity; PRJ-027 ICD Source Compliance Validation; PRJ-028 Orchestrator Gate Enforcement and Resume Control; PRJ-029 Live Run Liveness Fail-Closed; PRJ-030 Prompt Store Authority and Fail-Closed Loading.

Detailed mapping is maintained in:

- `Multi_Agent_Function_And_Interface_Requirements_Matrix.md`

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

- M0 (Threat Model Production Mission) satisfies PRJ-001, PRJ-003, PRJ-005 (core mission to produce governed canonical threat model artifacts)
- M1 (Source Ingestion and Normalization) satisfies PRJ-001, PRJ-027, INT-002 (unified input ingestion, ICD/narrative compliance)
- M2 (Canonical Graph Lifecycle Management) satisfies PRJ-002, PRJ-003, INT-005, PRJ-026 (canonical authority, deterministic pipeline, handoff integrity, stage events)
- M3 (Threat Analysis and Synthesis) satisfies PRJ-005 (full threat workflow including STRIDE, threat gen, mitigations)
- M4 (Artifact Packaging and Export) satisfies PRJ-011, INT-010, INT-011 (export bundle, STIX/report contracts)
- M5 (Governance and Runtime Integrity) satisfies PRJ-006, PRJ-014, PRJ-015, PRJ-019, PRJ-020, PRJ-023, PRJ-028, PRJ-029, PRJ-030 (HITL, re-run, fail-safe, async state, live-mode, langgraph, gate/resume, liveness, prompt authority)
- L2 functions F210-F340 satisfy the L1 mission subfunctions and allocated component requirements (see Function_Hierarchy_Registry.md for ID bindings)
- L3 stage/agent functions (F221-F301) satisfy stage-specific requirements exercised by the 9-agent pipeline (C02-A01-* through C10-A09-*)
- L3 governance functions (F311-F342) satisfy HITL, orchestration, and snapshot requirements (HITL-*, C01-ORCH-*, PRJ-*)
- L4 operational activities satisfy verification strategy (VS-009) and schema/contract assertions at boundaries

### Realizes

- M0 realizes CAP-L0-THREAT-MODELER
- M1 realizes functions allocated under C02 (input), C15 (interfaces) and supporting C16 delivery
- M2 realizes C01-ORCH-001 (orchestration) and C15-INT-001 (interface/canonical)
- M3 realizes C04/C05/C06 (STRIDE, threat, mitigation) capability slices
- M4 realizes C07/C08/C09/C10 packaging and reporting capability slices plus C14 verification evidence
- M5 realizes C01-ORCH, C12-HITL, C13-UI, C16-PRJ, C17-SCR, C18-ADM governance and control capabilities
- F220 (Canonical Initialization) realizes core of M2 / C01 and C15
- F240 (Trust Boundary Validation), F250 (STRIDE Scoring) realize M3 analysis slices
- F310 (Gate Decision Enforcement), F320 (Run State Management) realize M5 / C12 and C01
- L3 agent functions realize the L2 data-interaction functions (F220-F300 groups)
- All L3/L4 realize their parent L2 function in the decomposition

### Provides / Requires

- M1 Provides: normalized payload (narrative + ICD); Requires: well-formed source per 02_Interface_Requirements and schemas
- M2 Provides: versioned canonical graph state at each stage boundary; Requires: valid input from M1 and approved gate decisions from M5
- M3 Provides: scored STRIDE entities, concrete threats, mitigations; Requires: enriched canonical context from M2
- M4 Provides: STIX bundle, Mermaid diagrams, human report, JSON exports; Requires: approved final canonical + artifact references from prior stages
- M5 Provides: gate records, run snapshots, evidence ledger, prompt versions; Requires: runtime state, canonical validation, and operator decisions
- Graph construction (F220-F230) Provide: initial + context-enriched canonical; Require: validated ingestion
- Graph governance (F310+) Provide: pause/resume checkpoints and audit records; Require: stage results + HITL policy

### Implemented By

- M0, M5 (governance) : src/threat_modeler/orchestrator.py (FrameworkOrchestrator, stage graph) ; src/threat_modeler/backend/run_manager.py ; src/threat_modeler/hitl/service.py
- M1 (ingestion) : src/threat_modeler/agents/agent_01_input_normalizer.py ; src/threat_modeler/parsing/icd_parser.py ; src/threat_modeler/parsing/narrative_parser.py
- M2 (canonical lifecycle) : src/threat_modeler/models/canonical.py ; src/threat_modeler/agents/agent_02_context_builder.py ; src/threat_modeler/validation.py
- M3 (analysis) : src/threat_modeler/agents/agent_03_trust_boundary_validator.py ; agent_04_stride_scorer.py ; agent_05_threat_generator.py ; agent_07_mitigation_generator.py
- M4 (packaging/export) : src/threat_modeler/agents/agent_06_stix_packager.py ; agent_08_diagram_generator.py ; agent_09_human_report_writer.py ; export paths in orchestrator/run_manager
- L3 agent functions : one-to-one with agent_0N_*.py under src/threat_modeler/agents/ (F221=agent_01, F231=agent_02, ..., F301=agent_09)
- L3 governance : src/threat_modeler/hitl/ ; backend/run_manager ; prompt store backend (src/threat_modeler/ ? or frontend+backend prompt config)
- Snapshot functions F341/F342 : snapshot manager in backend/run_manager and evidence packaging design
- UI-mapped L3 (gate, progress) : frontend/src/components/HITLGateManager.tsx , ExecutionProgress.tsx and related React components
- L4 activities exercised by unit/integration tests under Tests/ and FQT plan execution

### Depends On

- Functional decomposition Depends On: stable L0-L2 IDs and parent capability references in Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md
- All M* and F* Depend On: corresponding requirement IDs allocated in 15_End_To_End_Traceability_Attributes_Registry.md with architecture/design + implementation + verification legs
- M2/M3/M4 data flow Depends On: canonical schema (docs/schemas/canonical_graph.schema.json) and ICD contracts
- Governance functions (M5) Depend On: 03_HITL_Requirements.md , 05_Verification_Strategy.md , and live governance config + planning artifacts
- L4 operational activities Depend On: executable verification (Tests/) that assert the described behaviors at stage boundaries and gates
