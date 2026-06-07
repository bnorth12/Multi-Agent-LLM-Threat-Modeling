# Independent Engineering Review Model

## Purpose

This document defines the authoritative model for the **Independent Engineering Review (IER)** of the Multi-Agent Threat Modeler. 

The IER provides a holistic, local-first assessment of the **maturity, health, and quality** of the system's engineering artifacts. It goes beyond simple traceability leg counting to evaluate:

- Actual **documentation relationships** expressed in Traceability Annexes using the INCOSE-aligned taxonomy (from Requirements/18_Traceability_Governance_Operating_Model.md).
- Fidelity of **implementation** to the documented designs, architectures, functions, and capabilities.
- Strength and relevance of **verification** (executable tests, FQT, evidence artifacts) substantiating the claims.
- Correctness and completeness of the **traceability matrices** relative to the underlying engineering reality (or gaps in the engineering artifacts themselves).
- Explicit linkage of **interfaces** (ICDs, data flows, contracts) to the various levels of abstraction in the functional decomposition (L0–L4).

The review produces a single canonical report (Markdown + JSON) that serves as an auditable engineering health snapshot for sprint planning, release readiness, and continuous improvement. It complements (but does not duplicate) CI-enforced checks.

## Guiding Principles

- **Content over presence**: Analyze the *actual text and relationships* in annexes, design documents, code comments/contracts, test cases, and evidence — not just file existence or ID mentions.
- **INCOSE relationships as primary evidence**: Use the canonical names and placement rules from 18_Traceability_Governance_Operating_Model.md (`Satisfies`, `Realizes`, `Provides`/`Requires`, `Implemented By`, `Verified By`, `Produces Evidence`, `Substantiates`, `Depends On`, etc.).
- **Bidirectional auditing**: The review must detect gaps in traceability *and* gaps/inconsistencies in the engineering documentation, implementation, or verification.
- **Abstraction-aware interfaces**: Interfaces must be explicitly mapped to the functional decomposition levels at which they operate.
- **Single source of truth output**: One canonical pair per run context in `independent_reviews/latest/`, with aggressive history compaction.
- **Local-first and independent**: Prioritizes repository artifacts (docs with annexes, src/, Tests/, FQT evidence) over external systems. CI provides fast automated gates; the IER provides deeper, content-rich, human-interpretable engineering insight.
- **Evolution from prior model**: Builds directly on the traceability governance operating model, the populated Traceability Annexes across capability/functional/architecture/design/requirements/test artifacts, and the 15_End_To_End_Traceability_Attributes_Registry.md.

## Engineering Artifact Classes

The IER evaluates the following primary classes of artifacts. Each class has defined governing documents, expected relationships (via annexes), implementation anchors, and verification expectations.

1. **Capability Hierarchy**
   - Governing artifact: `docs/architecture/Capability_Hierarchy_Baseline.md`
   - Key relationships: Decomposes into / Aggregated from, Realizes (by architecture), Satisfied By (by functions/requirements)
   - Evaluation focus: L0/L1/L2 stability, parent-child integrity, linkage to requirements and architecture authority.

2. **Functional Decomposition**
   - Governing artifact: `docs/architecture/Multi_Agent_Functional_Decomposition.md` + `docs/architecture/Function_Hierarchy_Registry.md`
   - Key relationships: Realizes capabilities, Satisfied By (requirements), Implemented By (code/stages), Provides/Requires (interfaces)
   - Levels: L0 (mission), L1 (subfunctions), L2 (system services), L3 (stage/agent/governance), L4 (operational activities)
   - Evaluation focus: Completeness across levels, data-flow consistency, agent/governance function coverage.

3. **Architecture**
   - Governing artifacts: `docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md` + supporting views (structural, logical, functional, data-centric, etc.)
   - Key relationships: Realizes capabilities/functions, Satisfies requirements, Provides/Requires interfaces
   - Evaluation focus: View consistency, alignment with functional decomposition, boundary definitions.

4. **Design**
   - Governing artifacts: `docs/design/software/*` (e.g., Runtime_And_Orchestration, Agent_Subsystem, Export_And_Evidence, Model_Configuration, Prompt_Store...) + `docs/design/system/*` (External_Interface, Functional_Data_Flow, Deployment, backfills)
   - Key relationships: Satisfies architecture/requirements, Implemented By (source), Provides/Requires (detailed contracts)
   - Evaluation focus: Design-to-architecture fidelity, implementation surface coverage, degraded-mode handling.

