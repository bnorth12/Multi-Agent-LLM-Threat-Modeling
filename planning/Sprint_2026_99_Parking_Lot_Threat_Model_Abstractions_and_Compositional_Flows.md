# Parking Lot 2026-99 Concept Review: Threat Model Abstractions and Compositional Flows

**Date**: 2026-05-21
**Status**: Parking Lot Concept Collection
**Source Conversation**: https://grok.com/share/bGVnYWN5LWNvcHk_3e5001c7-2448-4dc8-849a-7e219f843647

---

## 1. Review Purpose

This review captures the concept baseline from the linked chat and translates it into concrete gaps for the canonical threat model.

Primary objective:
- Ensure the canonical graph can represent System-of-Systems hierarchy, compositional data-flow abstractions, and low-level realizations where true attack surfaces exist.
- Define Parking Lot 2026-99 as the holding lane for a retrieval-aligned concept
	database (RAG) that links abstractions, protocol wrappers, threats, and
	mitigations.

Planning posture for Parking Lot 2026-99:
- This lane is currently a concept collection and research backlog, not a committed
	sprint execution plan.
- Formal sprint planning is expected only after explicit portfolio activation and capacity review.

---

## 2. Concept Baseline (From Reviewed Chat)

The reviewed concept defines a hierarchical, safety-critical System-of-Systems (SoS):
- Aircraft system
- Ground maintenance and logistics system
- Ground flight planning system
- Satellite communications path between ground and aircraft

Core modeling principles from the source:
- High-level flows are logical/compositional abstractions.
- Real flows exist at lowest-level interfaces (buffers, packets, IPC, bus frames, RF/physical).
- One high-level flow decomposes into many lower-level flows.
- Threading model concerns (many-to-one, one-to-one, many-to-many) belong primarily at node/computer level.
- OSI layer semantics are important for threat placement and propagation.
- Protocol wrappers carry abstractions between layers and are often where
	authentication, integrity, confidentiality, and anti-replay controls are
	implemented.

---

## 3. Canonical Model Coverage Check

Current canonical artifact baseline example: [exports_for_manual/canonical_graph.json](exports_for_manual/canonical_graph.json)

### 3.1 Currently Represented

- System metadata
- Subsystems
- Components
- Functions (component scoped)
- Interfaces
- STRIDE scores per interface
- Threats and mitigations per interface

### 3.2 Missing or Under-Represented Concepts

1. SoS-level hierarchy and independent collaborating systems
- Missing explicit entities for SoS root and peer systems.

2. Processing node/computer level between subsystem and component
- Missing explicit node layer for host/platform runtime context.

3. Thread and execution model representation
- No representation of thread model semantics or scheduling context for component execution.

4. Compositional flow decomposition
- Missing parent-child relationships between abstract flows and concrete realized flows.

5. Abstraction-level typing on flows
- No first-class tag for abstraction level (logical, protocol, frame, physical, IPC, memory).

6. Realization traceability
- Missing links from abstract flow to concrete assets/interfaces that realize it.

7. Cross-layer trust boundaries
- Boundaries exist on interfaces but not as reusable entities across hierarchy and OSI layers.

8. OSI-layer mapping
- No normalized field to locate threat exposure by OSI layer/hop.

9. Protocol stack reuse across heterogeneous links
- No model for same logical flow traversing different physical/protocol implementations.

10. Threat propagation across decomposition tree
- No explicit graph edges for propagating impact from low-level exploit to high-level mission flow.

11. Protocol wrapper and control anchoring model
- No first-class representation of wrapper stacks (headers, envelopes,
  sessions) or direct links from wrappers to implemented security controls and
  mitigations.

12. Retrieval-aligned concept corpus
- No structured knowledge store for concept-to-threat-to-mitigation retrieval
	across abstraction levels and protocol wrappers.

---

## 4. Missing Function Set for Sprint 2026-014

## 4.1 Data Model Functions

1. Add SoS hierarchy entities
- `sos`, `systems[]`, and parent-child relationships.

2. Add node/computer layer
- `processing_nodes[]` with host type, OS/RTOS, firmware context.

3. Add flow decomposition primitives
- `parent_flow_id`, `child_flow_ids[]`, `decomposes_into[]`.

