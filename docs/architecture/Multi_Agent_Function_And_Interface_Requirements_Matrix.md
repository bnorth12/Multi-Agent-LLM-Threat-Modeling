# Multi-Agent Function and Interface Requirements Matrix

## 1. Purpose

Provide architecture-level traceability from decomposed functions and interfaces to project, interface, and GUI requirement authorities.

Functional requirements are expected to appear as one or more functions in the decomposition hierarchy. Interfaces and ICDs capture the data flows and boundary paths that connect those functions.
Interface functions are treated as first-class functions in the matrix because boundary behavior often carries the primary requirement obligation across internal, external, and user-facing interfaces.

## 2. Functional Requirements Coverage Matrix

This matrix uses requirement identifiers together with requirement names so that readers can understand coverage intent without constantly switching over to the `Requirements/` package.

| Architecture Function ID | Function Name | Primary Requirement Coverage | Interface IDs |
|---|---|---|---|
| F210 | Input Payload Validation | PRJ-001 Unified Input Ingestion; PRJ-027 ICD Source Compliance Validation; INT-001 Parser Request Contract; INT-004 Validation Result Contract | INTF-I-001, INTF-E-001 |
| F220 | Canonical Initialization | PRJ-002 Canonical Graph Authority; PRJ-004 Stage Validation Gate; PRJ-026 Inter-Agent Handoff Integrity | INTF-I-001, INTF-I-002 |
| F230 | Context Enrichment | PRJ-005 Full Threat Workflow; PRJ-026 Inter-Agent Handoff Integrity | INTF-I-002 |
| F240 | Trust Boundary Validation | PRJ-005 Full Threat Workflow; PRJ-015 Fail-Safe Halting; INT-004 Validation Result Contract | INTF-I-002, INTF-I-003 |
| F250 | STRIDE Scoring | PRJ-005 Full Threat Workflow; INT-002 Agent Input Contract; INT-003 Agent Output Contract | INTF-I-002 |
| F260 | Threat Construction | PRJ-005 Full Threat Workflow; PRJ-010 Evidence-Linked Outputs; PRJ-026 Inter-Agent Handoff Integrity | INTF-I-002 |
| F270 | Mitigation Construction | PRJ-005 Full Threat Workflow; PRJ-010 Evidence-Linked Outputs | INTF-I-002 |
| F280 | STIX Packaging | PRJ-011 Export Artifact Set; INT-010 STIX Export Contract; GUI-018 STIX Threat Model Viewer | INTF-E-004 |
| F290 | Diagram Construction | PRJ-011 Export Artifact Set; GUI-020 Mermaid Diagram Viewer; GUI-034 Mermaid Multi-Diagram Review Workspace | INTF-E-005 |
| F300 | Report Composition | PRJ-011 Export Artifact Set; INT-011 Report Export Contract; GUI-025 Markdown Viewer and Editor | INTF-E-006 |
| F310 | Gate Decision Enforcement | PRJ-006 HITL Governance; PRJ-028 Orchestrator Gate Enforcement and Resume Control; INT-006 HITL Decision Contract; GUI-002 HITL Gate Screens | INTF-I-004, INTF-U-002 |
| F320 | Run State Management | PRJ-019 Asynchronous Backend State Authority; PRJ-029 Live Run Liveness Fail-Closed; GUI-003 Pipeline Status Dashboard; GUI-016 Backend Runtime State Projection; GUI-027 Run Diagnostics Panel | INTF-I-005, INTF-U-003 |
| F330 | Prompt Configuration Management | PRJ-018 Agent Prompt Configurability; PRJ-030 Prompt Store Authority and Fail-Closed Loading; GUI-009 Agent Prompt Editor; GUI-010 Agent Prompt Version History | INTF-I-006, INTF-U-005 |
| F340 | Snapshot and Evidence Management | PRJ-017 Run Snapshot Portability; PRJ-021 Component Semantic Version Authority; PRJ-022 Component File Version Traceability; GUI-007 Run Snapshot Export; GUI-008 Run Snapshot Restore; GUI-024 Component and File Version Visibility | INTF-I-007, INTF-U-006 |

## 3. Interface Requirements Coverage Matrix