5. **Requirements**
   - Governing artifacts: `Requirements/0*_*.md`, `Requirements/Components/`, `Requirements/1*_*.md` (project, interface, HITL, GUI, etc.)
   - Key relationships (per annex template): Derived From, Allocated To, Refines, Satisfied By (functions/design), Verified By (tests), Depends On
   - Evaluation focus: Traceability to capability/function, elaboration consistency, interface requirements clarity.

6. **Interfaces & ICDs**
   - Governing artifacts: `docs/architecture/Multi_Agent_Interface_Control_Document.md`, `docs/design/system/Functional_Data_Flow_Design_Traceability_Package.md`, `docs/design/system/External_Interface_And_Integration_Design_Package.md`
   - Key relationships: Provides / Requires (lateral between components), mapped to functional decomposition levels
   - Evaluation focus: Completeness of interface contracts at each abstraction level (L0–L4), data-flow fidelity, trust boundary definitions, integration with canonical graph and external providers.

7. **Implementation**
   - Anchors: `src/threat_modeler/`, `frontend/src/`, key scripts (orchestrator, agents, hitl, llm adapter, run_manager, validation, config, prompt store, etc.)
   - Key relationships: Implements (from design/function), Produces Evidence (via runtime behavior)
   - Evaluation focus: Direct realization of annex claims, contract adherence (input/output, state, handoff), configuration management (prompts, models, providers), runtime integrity (checkpoints, liveness, degraded modes).

8. **Verification & Evidence**
   - Governing artifacts: `Requirements/05_Verification_Strategy.md`, `Tests/Formal_Qualification_Test_Plan.md`, test suites (unit/integration/e2e), `docs/verification/`, FQT archives, execution summaries, evidence packages
   - Key relationships: Verifies (requirements), Produces Evidence / Substantiates (test artifacts), full chain closure in 15_End_To_End registry
   - Evaluation focus: Coverage of functional decomposition levels and interfaces, relevance to threat modeling behaviors (including HITL gates, live vs. fixture, export integrity), evidence freshness and substantiation strength.

9. **Configuration & Supporting Governance Artifacts**
   - Includes: Prompt store, model configuration, runtime state persistence, governance configs (`config/governance_*`, sprint defaults), planning artifacts that drive engineering scope.
   - Evaluation focus: Authority and auditability (e.g., prompt version history, provider validation gating), alignment with design and requirements claims.

## Evaluation Dimensions (per Artifact Class)

For each class the IER produces scores (0–100) and qualitative findings in these dimensions:

- **Completeness**: Does the class fully address its governing higher-level artifact and annex relationships? Are all expected L0–L4 functions, interfaces, or requirements represented?
- **Consistency**: Internal consistency within the class and with peer classes at the same abstraction level (e.g., architecture views align with functional decomposition).
- **Fidelity (Documentation Relationships)**: Strength and correctness of INCOSE relationships expressed in the Traceability Annexes (Satisfies, Realizes, Provides/Requires, Implemented By, etc.). Are the annexes populated with meaningful, bidirectional, evidence-backed entries?
- **Implementation Realization**: Directness and completeness of links from the class into source code, modules, classes, and symbols. Use of contracts, provenance, and fallback behavior.
- **Verification Substantiation**: Quality and relevance of executable evidence (tests, FQT steps, evidence artifacts) that substantiates the claims. Distinguishes existence of tests from meaningful coverage of the documented behaviors, including edge/degraded cases.
- **Interface-to-Functional-Decomposition Mapping** (class-specific or cross-cutting for Interfaces/Design/Functional): Every significant interface/contract must be explicitly linked to the Lx level(s) at which it operates in the decomposition.
- **Traceability Alignment**: How well the class's actual content (annexes, relationships, code, tests) is reflected in (or missing from) the traceability matrices (04, 16, 17, Capability_Function_Architecture_Traceability_Matrix, 15_End_To_End registry). Flags both matrix errors and gaps in the underlying engineering artifacts.

