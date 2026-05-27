# Agent 04 — STRIDE Scorer

## Theory of Operation

**What:** Agent 04 assigns STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) severity scores to each data flow, using a 0–5 scale with explicit justifications for each score. This quantifies threat exposure and drives prioritization of which data flows require detailed threat generation.

**When:** Agent 04 executes fourth in the pipeline, immediately after Agent 03 enriches the graph with trust boundary information. STRIDE scores depend on boundary crossing knowledge—data flows crossing trust boundaries typically score higher (3–5) than internal flows. STRIDE scores drive Agent 05's threat generation decisions: only flows scoring 3+ on any STRIDE dimension trigger threat generation.

**Why:** STRIDE scoring converts qualitative architectural assessment (trust boundaries) into quantitative risk metrics that enable downstream prioritization and analyst calibration. Without scores, the threat modeler cannot distinguish high-risk flows from low-risk ones, leading to exhaustive (and often impractical) threat generation on every interface. Additionally, STRIDE scores provide a common language for communicating risk to stakeholders: security teams understand that a score of 4–5 on "Tampering" or "Denial of Service" indicates high likelihood and impact. Justification strings ensure traceability—analysts can see *why* a flow received a particular score and can override via HITL gates if justifications are incorrect or policy has changed.

**How:** The agent executes four steps: **(1) Fetch** — retrieves boundary-enriched canonical graph from Agent 03; validates schema compliance. **(2) Score** — calls LLM with system prompt defining STRIDE 0–5 scoring rubric and guidance (e.g., trust boundary crossings on safety-critical paths typically warrant 3–5; unencrypted flows warrant elevated Tampering scores; flows with no repudiation logging warrant elevated Repudiation scores); LLM independently scores each of the six STRIDE dimensions (S/T/R/I/D/E) for every data flow and provides justification strings. **(3) Apply** — extracts scores and justifications from LLM response; applies to each data flow's `stride` object. **(4) Validate & Emit** — validates that each score is integer 0–5 and each justification is non-empty; rejects schema violations; emits scored graph to Agent 05; annotates flows scoring 4–5 for potential HITL analyst review.

**Who:** Agent 03 produces the boundary-enriched graph. Agent 04 depends on the LLM adapter for scoring logic and rubric guidance. Agent 05 consumes the scored graph and uses scores to determine which flows generate threats. Security analysts and stakeholders use STRIDE scores to understand risk prioritization. HITL gates enable analyst review and recalibration of high-severity scores (4–5) to validate LLM judgment.

## High-Level Interfaces

$2### Input Interfaces

- **Boundary-Enriched Graph** — Output from Agent 03; all data flows include trust boundary crossing status and boundary names
- **STRIDE Rubric Context** — System prompt defining 0–5 severity scale and scoring guidance (trust boundary, safety criticality, protocol type, etc.)

$2### Output Interfaces

- **STRIDE-Scored Graph** — Canonical graph with six scores (S/T/R/I/D/E) and six justification strings per data flow
- **Risk Summary** — Indicates flows scoring 4–5 on any STRIDE dimension (candidates for threat generation)

$2### Internal Processing Interfaces

- **LLM Request/Response** — Prompt contains graph and scoring guidance; response contains scores and justifications for all flows

## Component Pieces and Parts

$2### Graph Fetcher
Retrieves boundary-enriched canonical graph from orchestrator state (produced by Agent 03); validates schema compliance; extracts all data flows for scoring; passes to LLM Prompt Handler.
$2### LLM Prompt Handler
Constructs Agent 04 system prompt (STRIDE 0–5 scoring rubric and guidance: trust boundary crossings, safety criticality, protocol types typically warrant higher scores); builds user prompt containing all data flows with context; sends request to LLM; handles timeouts and retries.
$2### STRIDE Applicator
Extracts six scores (S/T/R/I/D/E) and six justification strings from LLM response; applies to each data flow's `stride` object; ensures all six fields are populated; produces scored graph.
$2### Validation Engine
Validates STRIDE scores: checks that each of S/T/R/I/D/E is integer 0–5; checks that each justification string is non-empty; ensures schema compliance; detects and rejects non-compliant scores with detailed error.
$2### State Emitter
Serializes STRIDE-scored canonical graph; packages into orchestrator state object with timestamp; hands off to orchestrator for Agent 05 processing; annotates flows scoring 4–5 for potential HITL review.

## Trust Boundaries

**LLM Provider Boundary** — Agent sends canonical graph structure with trust boundary data to external LLM; receives six scores per flow from untrusted service; must validate all scores are integers 0–5 and justifications are non-empty before accepting.

**Analyst Calibration Boundary** — High STRIDE scores (4–5) may require analyst review for calibration; LLM scoring is advisory and subject to human override via HITL gate.

## Error Handling

- **Missing Graph** — Validation error; Agent 03 must successfully complete before Agent 04 starts
- **LLM Timeout** — Retries up to 3 times; if all fail, emits error and halts
- **Non-Integer Scores** — Validation engine rejects; returns detailed error indicating which scores are invalid
- **Missing Justifications** — Validation engine detects empty justification strings; rejects with error
- **Calibration Request** — Flows scoring 4–5 marked for optional HITL analyst review (controlled by gate configuration)

## Operational Constraints

- **Timeout** — Default 60 seconds per LLM call; configurable
- **Score Range** — All STRIDE scores must be integers 0–5; string or decimal values rejected
- **Justification Required** — All six justification strings must be non-empty; empty or whitespace-only strings rejected
- **HITL Gate** — Can trigger analyst review and override of high-severity scores (4–5)