4. Add abstraction typing
- `abstraction_level` enum (for example: `sos_logical`, `system_logical`, `protocol_message`, `frame`, `ipc`, `memory_copy`, `physical_signal`).

5. Add realization links
- `realized_by_assets[]` linking abstract flows to concrete interfaces/components/nodes.

6. Add OSI annotations
- `osi_layer`, `encapsulation_context`, `link_type` on concrete flow segments.

7. Add protocol-wrapper entities
- `protocol_wrappers[]` with wrapper type, layer placement, encapsulates,
	decapsulates, and `implemented_controls[]` fields.

8. Add mitigation-to-wrapper bindings
- `mitigation_anchor` or `enforced_at_wrapper_id` so mitigations can be tied to
	the protocol abstraction where they are applied.

9. Add retrieval indexing metadata
- `concept_tags[]`, `threat_tags[]`, `mitigation_tags[]`,
	`abstraction_path[]`, and `protocol_stack_signature` for RAG indexing.

## 4.2 Analysis Functions

1. Recursive flow expansion
- Expand a high-level flow into concrete leaf flows.

2. Bidirectional trace
- Trace from mission/business flow down to concrete surfaces and back.

3. Threat propagation engine
- Propagate low-level threats to affected higher-level logical flows and mission impacts.

4. Layer-aware STRIDE placement
- Distinguish threat classes by OSI and runtime layer context.

5. Boundary inheritance and override checks
- Compute trust-boundary crossings through decomposition paths.

6. Multi-interface equivalence analysis
- Detect equivalent logical flow realized over different link types/protocols.

7. Wrapper control effectiveness analysis
- Validate that required controls (auth, integrity, encryption, replay
	protection) exist at the wrapper level where the threat is realized.

8. RAG retrieval quality checks
- Evaluate whether a query at any abstraction level can retrieve aligned
	protocol wrappers, relevant threats, and mapped mitigations.

## 4.3 Visualization Functions

1. Collapsible hierarchical DFD view
- SoS -> System -> Subsystem -> Node -> Component -> Function -> Interface -> Concrete flow.

2. Expand Real Flows control
- Show decomposition path from logical flow to concrete leaves.

3. Threat overlay by layer
- Display threats by hierarchy level and OSI layer.

4. Propagation path view
- Show causal chain from exploit surface to mission-level consequence.

5. Wrapper stack security view
- Show protocol wrapper stack per flow segment with mapped mitigations and
	control coverage gaps.

6. RAG trace panel
- Show retrieved concept chunks, source mappings, and abstraction-level
	alignment confidence for analyst review.

---

## 5. Diagram Concepts To Represent (Sprint 2026-014)

The source conversation includes diagrams conceptually covering:
- Thread mapping models (many-to-one, one-to-one, many-to-many)
- Data Flow Graph (DFG) with dependency/parallel branches
- SoS hierarchical decomposition
- Hierarchical flow decomposition (logical to concrete)
- OSI-layered communication abstraction
- Protocol wrapper stack and control insertion points
- Integrated view (threads + flows + OSI)

Required sprint outcome:
- Recreate these as project-owned architecture/threat-model diagrams aligned to canonical schema fields.

### 5.1 Sample Diagram Concepts for Inspiration (Not Final Targets)

Context:
- The current canonical graph is primarily a JSON artifact. S14 should evaluate
	one or more visual views so analysts can reason over structure and risk faster
	(picture-over-text benefit).
- These sample concepts are inspiration references only; no single sample
	currently satisfies the full modeling and analyst-review need.

Candidate concept patterns to combine and evolve:
1. Hierarchy map view
- Tree view from SoS to concrete interfaces/functions showing containment and
	ownership boundaries.

2. Flow decomposition view
- Expand/collapse graph from high-level mission/logical flow to protocol,
	frame, IPC, and physical realizations.

3. Trust-boundary crossing view
- Emphasize where flows cross trust zones and annotate boundary type,
	authentication context, and control expectations.

4. Protocol wrapper stack view
- Layered depiction of encapsulation/decapsulation points with mapped
	mitigations and coverage gaps.

5. Threat and mitigation overlay view
- Overlay STRIDE/threat nodes and mitigation anchors onto hierarchy/flow paths,
	including propagation from concrete exploit to mission impact.

