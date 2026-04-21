# Multi-Agent Threat Modeler Requirements Baseline v0.1

Date: 2026-04-20
Status: Draft for review
Requirement format: Noun SHALL Verb

## 1. Scope

This baseline defines:
- Project-level requirements for the overall Threat Modeler.
- Derived component requirements for each pipeline agent and core services.
- Interface requirements for module-to-module and human-to-system interactions.
- Initial traceability from project requirements to component requirements.

## 2. Project-Level Requirements (System Requirements)

PRJ-001: Threat Modeler SHALL ingest free-text architecture descriptions and tabular data-flow inputs in a single analysis run.

PRJ-002: Threat Modeler SHALL produce a canonical threat-model graph as the authoritative run artifact.

PRJ-003: Threat Modeler SHALL execute a deterministic multi-agent pipeline with auditable stage boundaries.

PRJ-004: Threat Modeler SHALL validate every stage output against a defined schema before downstream processing.

PRJ-005: Threat Modeler SHALL perform trust-boundary analysis, STRIDE scoring, threat generation, mitigation mapping, STIX packaging, diagram generation, and report generation for each completed run.

PRJ-006: Threat Modeler SHALL support human-in-the-loop approval, edit, and override gates at defined decision points.

PRJ-007: Threat Modeler SHALL maintain immutable run history with who, what, when, and why metadata for all analyst edits.

PRJ-008: Threat Modeler SHALL support configurable model-provider selection through configuration without source-code changes.

PRJ-009: Threat Modeler SHALL allow deployment in offline-only mode and policy-approved hybrid mode.

PRJ-010: Threat Modeler SHALL provide retrieval-augmented evidence references for generated threats and mitigations when knowledge bases are enabled.

PRJ-011: Threat Modeler SHALL produce exportable outputs for canonical JSON, STIX 2.1, Mermaid diagrams, and final markdown report.

PRJ-012: Threat Modeler SHALL enforce role-based permissions for author, reviewer, and approver actions.

PRJ-013: Threat Modeler SHALL support incremental model enrichment without destructive overwrite of previously approved data.

PRJ-014: Threat Modeler SHALL provide selective re-run from an analyst-selected stage after approved edits.

PRJ-015: Threat Modeler SHALL fail safely by halting downstream execution when critical validation errors are detected.

## 3. Component Requirements (Derived)

### 3.1 Orchestrator and State Management

CMP-ORCH-001: LangGraph Orchestrator SHALL route execution through all enabled agents using explicit next-state transitions. Derived from PRJ-003.

CMP-ORCH-002: LangGraph Orchestrator SHALL persist checkpoints after each stage transition. Derived from PRJ-003 and PRJ-007.

CMP-STATE-001: State Store SHALL version canonical graph snapshots per run and per stage. Derived from PRJ-002 and PRJ-007.

CMP-STATE-002: State Store SHALL preserve analyst-approved baselines as non-editable history entries. Derived from PRJ-007 and PRJ-013.

CMP-STATE-003: Validation Layer SHALL block stage handoff on schema failure and emit structured error records. Derived from PRJ-004 and PRJ-015.

### 3.2 Agent 1 Input Normalizer and Graph Builder

CMP-A01-001: Agent 1 SHALL transform raw text and table inputs into canonical graph structures without introducing unsupported fields. Derived from PRJ-001 and PRJ-002.

CMP-A01-002: Agent 1 SHALL assign deterministic identifiers to new systems, subsystems, components, and data flows. Derived from PRJ-002 and PRJ-013.

CMP-A01-003: Agent 1 SHALL mark unknown trust-boundary status explicitly when source data is insufficient. Derived from PRJ-005 and PRJ-015.

### 3.3 Agent 2 Hierarchical Context Builder

CMP-A02-001: Agent 2 SHALL merge new submissions into existing canonical graphs without deleting existing approved elements. Derived from PRJ-013.

CMP-A02-002: Agent 2 SHALL record merge-conflict notes for analyst review when contradictory source claims are detected. Derived from PRJ-006 and PRJ-007.

### 3.4 Agent 3 Trust Boundary Validator

CMP-A03-001: Agent 3 SHALL evaluate each data flow for trust-boundary crossing status using configured policy rules. Derived from PRJ-005.

