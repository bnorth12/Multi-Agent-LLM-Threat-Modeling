# Agent 05 — Threat Generator

## Theory of Operation

**What:** Agent 05 generates concrete, actionable threat statements for data flows that score high (3+) on any STRIDE dimension. Each threat includes name, description, MITRE ATT&CK technique identifiers, CAPEC and CWE references, and likelihood/impact ratings, enabling downstream operators and security analysts to understand specific attack mechanics and risk.

**When:** Agent 05 executes fifth in the pipeline, immediately after Agent 04 assigns STRIDE scores. Its output (populated threat objects) is consumed by Agent 06 (STIX Packager), which exports threats into standardized STIX 2.1 bundles. Threat generation must occur after STRIDE scoring because only flows scoring 3+ warrant the computational cost and LLM calls needed for detailed threat derivation.

**Why:** STRIDE scores quantify risk but do not describe *how* that risk manifests. A score of "4 on Tampering" indicates high risk of data modification, but operators need concrete threat scenarios (e.g., "Adversary performs man-in-the-middle attack to inject false position data") and attack frameworks (MITRE ATT&CK, CAPEC, CWE) to mount effective defenses. Additionally, threat generation forces technical specificity: abstract risks are reframed as concrete attack paths with named techniques, enabling security teams to search threat intelligence, map to existing controls, and prioritize mitigations. Likelihood and impact ratings provide a risk scoring framework for analyst calibration and stakeholder communication.

**How:** The agent executes four steps: **(1) Fetch & Filter** — retrieves STRIDE-scored canonical graph from Agent 04; identifies all data flows scoring 3+ on any STRIDE dimension (S/T/R/I/D/E). **(2) Contextualize** — extracts threat context for each high-risk flow: trust boundary names, source and destination component functions, interface protocols, data items carried, and STRIDE justifications. **(3) Generate** — calls LLM with system prompt defining threat generation rules (plausible for aerospace/ICS contexts; must reference MITRE ATT&CK, CAPEC, CWE; likelihood and impact 1–5) and user prompt containing high-risk flows with context; LLM produces concrete threat scenarios. **(4) Validate & Emit** — validates threat objects (non-empty name/description, valid taxonomy IDs, likelihood/impact integers 1–5); populates threats array in each qualifying flow; rejects schema violations; emits threat-populated graph to Agent 06.

**Who:** Agent 04 produces the STRIDE-scored graph. Agent 05 depends on the LLM adapter for threat synthesis and on access to threat taxonomy databases (MITRE ATT&CK, CAPEC, CWE). Agent 06 consumes the threat-populated graph and packages threats into STIX bundles. Security analysts use threat names, descriptions, and taxonomy references to understand attack surface. HITL gates may request analyst review of generated threats for accuracy, relevance, and completeness.

## High-Level Interfaces

$2### Input Interfaces

- **STRIDE-Scored Graph** — Output from Agent 04; all data flows include STRIDE scores (S/T/R/I/D/E) with justifications
- **Threat Generation Rules Context** — System prompt parameters defining plausible aerospace/ICS threat scenarios and taxonomy requirements

$2### Output Interfaces

- **Threat-Populated Graph** — Canonical graph with threat objects (name, description, MITRE ATT&CK, CAPEC, CWE, likelihood, impact) populated in the `threats` array of high-risk flows (3+ score)
- **Validation Status** — Indicates which flows generated threats; taxonomy mapping success; anomalies flagged for analyst review

$2### Internal Processing Interfaces

- **LLM Request/Response** — Prompt contains high-risk flows with STRIDE context; response contains threat object arrays per flow

## Component Pieces and Parts

$2### Graph Fetcher
Retrieves STRIDE-scored canonical graph from orchestrator state (produced by Agent 04); analyzes STRIDE scores; filters to identify all flows scoring 3+ on any dimension; extracts threat context for each qualifying flow.
$2### Context Analyzer
Extracts threat-generation context for each high-risk flow: trust boundary names, source and destination component names, interface protocols, data items, STRIDE scores and justifications; assembles context into structured format for LLM consumption.
$2### LLM Prompt Handler
Constructs Agent 05 system prompt (threat generation rules: plausibility for aerospace/ICS, MITRE ATT&CK mapping, CAPEC/CWE reference requirements, likelihood/impact 1–5 scale); builds user prompt containing high-risk flows with context; sends request to LLM; handles timeouts and retries.
$2### Threat Generator
Extracts threat objects from LLM response; for each threat: validates name (non-empty), description (non-empty), MITRE ATT&CK techniques (array of strings), CAPEC ID (string), CWE ID (string), likelihood (integer 1–5), impact (integer 1–5); maps threats to source flows; populates `threats` array in each qualifying flow.
$2### Validation Engine
Validates threat objects: checks that all required fields are present and non-empty; validates MITRE IDs follow expected format (T-prefixed); validates likelihood/impact are integers 1–5; ensures schema compliance; rejects non-compliant threats with detailed error.
$2### State Emitter
Serializes threat-populated canonical graph; packages into orchestrator state object with timestamp; hands off to orchestrator for Agent 06 processing; annotates flows with generated threats for HITL analyst review (optional).

## Trust Boundaries

**LLM Provider Boundary** — Agent sends high-risk flow context (component names, interface definitions, STRIDE context) to external LLM; receives threat descriptions from untrusted service; must validate all taxonomy IDs and numeric ranges before accepting.

**Threat Accuracy Boundary** — LLM-generated threats may be incomplete, irrelevant, or technically inaccurate for specific system domains; marked for optional HITL analyst review and refinement.

## Error Handling

- **Missing or Invalid STRIDE Scores** — Validation error; Agent 04 must successfully complete and pass schema-compliant graph
- **LLM Timeout** — Retries up to 3 times; if all fail, emits error and halts
- **Non-JSON Threat Response** — Retries LLM call; if response remains non-JSON, emits error
- **Invalid Taxonomy IDs** — Validation engine detects non-standard MITRE/CAPEC/CWE IDs; marked for analyst review or rejected
- **Out-of-Range Likelihood/Impact** — Validation engine detects values <1 or >5; rejects with error

## Operational Constraints

- **Score Filter** — Only flows scoring 3+ on any STRIDE dimension generate threats; flows scoring ≤2 emit empty threats array
- **Timeout** — Default 60 seconds per LLM call; configurable
- **Threat Taxonomy** — MITRE ATT&CK, CAPEC, CWE references must be valid; invalid IDs rejected
- **HITL Gate** — Can trigger analyst review of generated threats for accuracy or additional threat scenarios
