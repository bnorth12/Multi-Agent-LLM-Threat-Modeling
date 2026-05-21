# Agent 01 — Input Normalizer

## Theory of Operation

**What:** Agent 01 transforms operator-provided ICD CSV files and Markdown narrative descriptions into a canonical threat-model graph JSON structure that serves as the foundation for all downstream threat analysis.

**When:** Agent 01 executes first in the pipeline, immediately after the operator uploads files via the Streamlit UI. It is the only entry point for external system architecture inputs; all subsequent agents depend on its normalized output.

**Why:** Operators provide system models in diverse formats (CSV spreadsheets, markdown narratives) with varying structure and terminology. Agent 01 must canonicalize these heterogeneous inputs into a deterministic graph representation that guarantees all downstream agents receive consistent, schema-compliant data. Without normalization, the pipeline cannot enforce contract validation or trust boundary analysis. Additionally, Agent 01 must reject malformed or adversarial inputs before they reach LLM-based agents, preventing prompt injection and resource exhaustion attacks.

**How:** The agent executes four sequential steps: **(1) Ingest & Validate** — accepts CSV and markdown files; validates against expected schemas; rejects oversized or malformed payloads. **(2) Parse** — transforms CSV rows into entity tuples (subsystems, components, data flows); extracts narrative sections from markdown. **(3) Normalize** — sends parsed inputs to an LLM with a system prompt requesting canonicalization into schema-compliant JSON; the LLM produces a structured canonical graph. **(4) Validate & Emit** — verifies the generated graph against the canonical schema; rejects if unsupported fields are present; passes validated graph to orchestrator state for Agent 02.

**Who:** Operators upload raw ICD and narrative files. Agent 01 depends on the LLM adapter for canonicalization. Downstream agents (Agent 02 through Agent 09) consume Agent 01's output. The HITL gate system may request analyst approval of normalization decisions before handoff to Agent 02.

## High-Level Interfaces

### Input Interfaces

- **ICD CSV File** — RFC 4180 compliant CSV with columns: entity_type (subsystem|component|data_flow), id, name, description, parent, hardware, software_modules, from_node, to_node, protocol, data_items, trust_boundary_crossing, trust_boundary_name
- **Markdown Narrative** — CommonMark-compliant markdown describing system architecture, segments, components, and operational context; first heading (#) is system name
- **LLM Adapter** — Connection to LLM provider (Grok XAI, OpenAI-compatible, or fixture mode) for normalized canonicalization

### Output Interfaces

- **Canonical Graph JSON** — Schema-compliant threat-model graph with system metadata, subsystems, components, functions, and data flows; all entities linked and deterministically identified
- **Error Messages** — Validation failure messages indicating CSV schema errors, LLM timeout, response non-compliance, or schema violations

### Internal Processing Interfaces

- **Parsed Entity Tuples** — Intermediate representation of CSV rows as entity and data-flow tuples (not persisted; used between parser and LLM handler)
- **LLM Request/Response** — Structured JSON prompts sent to LLM and structured JSON responses received (requests include parsed input context; responses must be valid canonical graph JSON)

## Component Pieces and Parts

### File Ingestion Handler

Accepts ICD CSV and Markdown narrative bytes from HTTP multipart upload; performs basic file type and size validation; passes validated bytes to Schema Validator.

### Schema Validator

Validates ICD CSV column headers (entity_type, id, name, description, parent, etc.); validates Markdown format compliance (CommonMark structure, valid headings); rejects inputs that fail validation with detailed error message.

### CSV and Markdown Parser

Transforms validated CSV rows into entity and data-flow tuples; extracts markdown sections (headings, narrative blocks, lists); produces intermediate JSON with parsed entities and narrative metadata for LLM handler.

### LLM Prompt Handler

Constructs Agent 01 system prompt (requesting schema-compliant canonicalization) and user prompt (containing parsed CSV entities and narrative context); sends request to LLM Adapter; handles timeouts and retry logic.

### LLM Adapter Interface

Calls external LLM provider (Grok XAI, OpenAI-compatible endpoint, or offline FixtureAdapter) with prompts; receives structured JSON response; validates response is valid JSON before passing downstream.

### Canonical Graph Builder

Transforms LLM response JSON into canonical graph structure; assigns deterministic IDs; links entities by parent references; constructs System, Subsystem, Component, and DataFlow objects; ensures all required fields are present.

### Output Validator

Validates built canonical graph against canonical schema; checks for unsupported fields, missing required fields, and type mismatches; rejects non-compliant graphs with detailed error message.

### State Emitter

Serializes validated canonical graph JSON; packages it into orchestrator state object with timestamp and metadata; hands off to orchestrator for Agent 02 processing or HITL gate (if enabled).

## Trust Boundaries

**LLM Provider Boundary** — Agent sends parsed system architecture details (component names, interfaces, security context) in LLM prompts; receives untrusted JSON from external LLM service; must validate all responses against schema before accepting.

**Input Boundary** — User-supplied CSV and Markdown files are untrusted; malformed, oversized, or adversarial payloads must be rejected during schema validation and file ingestion phases.

## Error Handling

- **Invalid CSV/Markdown** — Schema validation rejects with error; returns validation failure message to UI; operator resubmits with corrected files
- **LLM Timeout** — Retries up to 3 times; if all attempts fail, emits validation error and halts
- **LLM Response Non-JSON** — Retries LLM call; if response remains non-JSON, emits validation error
- **Schema Violation** — Output validator rejects; detailed error message indicates which fields are missing or invalid

## Operational Constraints

- **Timeout** — Default 60 seconds per LLM call; configurable up to 1800 seconds
- **Fixture Mode** — In offline mode, FixtureAdapter loads pre-computed canonical graph from fixture file instead of calling live LLM
- **HITL Gate** — Stage completion can trigger analyst approval gate before handoff to Agent 02 (controlled by pipeline configuration)