CMP-A03-002: Agent 3 SHALL emit trust-boundary review flags for human approval when confidence is below policy threshold. Derived from PRJ-006 and PRJ-015.

### 3.5 Agent 4 STRIDE Scorer

CMP-A04-001: Agent 4 SHALL assign STRIDE severity scores for each data flow using the configured scoring scale. Derived from PRJ-005.

CMP-A04-002: Agent 4 SHALL provide concise justification text for each STRIDE dimension score. Derived from PRJ-005 and PRJ-010.

CMP-A04-003: Agent 4 SHALL preserve analyst-overridden scores and associated rationale metadata. Derived from PRJ-006 and PRJ-007.

### 3.6 Agent 5 Concrete Threat Generator

CMP-A05-001: Agent 5 SHALL generate concrete threats for flows meeting configured risk trigger criteria. Derived from PRJ-005.

CMP-A05-002: Agent 5 SHALL attach threat taxonomy references where available, including ATT&CK, CAPEC, and CWE identifiers. Derived from PRJ-010.

CMP-A05-003: Agent 5 SHALL emit likelihood and impact values for each generated threat. Derived from PRJ-005.

### 3.7 Agent 6 STIX Packager

CMP-A06-001: Agent 6 SHALL transform approved threat artifacts into a valid STIX 2.1 bundle. Derived from PRJ-005 and PRJ-011.

CMP-A06-002: Agent 6 SHALL include stable object identifiers and relationship links for generated STIX entities. Derived from PRJ-011.

### 3.8 Agent 7 Mitigation Generator

CMP-A07-001: Agent 7 SHALL map each approved threat to technical and administrative controls based on configured control frameworks. Derived from PRJ-005.

CMP-A07-002: Agent 7 SHALL assign residual-risk estimates after proposed controls. Derived from PRJ-005.

CMP-A07-003: Agent 7 SHALL include rationale linking control selections to threat mechanics. Derived from PRJ-010.

### 3.9 Agent 8 Diagram Generator

CMP-A08-001: Agent 8 SHALL generate Level 0, Level 1, and selected Level 2 Mermaid diagrams from canonical graph data. Derived from PRJ-005 and PRJ-011.

CMP-A08-002: Agent 8 SHALL render trust boundaries and risk severity overlays using configured visual conventions. Derived from PRJ-005 and PRJ-011.

CMP-A08-003: Agent 8 SHALL preserve deterministic node and edge identifiers across regenerations for unchanged structures. Derived from PRJ-014.

### 3.10 Agent 9 Human Report Writer

CMP-A09-001: Agent 9 SHALL generate a formal markdown report containing executive summary, scope, boundaries, findings, mitigations, and residual risk sections. Derived from PRJ-005 and PRJ-011.

CMP-A09-002: Agent 9 SHALL reference approved diagrams, threats, and controls from current run artifacts only. Derived from PRJ-007 and PRJ-011.

CMP-A09-003: Agent 9 SHALL produce report outputs suitable for downstream document conversion workflows. Derived from PRJ-011.

### 3.11 Model Provider Abstraction

CMP-LLM-001: Model Adapter SHALL select active model provider and model name from runtime configuration. Derived from PRJ-008.

CMP-LLM-002: Model Adapter SHALL support policy-constrained model allowlists by deployment mode. Derived from PRJ-008 and PRJ-009.

CMP-LLM-003: Model Adapter SHALL support future provider additions without agent contract changes. Derived from PRJ-008.

### 3.12 HITL and Audit Services

CMP-HITL-001: HITL Service SHALL pause execution at configured approval gates and await explicit analyst decision. Derived from PRJ-006.

CMP-HITL-002: HITL Service SHALL support approve, reject, edit, and re-run actions at each gate according to role permissions. Derived from PRJ-006 and PRJ-012.

CMP-HITL-003: Audit Service SHALL record before-and-after diffs for all analyst edits. Derived from PRJ-007.

CMP-HITL-004: Audit Service SHALL prevent silent mutation of approved artifacts outside tracked workflows. Derived from PRJ-007 and PRJ-013.

## 4. Interface Requirements

INT-001: Parser Interface SHALL accept normalized text payloads and table payloads in structured request format.