6. Multi-view synchronized analyst workspace
- Linked panels where selecting an element in one view highlights related
	elements in hierarchy, flow, wrapper, and threat/mitigation views.

Selection guidance for post-S13 planning:
- Prioritize views that improve threat traceability, mitigation explainability,
	and HITL review speed.
- Select initial implementation set based on evidence from analyst walkthroughs
	and smoke-test usability.
- Prefer compositional designs that merge strengths from multiple samples,
	instead of adopting any single sample view as-is.

---

## 6. Proposed S14 Concept Candidates (Not Committed Stories Yet)

| Story ID | Story | Deliverable | Evidence |
|---|---|---|---|
| S14-001 | SoS Hierarchy Extension | Canonical schema update for SoS/System/Node layers | Schema diff + sample canonical export |
| S14-002 | Compositional Flow Graph | Parent-child flow decomposition fields and validators | Unit tests for decomposition integrity |
| S14-003 | Abstraction and Realization Tagging | Flow abstraction-level and realized-by links | Validation tests + sample exports |
| S14-004 | OSI and Link Semantics | OSI annotations and protocol-hop representation | Tests for layer completeness |
| S14-005 | Threat Propagation Rules | Propagation from concrete leaves to mission-level impacts | Integration tests with expected paths |
| S14-006 | Hierarchical Visualization | Collapsible view and expand-real-flow behavior | UI snapshots + smoke evidence |
| S14-007 | Cross-Layer Trust Boundaries | Boundary object model and inheritance checks | Boundary-crossing analysis tests |
| S14-008 | Protocol Wrapper Control Anchoring | Wrapper model plus mitigation binding to wrapper enforcement points | Unit tests for wrapper coverage and mitigation linkage |
| S14-009 | RAG Knowledge Base Bootstrap | Concept/protocol/threat/mitigation store with abstraction-aware indexing | Seed dataset, index build logs, retrieval validation tests |

---

## 6.2 Potential Agent Skills for S14 Research and Future Execution

These are candidate skills to shape design and prototyping during concept
collection. They are not yet approved implementation commitments.

Aircraft and architecture threat-research skill candidates:
- `AircraftProtocolIntelligenceSkill`
- `InformationFlowDecompositionSkill`
- `DataExposureClassificationSkill`
- `AerospaceZeroTrustMappingSkill`

Threat-model workflow skill candidates:
- `ThreatHypothesisGenerationSkill`
- `AttackSurfaceScoringSkill`
- `MitigationSynthesisSkill`
- `ThreatPropagationTraceSkill`

RAG and intelligence-integration skill candidates:
- `STIXIngestionNormalizationSkill`
- `AbstractionAwareChunkingSkill`
- `RetrievalOrchestrationSkill`
- `EvidenceProvenanceScoringSkill`

Candidate prompt-orchestration pattern:
- Prompt defines policy intent and gating criteria.
- Skills execute bounded functions with schema-constrained outputs.
- HITL checkpoints validate high-impact threat and mitigation proposals.

---

## 6.1 RAG Bootstrap Concept for Sprint 2026-014

Goal:
- Start a governance-ready knowledge base that supports retrieval by abstraction
  level and protocol context, not just keyword matching.
- Use STIX 2.1 as the normalized interchange layer for external threat
	intelligence and mitigation knowledge where possible.

Minimum schema entities:
- `concept`
- `abstraction_level`
- `flow_segment`
- `protocol_wrapper`
- `threat_pattern`
- `mitigation_control`
- `trace_link` (concept -> wrapper -> threat -> mitigation)
- `stix_object_ref` (source object id/type/version and provenance)

Required alignment keys:
- `abstraction_path`
- `osi_layer`
- `protocol_stack_signature`
- `trust_boundary_id`
- `threat_taxonomy_refs` (for example CAPEC/CWE/MITRE ATT&CK)

External intelligence mapping expectations:
- MITRE ATT&CK techniques and tactics map to `threat_pattern` and propagation
	paths.
- MITRE D3FEND controls map to `mitigation_control` and wrapper enforcement
	anchors.
- CAPEC attack patterns map to canonical threat scenarios and interface abuse
	cases.
- CWE weakness classes map to concrete implementation-level exposure points.
- Additional STIX 2.1 compatible sources can be ingested with the same object
	normalization path.

