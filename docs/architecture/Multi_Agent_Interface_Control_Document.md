# Multi-Agent Threat Modeler Interface Control Document (ICD)

## 1. Scope

This ICD defines internal, external, and user-facing interfaces for the Multi-Agent Threat Modeler application architecture.

It represents the logical and physical path constraints for data flows between functions, components, and external systems.
Interface functions are the boundary-crossing behaviors that this ICD constrains, including validation, transformation, protocol handling, and user interaction handoffs.

## 2. Interface Classification

- `INTF-I`: internal interfaces (service-to-service, stage-to-stage)
- `INTF-E`: external interfaces (provider APIs, input files, export files)
- `INTF-U`: user interfaces (analyst actions and HMI workflows)

For readability, the Contract Anchors column lists both the requirement identifier and the requirement name where practical. The identifier preserves traceability, while the name lets a reader understand why the interface matters without leaving the table.

## 3. Internal Interfaces

| Interface ID | Type | Source | Destination | Payload | Contract Anchors |
|---|---|---|---|---|---|
| INTF-I-001 | Internal | Input normalization service | Canonical initialization service | normalized source envelope; source provenance | INT-001 Parser Request Contract; INT-002 Agent Input Contract; PRJ-001 Unified Input Ingestion; PRJ-027 ICD Source Compliance Validation |
| INTF-I-002 | Internal | Stage N orchestrator adapter | Stage N+1 adapter | canonical graph subset + stage metadata + correlation ID | INT-002 Agent Input Contract; INT-003 Agent Output Contract; INT-005 Stage Event Contract; PRJ-026 Inter-Agent Handoff Integrity |
| INTF-I-003 | Internal | Stage validator | Orchestrator gate controller | validation result codes and blocking severity | INT-004 Validation Result Contract; PRJ-004 Stage Validation Gate; PRJ-015 Fail-Safe Halting |
| INTF-I-004 | Internal | Gate UI adapter | Orchestrator runtime | approve/reject/override decision record | INT-006 HITL Decision Contract; PRJ-006 HITL Governance; PRJ-028 Orchestrator Gate Enforcement and Resume Control |
| INTF-I-005 | Internal | Runtime manager | UI projection layer | run status, stage, gate, heartbeat, diagnostics | PRJ-019 Asynchronous Backend State Authority; GUI-016 Backend Runtime State Projection; GUI-027 Run Diagnostics Panel |
| INTF-I-006 | Internal | Prompt editor UI | Prompt store backend | prompt update request, version metadata, rollback target | PRJ-018 Agent Prompt Configurability; PRJ-030 Prompt Store Authority and Fail-Closed Loading; GUI-009 Agent Prompt Editor; GUI-010 Agent Prompt Version History |
| INTF-I-007 | Internal | Snapshot manager | Runtime and persistence backend | snapshot export/import package | PRJ-017 Run Snapshot Portability; GUI-007 Run Snapshot Export; GUI-008 Run Snapshot Restore |

## 4. External Interfaces

| Interface ID | Type | Source | Destination | Payload | Contract Anchors |
|---|---|---|---|---|---|
| INTF-E-001 | External | Analyst source upload | Ingestion subsystem | ICD table files and narrative sources | PRJ-001 Unified Input Ingestion; PRJ-027 ICD Source Compliance Validation; GUI-001 Input Entry Form |
| INTF-E-002 | External | Runtime provider client | LLM provider endpoint | provider request envelope and auth config | INT-012 Provider Config Contract; INT-015 Model Connection Contract; PRJ-008 Configurable Model Selection; GUI-012 Model Provider Selection Screen; GUI-013 Model Connection Details Configuration; GUI-014 Model Connection Validation |
| INTF-E-003 | External | Export service | Analyst downstream tools | canonical JSON export | PRJ-011 Export Artifact Set; INT-011 Report Export Contract; GUI-006 Results Export Interface |
| INTF-E-004 | External | Export service | STIX ecosystem tools | STIX 2.1 bundle | PRJ-011 Export Artifact Set; INT-010 STIX Export Contract; GUI-018 STIX Threat Model Viewer |
| INTF-E-005 | External | Export service | Diagram consumers | Mermaid diagram source/output | PRJ-011 Export Artifact Set; GUI-020 Mermaid Diagram Viewer; GUI-034 Mermaid Multi-Diagram Review Workspace |
| INTF-E-006 | External | Export service | Governance/release evidence | markdown report, token usage, version inventories | PRJ-021 Component Semantic Version Authority; PRJ-022 Component File Version Traceability; GUI-015 Token Usage Telemetry Dashboard and Export; GUI-024 Component and File Version Visibility |