INT-002: Agent Input Interface SHALL receive canonical graph payload, run metadata, and stage context for each invocation.

INT-003: Agent Output Interface SHALL return canonical graph payload and stage result status in a schema-valid structure.

INT-004: Validation Interface SHALL return pass or fail result with machine-readable error codes and locations.

INT-005: Orchestrator Interface SHALL expose stage transition events with stage name, timestamp, and correlation identifier.

INT-006: HITL Decision Interface SHALL accept analyst decision objects containing action, rationale, actor, and role.

INT-007: Re-Run Interface SHALL accept stage restart requests and resume execution from selected stage with preserved run context.

INT-008: Visualization Interface SHALL provide read access to graph nodes, flows, boundaries, threats, mitigations, and evidence references.

INT-009: Visualization Edit Interface SHALL submit proposed changes as typed patch operations rather than direct artifact overwrite.

INT-010: STIX Export Interface SHALL output a standards-conformant STIX 2.1 bundle artifact with validation result metadata.

INT-011: Report Export Interface SHALL output markdown report artifact and structured section index.

INT-012: Provider Configuration Interface SHALL accept provider name, model name, mode, and policy profile settings.

INT-013: Security Interface SHALL enforce role-based authorization checks before any edit, approve, or release action.

INT-014: Audit Retrieval Interface SHALL return immutable change history for a selected run and artifact.

## 5. HITL Stage Requirements

HITL-001: Threat Modeler SHALL provide Scope Confirmation Gate after context merge completion.

HITL-002: Threat Modeler SHALL provide Trust Boundary Approval Gate after trust-boundary validation.

HITL-003: Threat Modeler SHALL provide STRIDE Calibration Gate after STRIDE scoring.

HITL-004: Threat Modeler SHALL provide Threat Plausibility Gate after threat generation.

HITL-005: Threat Modeler SHALL provide Mitigation Adequacy Gate after mitigation generation.

HITL-006: Threat Modeler SHALL provide Final Release Gate before report and STIX publication.

HITL-007: Threat Modeler SHALL require rationale entry for analyst overrides at all gates.

HITL-008: Threat Modeler SHALL preserve gate decisions as signed run records.

## 6. Initial Traceability Matrix (Project to Component)

- PRJ-001 traces to CMP-A01-001, INT-001.
- PRJ-002 traces to CMP-STATE-001, CMP-A01-001, INT-002, INT-003.
- PRJ-003 traces to CMP-ORCH-001, CMP-ORCH-002, INT-005.
- PRJ-004 traces to CMP-STATE-003, INT-004.
- PRJ-005 traces to CMP-A03-001, CMP-A04-001, CMP-A05-001, CMP-A06-001, CMP-A07-001, CMP-A08-001, CMP-A09-001.
- PRJ-006 traces to CMP-HITL-001, CMP-HITL-002, HITL-001 through HITL-006, INT-006.
- PRJ-007 traces to CMP-STATE-002, CMP-HITL-003, CMP-HITL-004, INT-014.
- PRJ-008 traces to CMP-LLM-001, CMP-LLM-003, INT-012.
- PRJ-009 traces to CMP-LLM-002, INT-012.
- PRJ-010 traces to CMP-A04-002, CMP-A05-002, CMP-A07-003, INT-008.
- PRJ-011 traces to CMP-A06-001, CMP-A08-001, CMP-A09-001, INT-010, INT-011.
- PRJ-012 traces to CMP-HITL-002, INT-013.
- PRJ-013 traces to CMP-A02-001, CMP-STATE-002, CMP-HITL-004.
- PRJ-014 traces to CMP-A08-003, INT-007.
- PRJ-015 traces to CMP-STATE-003, CMP-A03-002.

## 7. Verification Method Recommendations

Each requirement should be tagged in the next revision with one or more verification methods:
- Test: verified by automated or manual test case
- Analysis: verified by design or data analysis
- Inspection: verified by artifact review
- Demonstration: verified by operational run-through

## 8. Next Requirements Engineering Steps

1. Approve this baseline and lock requirement ID namespace.
2. Decide mitigation data model placement and update all affected requirements.
3. Add acceptance criteria per requirement with objective pass conditions.
4. Add verification ownership and planned verification milestone.
5. Generate component specification sheets from this baseline for implementation tickets.