Initial ingestion sources:
- Canonical graph artifacts
- Threat and mitigation exports
- Protocol wrapper definitions and interface specifications
- Sprint concept documents and approved architecture references
- STIX 2.1 bundles for ATT&CK/D3FEND/CAPEC/CWE-aligned data sources

STIX 2.1 ingestion requirements:
1. Preserve original STIX ids, object types, relationships, and source
	provenance metadata.
2. Normalize relationships into retrieval edges (for example
	technique -> mitigated-by -> control).
3. Support periodic refresh and de-duplication by STIX id and modified date.
4. Maintain mappings from STIX objects to abstraction-level flow segments and
	protocol wrappers.

Initial retrieval acceptance checks:
1. Query from high-level mission flow returns correct lower-level protocol
	wrappers and candidate attack surfaces.
2. Query by protocol wrapper returns mapped threats and enforced mitigations.
3. Query by mitigation control returns associated abstractions and realized flow
	segments.
4. Query by threat returns both abstract impact path and concrete enforcement
	points.
5. Query by ATT&CK technique returns relevant protocol wrappers, impacted
	abstractions, and mapped mitigations (including D3FEND when available).
6. Query by CAPEC or CWE returns aligned threat patterns and candidate control
	sets for affected flow segments.

---

## 7. Governance Review Checklist (Concept Closure)

- [ ] Concept accepted: High-level flows are modeled as abstractions, not physical transfer.
- [ ] Concept accepted: Low-level flows are authoritative attack surfaces.
- [ ] Concept accepted: Canonical model supports recursive decomposition.
- [ ] Concept accepted: OSI and runtime layers are represented for threat placement.
- [ ] Concept accepted: Threat propagation supports both bottom-up and top-down traceability.
- [ ] Concept accepted: SoS hierarchy is explicit and navigable.
- [ ] Concept accepted: Protocol wrappers are represented as abstraction carriers and mitigation enforcement anchors.
- [ ] Concept accepted: RAG concept database bootstrap aligns abstraction levels,
  protocol wrappers, threats, and mitigations for end-to-end retrieval.

---

## 8. Immediate Recommendation

Adopt this document as Sprint 2026-014 concept baseline and treat S14-001
through S14-009 as concept candidates for prioritization during post-S13 sprint
planning. Do not lock scope or commitments until S13 closeout, resourcing, and
entry criteria are approved.

---

## 9. S14 Vector DB Data-Retrieval Gap List and Organization Starter Plan

Purpose:

- Convert the vector-store reference baseline in `docs/references/Vector DB Design.txt`
	into an S14 retrieval backlog that identifies missing data for a complete,
	abstraction-aware concept knowledge base.

### 9.1 Additional Data to Retrieve for a More Complete Set

| Priority | Data Domain | Additional Data Needed | Why Needed for S14 Retrieval Completeness | Target Output |
|---|---|---|---|---|
| P0 | Canonical model lineage | Versioned canonical graph snapshots per sprint/release with stable ids | Enables diff-aware retrieval and provenance-safe trace links | `canonical_graph_YYYY_MM_DD.json` + lineage manifest |
| P0 | Flow decomposition corpus | Explicit parent-child flow decomposition examples from real system models | Required to train/validate abstraction-path retrieval | `flow_decomposition_seed.jsonl` |
| P0 | Protocol wrapper inventory | Structured wrapper definitions (encapsulation, decapsulation, layer, control anchors) | Needed for wrapper-aware threat/mitigation retrieval | `protocol_wrapper_catalog.json` |
| P0 | Threat-to-wrapper mappings | Curated mappings from threat patterns to wrapper enforcement points | Supports wrapper control-gap queries from S14 objectives | `threat_wrapper_mapping.jsonl` |
| P0 | Mitigation enforcement evidence | Control implementation evidence tied to wrapper ids and trust boundaries | Enables retrieval of "what control is enforced where" | `mitigation_enforcement_evidence.jsonl` |
| P1 | STIX normalization bundle | ATT&CK, CAPEC, CWE, D3FEND normalized to shared schema with dedupe keys | Needed for cross-source retrieval consistency | `stix_normalized_bundle.jsonl` |
| P1 | Trust-boundary policy rules | Machine-readable trust-boundary rules and boundary-crossing requirements | Enables policy-constrained retrieval and boundary checks | `trust_boundary_rules.json` |
| P1 | OSI/link semantics coverage | Flow-segment annotations for osi layer, link type, protocol stack signatures | Required for layer-aware threat placement queries | `flow_segment_layer_annotations.jsonl` |
| P1 | Historical threat model slices | Redacted historical reports chunked with concept tags and abstraction paths | Improves retrieval recall for real-world patterns | `historical_reports_chunks.jsonl` |
| P1 | Secure design doctrine corpus | FSAD (Fundamentals of Secure Aerospace Design) concept mappings to abstractions, wrappers, and controls | Adds aerospace-secure-design guidance coverage for retrieval and mitigation rationale | `fsad_concept_control_mapping.jsonl` |
| P1 | Threat-driven design corpus | Lockheed Martin Threat-Driven Approach white paper mappings to threat prioritization and mitigation sequencing patterns | Adds threat-driven decision logic for higher-value retrieval and ranking | `lm_threat_driven_mapping.jsonl` |
| P1 | STRIDE augmentation corpus | STRIDE limitation crosswalk and modern threat category mappings for campaign, identity, supply-chain, control-plane, and mission-impact reasoning | Improves retrieval quality beyond STRIDE-only classification | `stride_modern_category_crosswalk.jsonl` |
| P2 | Validation query set | Analyst-authored gold queries with expected retrieval results | Enables objective retrieval quality testing | `retrieval_acceptance_queries.yaml` |
| P2 | Negative/ambiguity set | Confusable queries and known near-miss examples | Reduces false positives and improves ranking behavior | `retrieval_negative_set.yaml` |

