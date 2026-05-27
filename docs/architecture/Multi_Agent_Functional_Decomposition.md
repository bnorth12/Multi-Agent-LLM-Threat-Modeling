# Multi-Agent Threat Modeler Functional Decomposition

## 1. Functional Decomposition Strategy

This decomposition defines functions from mission level to implementable activity level.

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
