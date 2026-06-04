# Traceability Governance Operating Model

## Purpose

Define one consistent policy for traceability artifacts across all decomposition levels:

- requirement sources
- architecture and design anchors
- implementation anchors
- executable verification anchors
- sprint-time normalization and remediation artifacts

## Relationship Taxonomy

This table is the authoritative reference for all traceability relationship names used across capabilities, requirements, architecture, design, implementation, test, and evidence artifacts.

| Relationship | Direction | From | To | Canonical Name | Required In |
|---|---|---|---|---|---|
| Capability decomposition | top-down | Parent capability | Child capability | **Decomposes into** / **Aggregated from** | Capability_Hierarchy_Baseline.md |
| Requirement allocation | top-down | System or subsystem requirement | Component or detail requirement | **Allocated to** / **Derived from** | Requirement spec Traceability Annex |
| Requirement elaboration | same level | Higher-detail requirement | Same-level requirement that adds detail without changing scope | **Refines** | Requirement spec Traceability Annex |
| Architecture satisfaction | upward | Architecture element or design function | Requirement | **Satisfies** | Function_Hierarchy_Registry.md; design artifacts; Traceability Annex |
| Capability realization | upward | Architecture element | Capability | **Realizes** | Capability_Hierarchy_Baseline.md; Function_Hierarchy_Registry.md |
| Interface provision and consumption | lateral | Component | Interface contract | **Provides** / **Requires** | Multi_Agent_Interface_Control_Document.md; Traceability Annex |
| Implementation | downward | Architecture function or design element | Source code file and symbol | **Implemented by** (from function) / **Implements** (from code) | Function_Hierarchy_Registry.md; 15_End_To_End_Traceability_Attributes_Registry.md |
| Verification | upward | Test case or test step | Requirement | **Verified by** (from requirement) / **Verifies** (from test) | Requirement spec Traceability Annex; 15_End_To_End_Traceability_Attributes_Registry.md |
| Evidence production | downward | Test case | Test artifact: report, log, signed record | **Produces evidence** | 15_End_To_End_Traceability_Attributes_Registry.md Test Artifact ID column |
| Evidence substantiation | upward | Test artifact | Verification objective | **Substantiates** | 15_End_To_End_Traceability_Attributes_Registry.md Test Artifact ID column; distinguishes test existence from test result existence |
| Dependency | lateral | Requirement or design element | Requirement or design element it assumes stable | **Depends on** | Requirement spec Traceability Annex; must be resolved before sprint commitment of the dependent item |
| Conflict | lateral | Requirement | Contradicting requirement | **Conflicts with** | Tracked as a defect; must be resolved before implementation starts; never placed in a governed artifact |

### Relationship Placement Rules

- **Derived from / Allocated to**: recorded in the Traceability Annex of the child document, pointing at the parent.
- **Refines**: recorded in the Traceability Annex of the refining document.
- **Satisfies / Realizes / Provides / Requires / Implemented by**: recorded in the architecture or design artifact annex and in `Requirements/15_End_To_End_Traceability_Attributes_Registry.md` rows.
- **Verified by / Verifies**: recorded in the requirement spec annex (requirement side) and in the test plan or test file header (test side).
- **Produces evidence**: the Test Artifact ID column in `Requirements/15_End_To_End_Traceability_Attributes_Registry.md` carries the substantiation artifact reference.
- **Substantiates**: same column as Produces evidence; the distinction is directional — the test case produces evidence, the artifact substantiates the objective. Both are recorded in the same registry row.
- **Depends on**: recorded in the requirement spec annex; must be resolved before sprint planning commits dependent items.
- **Conflicts with**: never placed in a governed artifact; tracked as a defect requiring resolution before implementation starts.

### Annex Template by Artifact Family

Requirement spec — use these headings in `## Traceability Annex`:

```text
### Derived From
### Allocated To
### Refines
### Satisfied By
### Verified By
### Depends On
```

Architecture or design artifact — use these headings in `## Traceability Annex`:

```text
### Satisfies
### Realizes
### Provides / Requires
### Implemented By
### Depends On
```

Test artifact or test plan section — use these headings:

```text
### Verifies
### Produces Evidence
### Substantiates
```

## Canonical Artifact Roles

| Layer | Canonical Artifact | Allowed Evidence Type | Notes |
|---|---|---|---|
| Requirement source of truth | Requirements/01_Project_Requirements.md, Requirements/02_Interface_Requirements.md, Requirements/03_HITL_Requirements.md, Requirements/10_GUI_Requirements.md, Requirements/13_Runtime_State_And_Input_Contract_Requirements.md, Requirements/06_Project_Administration_Requirements.md, Requirements/14_Prompt_Requirements_Baseline.md, Requirements/04_Traceability_Matrix.md | Requirement text and requirement-level verification intent | Requirement IDs originate here. |
| End-to-end governed chain | Requirements/15_End_To_End_Traceability_Attributes_Registry.md | Source plus architecture/design plus implementation plus executable verification | Release and audit decisions use this table. |
| Active sprint execution planning | Requirements/16_Active_Sprint_Traceability_Matrix.md | Sprint-scoped closure planning and in-flight status | Temporary execution workspace, not the release baseline. |
| Implementation normalization bridge | Requirements/17_Implementation_Trace_Normalization.md | Implementation-anchor normalization only | Transitional bridge used to normalize existing relationships before promotion into Requirements/15_End_To_End_Traceability_Attributes_Registry.md. |
| Historical/transient reconciliation | Requirements/appendices/15_End_To_End_Traceability_Attributes_Registry_Historical_Remediation_Appendix.md | Prior remediation or planning-only chains | Not release-governing unless promoted. |

## Placement Policy

1. New requirement IDs must be added to requirement source files and Requirements/04_Traceability_Matrix.md.
2. New release-governed trace rows must be added to Requirements/15_End_To_End_Traceability_Attributes_Registry.md.
3. Requirements/16_Active_Sprint_Traceability_Matrix.md may track sprint closure sequencing but cannot be the only permanent evidence location.
4. Requirements/17_Implementation_Trace_Normalization.md may only contain implementation-normalization rows and must not contain architecture or verification closure-only content.
5. Any row that remains unresolved for architecture/design or executable verification belongs in the historical appendix until corrected.

## Promotion Workflow

1. Add or update sprint normalization in Requirements/17_Implementation_Trace_Normalization.md if implementation anchors are present but not yet normalized.
2. Add full source-to-evidence row in Requirements/15_End_To_End_Traceability_Attributes_Registry.md with executable verification anchor.
3. Confirm independent review reports no missing implementation or verification leg for the promoted IDs.
4. Remove promoted normalization entries from Requirements/17_Implementation_Trace_Normalization.md at sprint closeout, or mark them as promoted with date and destination row.

## Guardrails

- Requirement IDs are never created first in sprint-only files.
- Verification evidence in governed rows must point to executable test files under Tests/ or test/spec files under source trees.
- Planning and governance markdown references can supplement traceability context but cannot replace executable verification anchors.
- Architecture/design references must resolve to docs/architecture/ or docs/design/ artifacts.

## Review Cadence

- During sprint execution: update Requirements/16_Active_Sprint_Traceability_Matrix.md and Requirements/17_Implementation_Trace_Normalization.md as needed.
- Before release-readiness review: all active rows must be promoted or intentionally retained in appendix with explicit rationale.
- At sprint closeout: reconcile Requirements/17_Implementation_Trace_Normalization.md against Requirements/15_End_To_End_Traceability_Attributes_Registry.md and record promotion status.