### 9.2 Data Completeness Checklist (S14 Intake Gate)

- [ ] Canonical graph snapshots include stable object ids and source timestamps.
- [ ] Every flow decomposition record has `abstraction_path` and `realized_by_assets`.
- [ ] Every protocol wrapper record includes `implemented_controls` and layer placement.
- [ ] Threat mappings include source taxonomy refs (ATT&CK/CAPEC/CWE/D3FEND as available).
- [ ] Mitigation records include enforceable anchor (`wrapper_id` or equivalent).
- [ ] Trust-boundary ids are consistent across canonical graph, wrappers, and flow segments.
- [ ] Retrieval acceptance and negative test sets exist before index quality sign-off.

### 9.3 Organization Plan (Starter, Governance-Oriented)

Proposed S14 workspace structure:

- `data/vector_db/s14/intake/`
  Includes raw source drops by domain (`attack/`, `capec/`, `cwe/`, `d3fend/`, `canonical/`, `historical/`).
- `data/vector_db/s14/normalized/`
  Includes schema-aligned jsonl artifacts and dedupe outputs.
- `data/vector_db/s14/index/`
  Includes index build manifests, embedding metadata, and collection stats.
- `data/vector_db/s14/validation/`
  Includes retrieval acceptance queries, negative sets, and result reports.
- `data/vector_db/s14/governance/`
  Includes data inventory matrix, provenance ledger, and refresh cadence logs.

### 9.4 Execution Phasing (Initial)

1. Phase A: Intake inventory and provenance capture.
1. Phase B: Normalize and link abstraction/wrapper/threat/mitigation entities.
1. Phase C: Build collections and record index manifests.
1. Phase D: Run retrieval acceptance/negative tests and publish quality report.
1. Phase E: Review HITL/governance gates and approve promotion to active retrieval baseline.

### 9.5 S14 Deliverables to Start Immediately

1. Create a data inventory matrix for the P0/P1 datasets above.
1. Define json/jsonl schemas for wrapper mappings and mitigation enforcement evidence.
1. Produce first `retrieval_acceptance_queries.yaml` from the S14 acceptance checks in this document.
1. Establish weekly refresh and ownership table for each collection domain.
1. Use `docs/references/S14_Reference_Register.md` as the mandatory coverage baseline for IoT, aerospace, and CTI sources.

### 9.6 External Reference Governance Note (FSAD)

- FSAD (Fundamentals of Secure Aerospace Design, Lockheed Martin publication)
	is approved as an S14 design-reference input and should be represented in the
	S14 reference register and retrieval data inventory.
- For implementation, store structured derived mappings (concept/control/abstraction
	links and provenance metadata) rather than redistributing full-source content,
	unless repository distribution rights are explicitly confirmed for full text.
