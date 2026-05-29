# Canonical Graph Hierarchical Visualization and Structured Editing Concept

Date: 2026-05-29
Status: Draft architecture concept
Related GitHub issues: #93, #94, #95, #85

## 1. Purpose

Define the target architecture for analyst-first canonical graph interaction, combining:

- Hierarchical visualization as a deterministic projection of canonical graph authority.
- Structured, schema-aware stage-output editing at HITL checkpoints.
- Controlled revision loops that preserve governance, traceability, and reproducibility.

## 2. Scope and Boundaries

In scope:

- Canonical-to-visual projection contracts and graph navigation behavior.
- Graph-to-editor deep links for node, edge, and boundary classes.
- Stage-output structured editing policies and impact-class governance.
- Integration touch points with interactive LLM revision loops.

Out of scope:

- Replacing canonical graph as source of truth.
- Free-form raw JSON editing as primary analyst workflow.
- Redefining existing stage semantics for agent_01 through agent_09.

## 3. Current-State Validation Against Implementation

Current architecture baseline is aligned with implemented behavior:

- Runtime authority and lifecycle management are centered in `backend/run_manager.py` with orchestrator execution and checkpoint handling.
- Sequential stage planning remains explicit in `orchestrator.py` via `build_langgraph_execution_plan` and planned stage IDs.
- Canonical graph authority and schema validation behavior are represented in `validation.py` and stage-level validator paths.
- Artifact generation/export pathways for canonical JSON, Mermaid, STIX, and report are present in `exports/` and UI/API export surfaces.
- Analyst-facing runtime components in React include gate control, execution progress, pipeline config, and artifact inspection components.

Validated deltas from current baseline to target architecture:

- No dedicated visual projection layer that maps canonical graph to stable render model with explicit deep-link identities.
- No structured editor contract for controlled field-level graph updates across stage outputs.
- No formal impact-assessment service that decides local acceptance versus required partial/full re-cycle.

## 4. End-State Intent

The end-state architecture introduces a governed analyst interaction loop:

1. Canonical graph remains source-of-truth and validation anchor.
1. Projection service emits deterministic visual model with stable IDs.
1. Analyst actions on visual elements deep-link into schema-aware structured editor.
1. Edit impact is classified and enforced as local validate or pipeline re-cycle.
1. HITL records preserve decision rationale, revision provenance, and replayability.

## 5. Hierarchical Visualization Model

The visualization model must support uneven maturity depth without losing graph integrity.

Required levels:

- System-of-systems
- System
- Subsystem
- Component
- Interface and data-flow realization
- Function-level and implementation-context attachments

Required rendering characteristics:

- Expand/collapse and focus navigation with context retention.
- Directed multi-edge flow support between identical endpoints.
- Boundary overlays for trust, security, and safety crossings.
- Integrity signals for orphaned nodes/flows and unresolved relationships.
- Deterministic node and edge identity for diff and reproducible review.

## 6. Graph-to-Structured-Editor Navigation

Each graph element class shall map to an editor contract:

- Node selection maps to entity editor forms (system/subsystem/component/function).
- Edge selection maps to interface and flow endpoint editor forms.
- Boundary marker selection maps to boundary-crossing attributes and rationale fields.

Structured editor design requirements:

- Schema-aware forms with typed controls and constraints.
- Relationship integrity checks prior to commit.
- Explicit validation feedback before persistence.
- Impact preview prior to apply for edits with potential threat/mitigation consequences.

## 7. Stage-Output Editing Governance

Stage-output editing is controlled under HITL governance, not ad hoc mutation.

Edit classes:

- Low impact metadata edits: local validation and audit append only.
- Medium impact topology-adjacent edits: local validation plus targeted downstream recompute candidate.
- High impact structural edits: mandatory orchestrator re-cycle path with gate re-approval.

Minimum governance controls:

- Edit intent declaration and rationale.
- Pre- and post-edit diff snapshot.
- Attribution and timestamping in run evidence.
- Replay-safe event sequencing for resumed runs.

## 8. Relationship to Agent Pipeline and HITL Revision Loops

Pipeline contracts remain centered on agent_01 to agent_09 execution outputs.

Integration principles:

- #93 owns interactive LLM revision loop behavior at gates.
- #94 owns structured stage-output editing UX and validation contracts.
- #95 owns visual projection, hierarchy navigation, and graph-to-editor linkage.
- #85 should track architecture-diagram and baseline documentation synchronization as these capabilities mature.

### 8.1 Issue-to-Section Mapping

| Issue | Primary focus in this document | Key sections |
| --- | --- | --- |
| #93 | HITL interactive LLM revision-loop integration and governance boundaries | 1, 2, 7, 8, 10 |
| #94 | Structured stage-output editing contracts and validation controls | 1, 2, 6, 7, 10 |
| #95 | Deterministic hierarchical visualization projection and graph navigation | 1, 2, 4, 5, 6, 9, 10 |
| #85 | Architecture baseline and diagram synchronization as implementation evolves | 3, 8, 10 |

## 9. Canonical Schema and Service Contract Considerations

Potential schema/service additions to evaluate:

- Stable projection identifiers for graph elements and cross-level lineage.
- Optional visualization hints that do not affect analysis semantics.
- Edit impact metadata and re-cycle recommendation fields.
- Cross-level summary references for abstraction mapping.
- Audit payload schemas for structured editing actions.

## 10. Delivery Phasing and Sprint Fit

Sprints 13 and 14 should focus on architecture-safe prework only:

- Finalize projection and structured editor contracts.
- Publish trade study criteria and scoring template.
- Add validation-only scaffolding for impact classification.

Deferred beyond S14 (implementation-heavy scope):

- Full interactive hierarchical viewer with deep-link navigation.
- Full structured editing UI for all canonical classes.
- Full re-cycle orchestration with partial recompute optimization.

## 11. Open Questions

1. What is the minimum MVP class set for graph deep-link targets at gates?
1. Which edit types may safely remain local without re-running threat generation stages?
1. Where should projection integrity checks execute first: validator path or projection service path?
1. What cycle-over-cycle diff primitives are required for audit acceptance?
1. Which lineage fields are mandatory for deterministic branch-level decomposition tracking?