| Interface ID | Interface Class | Requirement Coverage | Verification Focus |
|---|---|---|---|
| INTF-I-001 | Internal | INT-001 Parser Request Contract; INT-002 Agent Input Contract; PRJ-001 Unified Input Ingestion; PRJ-027 ICD Source Compliance Validation | source normalization and provenance completeness |
| INTF-I-002 | Internal | INT-002 Agent Input Contract; INT-003 Agent Output Contract; INT-005 Stage Event Contract; PRJ-026 Inter-Agent Handoff Integrity | stage handoff integrity and correlation continuity |
| INTF-I-003 | Internal | INT-004 Validation Result Contract; PRJ-004 Stage Validation Gate; PRJ-015 Fail-Safe Halting | validation failure signaling and block behavior |
| INTF-I-004 | Internal | INT-006 HITL Decision Contract; PRJ-006 HITL Governance; PRJ-028 Orchestrator Gate Enforcement and Resume Control | gate action contract and rationale capture |
| INTF-I-005 | Internal | PRJ-019 Asynchronous Backend State Authority; PRJ-029 Live Run Liveness Fail-Closed; GUI-016 Backend Runtime State Projection; GUI-027 Run Diagnostics Panel | runtime coherence and liveness observability |
| INTF-I-006 | Internal | PRJ-018 Agent Prompt Configurability; PRJ-030 Prompt Store Authority and Fail-Closed Loading; GUI-009 Agent Prompt Editor; GUI-010 Agent Prompt Version History | prompt authority and rollback behavior |
| INTF-I-007 | Internal | PRJ-017 Run Snapshot Portability; GUI-007 Run Snapshot Export; GUI-008 Run Snapshot Restore | snapshot portability and state reconstitution |
| INTF-E-001 | External | PRJ-001 Unified Input Ingestion; PRJ-027 ICD Source Compliance Validation; GUI-001 Input Entry Form | source file format and structural compliance |
| INTF-E-002 | External | INT-012 Provider Config Contract; INT-015 Model Connection Contract; PRJ-008 Configurable Model Selection; GUI-012 Model Provider Selection Screen; GUI-013 Model Connection Details Configuration; GUI-014 Model Connection Validation | provider configuration and connection validation |
| INTF-E-003 | External | PRJ-011 Export Artifact Set; INT-011 Report Export Contract; GUI-006 Results Export Interface | canonical JSON export integrity |
| INTF-E-004 | External | PRJ-011 Export Artifact Set; INT-010 STIX Export Contract; GUI-018 STIX Threat Model Viewer | STIX validity and metadata completeness |
| INTF-E-005 | External | PRJ-011 Export Artifact Set; GUI-020 Mermaid Diagram Viewer; GUI-034 Mermaid Multi-Diagram Review Workspace | diagram rendering and source consistency |
| INTF-E-006 | External | PRJ-021 Component Semantic Version Authority; PRJ-022 Component File Version Traceability; GUI-015 Token Usage Telemetry Dashboard and Export; GUI-024 Component and File Version Visibility | release evidence and version traceability |
| INTF-U-001 | User | PRJ-016 Analyst Graphical Interface; GUI-001 Input Entry Form | complete and valid analyst input workflow |
| INTF-U-002 | User | PRJ-006 HITL Governance; PRJ-028 Orchestrator Gate Enforcement and Resume Control; GUI-002 HITL Gate Screens; GUI-032 Input Integrity Preflight Review Gate; GUI-033 Post-Stage-1 Normalization Review Gate | governed decision workflow enforcement |
| INTF-U-003 | User | PRJ-019 Asynchronous Backend State Authority; PRJ-029 Live Run Liveness Fail-Closed; GUI-003 Pipeline Status Dashboard; GUI-017 Live Mode Failover Hard-Stop Visibility; GUI-026 Run Liveness Telemetry; GUI-027 Run Diagnostics Panel | operator runtime visibility and fail-closed feedback |
| INTF-U-004 | User | GUI-018 STIX Threat Model Viewer through GUI-025 Markdown Viewer and Editor; GUI-041 Header-Authoritative Artifact Domain Navigation; GUI-042 Header Review and Export Icon Entry Points | artifact inspection and export usability |
| INTF-U-005 | User | PRJ-018 Agent Prompt Configurability; PRJ-030 Prompt Store Authority and Fail-Closed Loading; GUI-009 Agent Prompt Editor; GUI-010 Agent Prompt Version History | controlled prompt edits and history |
| INTF-U-006 | User | PRJ-017 Run Snapshot Portability; GUI-007 Run Snapshot Export; GUI-008 Run Snapshot Restore | snapshot export and restore workflow |

## 4. Coverage Gaps and Follow-On Requirement Actions

Potential follow-on requirement additions to formal `Requirements/` set:

- explicit architecture-level requirements for canonical subset exchange classes (`CG-S0` through `CG-S5`)
- explicit control-loop requirements for validation feedback and runtime integrity monitoring
- explicit interface performance and timeout requirements for provider and export interfaces

Until promoted into `Requirements/`, these remain architecture guidance and should be enforced via design reviews and test strategy updates.
