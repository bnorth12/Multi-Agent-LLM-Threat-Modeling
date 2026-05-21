# Agent 03 — Trust Boundary Validator

## Theory of Operation

**What:** Agent 03 evaluates each data flow in the canonical graph to determine whether it crosses a security or safety trust boundary, enriching the graph with explicit boundary crossing flags and boundary names that become the foundation for subsequent threat analysis.

**When:** Agent 03 executes third in the pipeline, after Agent 02 completes graph merging. Its output (boundary classifications) is consumed by Agent 04 (STRIDE Scorer), which uses boundary crossings to calibrate severity scores. Trust boundary assessment must occur before STRIDE scoring because boundary crossings are inherently high-risk areas warranting elevated threat scrutiny.

**Why:** Trust boundaries are the fundamental security perimeter in system threat modeling. Identifying where data crosses security or safety domain boundaries is essential for understanding attack surface and risk concentration. Without explicit boundary classification, the threat modeler cannot prioritize which data flows and interfaces warrant detailed threat generation. Boundary crossing identification is also critical for compliance frameworks (e.g., separation of safety-critical and non-safety-critical domains in aerospace systems) and for architecture review—showing which interfaces require special controls (encryption, authentication, failsafes).

**How:** The agent executes four steps: **(1) Fetch** — retrieves merged canonical graph from Agent 02; validates schema compliance. **(2) Analyze** — calls LLM with system prompt defining trust boundary rules (e.g., different security enclaves = crossing, unencrypted cross-domain flow = crossing, safety-critical to non-safety-critical interface = crossing); LLM evaluates each data flow and provides boundary crossing decisions and descriptive boundary names. **(3) Enrich** — applies LLM decisions to each data flow: sets `trust_boundary_crossing` (boolean true/false) and sets `trust_boundary_name` (descriptive string) for all crossing=true entries. **(4) Validate & Emit** — validates that every flow has a boolean crossing flag and that all crossing=true flows have non-empty boundary names; rejects schema violations; emits enriched graph to Agent 04.

**Who:** Agent 02 produces the merged graph. Agent 03 depends on the LLM adapter for boundary classification logic and policy context (enclave definitions, encryption standards, safety criticality levels). Agent 04 consumes the boundary-enriched graph and uses boundary crossings to calibrate STRIDE scores. HITL gates may request analyst review and override of boundary classifications for calibration or policy adjustments.

## High-Level Interfaces

$2### Input Interfaces

- **Merged Canonical Graph** — Output from Agent 02; contains all subsystems, components, and data flows with metadata
- **Trust Boundary Rules Context** — System prompt parameters defining boundary classification logic (enclaves, encryption, safety levels, etc.)

$2### Output Interfaces

- **Boundary-Enriched Graph** — Canonical graph with `trust_boundary_crossing` (boolean) and `trust_boundary_name` (string) populated for all data flows
- **Validation Status** — Indicates whether all flows successfully evaluated; boundary crossing decisions valid

$2### Internal Processing Interfaces

- **LLM Request/Response** — Prompt contains graph definition and boundary rules; response contains updated data flows with crossing decisions

## Component Pieces and Parts

$2### Graph Fetcher
Retrieves merged canonical graph from orchestrator state (produced by Agent 02); validates schema compliance; extracts all data flow entries for boundary analysis; passes to LLM Prompt Handler.
$2### LLM Prompt Handler
Constructs Agent 03 system prompt (trust boundary evaluation rules: different enclaves, encryption requirements, safety-criticality levels); builds user prompt containing all data flows with context; sends request to LLM; handles timeouts and retries.
$2### Boundary Enricher
Extracts trust boundary crossing decisions from LLM response; applies decisions to each data flow: sets `trust_boundary_crossing` (boolean true/false) and sets `trust_boundary_name` for crossing=true entries; produces enriched graph.
$2### Validation Engine
Validates enriched graph: checks that `trust_boundary_crossing` is a JSON boolean (not string) for every flow; checks that all crossing=true flows have non-empty `trust_boundary_name`; ensures schema compliance; rejects non-compliant graphs.
$2### State Emitter
Serializes boundary-enriched canonical graph; packages into orchestrator state object with timestamp; hands off to orchestrator for Agent 04 processing.

## Trust Boundaries

**LLM Provider Boundary** — Agent sends canonical graph structure (includes component names and interface definitions) to external LLM; receives trust boundary classification decisions from untrusted service; must validate boolean types and non-empty names before accepting.

**Policy Boundary** — Trust boundary classification logic is based on input system policies (enclave definitions, encryption requirements); if policy context is incorrect or missing, LLM decisions may be inaccurate; marked for HITL analyst review.

## Error Handling

- **Missing Graph** — Validation error; Agent 02 must successfully complete before Agent 03 starts
- **LLM Timeout** — Retries up to 3 times; if all fail, emits error and halts
- **Invalid Boundary Decisions** — Validation engine detects non-boolean crossing values or missing boundary names; detailed error emitted
- **Low-Confidence Decisions** — If LLM indicates low confidence in boundary crossing decision, marked for HITL analyst review

## Operational Constraints

- **Timeout** — Default 60 seconds per LLM call; configurable
- **Trust Boundary Crossing** — Must be boolean (true/false); string values rejected
- **Boundary Name** — Required for all crossing=true flows; empty names rejected
- **HITL Gate** — Can trigger analyst review of boundary assignments for calibration or override