## 5. User Interfaces

| Interface ID | Type | Source Actor | Destination Logic | Interaction | Contract Anchors |
|---|---|---|---|---|---|
| INTF-U-001 | User | Analyst | Input ingestion logic | submit source data and context | GUI-001 Input Entry Form; GUI-001A Pipeline Auto-Execution After Form Submission; PRJ-016 Analyst Graphical Interface |
| INTF-U-002 | User | Reviewer/Approver | Gate decision logic | approve/reject/override with rationale | GUI-002 HITL Gate Screens; GUI-032 Input Integrity Preflight Review Gate; GUI-033 Post-Stage-1 Normalization Review Gate; PRJ-006 HITL Governance |
| INTF-U-003 | User | Analyst | Runtime control logic | observe status, diagnostics, and liveness | GUI-003 Pipeline Status Dashboard; GUI-017 Live Mode Failover Hard-Stop Visibility; GUI-026 Run Liveness Telemetry; GUI-027 Run Diagnostics Panel |
| INTF-U-004 | User | Analyst | Artifact logic | inspect graph, threats, STIX, Mermaid, report | GUI-018 STIX Threat Model Viewer through GUI-025 Markdown Viewer and Editor; GUI-041 Header-Authoritative Artifact Domain Navigation; GUI-042 Header Review and Export Icon Entry Points |
| INTF-U-005 | User | Authorized operator | Prompt store logic | edit/revert prompt and parameters | GUI-009 Agent Prompt Editor; GUI-010 Agent Prompt Version History; PRJ-018 Agent Prompt Configurability; PRJ-030 Prompt Store Authority and Fail-Closed Loading |
| INTF-U-006 | User | Analyst | Snapshot logic | export/import run snapshots | GUI-007 Run Snapshot Export; GUI-008 Run Snapshot Restore; PRJ-017 Run Snapshot Portability |

## 6. Canonical Graph Subset Exchange Patterns

Most interface payloads exchange one of these canonical graph subsets:

- `CG-S0`: full canonical graph object
- `CG-S1`: structure and interface topology subset
- `CG-S2`: trust boundary and crossing subset
- `CG-S3`: STRIDE score and rationale subset
- `CG-S4`: threat and mitigation subset
- `CG-S5`: export transformation subset

## 7. Interface Quality Attributes

Each interface should be verified for:

- schema conformance
- deterministic field presence
- correlation and version metadata continuity
- role and authorization enforcement where applicable
- explicit error signaling with machine-readable codes

## 8. Interface Verification Suites

- Unit contract tests for payload shape and error conditions
- Integration tests for stage handoff continuity and gate sequencing
- E2E tests for user workflows and export interoperability
- Governance checks for traceability of decisions and artifact lineage

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Satisfies

_None recorded._ <!-- [Req-ID] — rationale -->

### Realizes

_None recorded._ <!-- [Cap-ID] — rationale -->

### Provides / Requires

_None recorded._ <!-- Provides: [Interface-ID]; Requires: [Interface-ID] -->

### Implemented By

_None recorded._ <!-- [src/path/file.py] :: [ClassName.method] -->

### Depends On

_None recorded._ <!-- [element or artifact path] — dependency rationale -->