**Cross-Cutting Analyses** (always performed):
- Documentation Relationship Health (depth and accuracy of annex usage across all classes).
- Implementation & Verification Fidelity (end-to-end from capability/function → design → code → test for representative chains).
- Interface Abstraction Coverage (mapping quality across L0–L4).
- Traceability Matrix Audit (correctness: do matrix claims match actual annex/impl/verify content? Completeness: are real relationships missing from matrices? Gaps in engineering itself?).

## Scoring and Overall Health

- Per-class **Maturity Score** (weighted average of the dimensions above, emphasizing fidelity and interface mapping for this model).
- Per-class **Health** (penalties for critical gaps in relationships, missing verification of core behaviors, or matrix drift that obscures reality).
- Per-class **Quality Indicators** (qualitative: clarity of annex entries, evidence of review cycles, use of INCOSE verbs, handling of degraded modes).
- **Overall Engineering Health Score**: Weighted composite across classes (higher weight on Architecture, Design, Interfaces, Functional Decomposition, and Verification because they directly enable the threat-modeling mission).
- Trend deltas, confidence gates (e.g., evidence freshness), and comparison to prior runs.

Findings are classified (critical/major/minor/informational) with explicit references to files, annex sections, code symbols, test cases, and matrix rows.

## Relationship to Existing Governance Artifacts

- **Primary evidence sources**: The Traceability Annexes (populated per the templates in 18_Traceability_Governance_Operating_Model.md), 15_End_To_End_Traceability_Attributes_Registry.md, Function_Hierarchy_Registry.md, Capability_Hierarchy_Baseline.md, design specs, ICD, FQT, and actual source/test artifacts.
- The IER treats the annexes as first-class engineering products and the **primary source of truth** for documentation relationships (INCOSE verbs), not just traceability bookkeeping.
- Matrices (external) are audited *against* the annexes + implementation + verification reality, rather than being the sole source of truth. Going forward, keep annexes current in the engineering docs; matrices can be derived/summary views or periodically synced from annex + source analysis.
- Continues to support single canonical output in `independent_reviews/latest/`, pre-push / on-demand generation, and the known dirty-tree exception for the two review files.
- Complements (does not replace) CI gates (verify scripts, hooks, autoflow). The IER provides the deeper, content-based engineering insight that is difficult to fully automate.

## Execution and Output Expectations

The review is executed via the independent review skill / orchestrator (local Python script + optional agent delegation, per updated SKILL.md and independent-review-orchestrator.agent.md). It must:

- Prioritize local repository content (annex text, code, tests, evidence).
- Produce one canonical Markdown report + JSON for the run context, structured as:
  - Header + Overall Engineering Health Score (legacy health retained for continuity).
  - Executive Summary (holistic, with nod to per-class engineering view).
  - Per-Class Scorecards (one per engineering artifact class: Capability Hierarchy, Functional Decomposition, Architecture, Design, Requirements, Interfaces & ICDs, Implementation, Verification & Evidence, Configuration). Each includes maturity/health/quality indicators, documentation relationship (INCOSE annex) analysis, implementation/verification notes, and interface mapping where relevant.
  - Cross-Cutting Analyses: Documentation Relationship Health, Interface-to-Functional-Decomposition (L0–L4) Mapping, Traceability Matrix Audit (correctness/completeness vs. actual annexes + impl + tests + artifacts; explicit callouts for gaps in the *engineering* itself).
  - Consolidated Findings & Gaps (distinguishing matrix issues from engineering documentation/impl/verification gaps).
  - Trends, Recommendations (engineering improvement focused), and Appendices.
- Explicitly call out interface-to-abstraction (L0–L4) linkages from ICDs, data-flow packages, and annexes.
- Distinguish gaps in traceability matrices from gaps in the actual engineering documentation, implementation, or verification.
- The review script now includes a "Suggested Matrix Row Additions" section (generated from annex + source analysis) to facilitate syncing.
- Remain suitable for sprint planning intake while being useful as a long-term engineering quality record.

This model supersedes the narrower "traceability + remediation readiness" framing for mature phases of the project while preserving the operational discipline (single file, local-first, history compaction, known dirty-tree exception for the two review files) established for the independent review process. The agent and skill have been updated to task for the holistic per-class + cross-cutting engineering analysis.