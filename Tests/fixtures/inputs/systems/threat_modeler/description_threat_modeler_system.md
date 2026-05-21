# Multi-Agent Threat Modeler System

The Multi-Agent Threat Modeler is a system-of-systems designed to perform automated threat modeling of aerospace and defense systems using a multi-stage LLM-driven pipeline with human-in-the-loop validation gates. The system transforms unstructured and tabular system architecture inputs into threat-enriched canonical threat model graphs and exportable artifacts (STIX bundles, Mermaid diagrams, and markdown reports).

## System Overview

The threat modeler ingests two types of user inputs:
1. **ICD CSV** — Interface Control Document describing system entities (subsystems, components) and data flows
2. **Markdown Narrative** — Natural-language description of system architecture, components, and operational context

The system processes these inputs through a nine-stage pipeline:
- **Stages 01–06 (Core Threat Analysis)** — Parse, normalize, merge hierarchies, validate trust boundaries, score STRIDE severity, generate threats, and package into STIX
- **Stages 07–09 (Post-Processing)** — Generate mitigations, create diagrams, and produce human-readable reports

## System Segments

### Segment 1: Input Ingestion

Responsible for parsing operator-provided files and canonicalizing them into structured graph representations.

**Components:**
- **CSV/Markdown Parser** — Reads uploaded ICD CSV and narrative markdown; produces intermediate JSON
- **Graph Canonicalizer** — Transforms intermediate JSON into canonical threat graph with deterministic entity IDs and relationship linking

**Key Interfaces:**
- Accepts HTTP multipart uploads from Streamlit UI
- Outputs canonical graph JSON to orchestrator

### Segment 2: Threat Analysis Pipeline

The core multi-agent pipeline that enriches canonical graphs with trust boundary analysis, STRIDE scoring, threat generation, and optional mitigation mapping.

**Components:**
- **Agent Orchestrator** — LangGraph state machine coordinating execution of 9 agents with stage sequencing and validation gate enforcement
- **Agent 01 (Input Normalizer)** — Converts raw text and tables into canonical JSON (schema-compliant; no unsupported fields)
- **Agent 02 (Context Builder)** — Merges new submissions into existing graphs non-destructively; tracks merge conflicts
- **Agent 03 (Trust Boundary Validator)** — Evaluates each data flow for trust boundary crossing; enriches boundary metadata
- **Agent 04 (STRIDE Scorer)** — Assigns 0–5 severity scores (S/T/R/I/D/E) with justifications for each data flow
- **Agent 05 (Threat Generator)** — Generates concrete threats for flows scoring 3+ on any STRIDE dimension; includes MITRE ATT&CK/CAPEC/CWE mappings
- **Agent 06 (STIX Packager)** — Transforms approved threats into valid STIX 2.1 bundle with identity, attack-pattern, and relationship objects

**Key Interfaces:**
- State objects passed between agents via memory/IPC
- LLM provider calls for each agent's LLM-driven analysis
- HITL gate requests/responses for analyst approvals
- Audit log and state persistence after each stage

### Segment 3: LLM Provider Interface

Abstraction layer providing vendor-agnostic LLM access with support for multiple providers and fixture (offline) mode.

**Components:**
- **LLM Adapter** — Generic provider interface (OpenAI-compatible, Grok XAI, fixture mock)
- **Model Configuration Manager** — Selects provider, model, and endpoint without source-code changes

**Key Interfaces:**
- Accepts LLM provider selection and credentials from configuration
- Sends prompts to external LLM provider (or fixture mode)
- Receives structured JSON responses (threats, STIX objects, mitigations, diagrams, reports)

**Trust Boundaries:**
- **LLM Provider Boundary** — Separates threat modeler from external LLM services; all prompts and responses cross this boundary

### Segment 4: Output Packaging

Transforms threat analysis results into exportable, operator-consumable artifacts.

**Components:**
- **STIX Exporter** — Packages threats into STIX 2.1 JSON bundles with standardized threat objects and relationships
- **Diagram Generator** — Creates Mermaid flowchart diagrams showing system architecture, trust boundaries, and threat relationships
- **Report Generator** — Produces comprehensive markdown reports with executive summary, findings, and mitigation tables

**Key Interfaces:**
- Consumes canonical graph with threat/mitigation annotations from pipeline
- Exports artifacts to file system (STIX JSON, Mermaid markdown, report markdown)
- Sends download links to Streamlit UI

### Segment 5: Human-In-The-Loop Control System

Enforces analyst validation gates at configurable pipeline stages with approval, override, and edit capabilities.

**Components:**
- **HITL Gate Manager** — Pauses pipeline at configured stages and waits for analyst decision
- Supports approval, rejection, and override paths
- Captures analyst rationale for audit trail

**Key Interfaces:**
- Receives gate requests from orchestrator
- Presents UI prompts to analyst (threat review, boundary confirmation, severity calibration)
- Returns approval decision or override to orchestrator

### Segment 6: State and Audit

Maintains immutable canonical graph versions, stage state snapshots, and complete edit audit trail.

**Components:**
- **Audit Logger** — Records all stage transitions, HITL approvals, analyst edits, and state changes with full provenance
- **State Manager** — Persists canonical graph and intermediate stage states with versioning; supports run rollback

**Key Interfaces:**
- Receives audit events from orchestrator and HITL gates
- Receives state snapshots after each agent stage
- Supports historical state retrieval and analyst edit tracing

### Segment 7: Streamlit User Interface

Web-based dashboard for run initiation, monitoring, diagnostics, and manual artifact review.

**Components:**
- **Run Dashboard** — Primary interface for file upload, run execution, stage progress monitoring, and artifact download
- **Diagnostics Panel** — Secondary interface for real-time pipeline logs, adapter status, and performance metrics
- **Heartbeat Monitor** — Visual indicator of pipeline liveness (10-second timeout; age display)

**Key Interfaces:**
- Accepts file uploads (ICD CSV, Markdown narrative) from operator
- Displays real-time run status and stage progress
- Provides artifact downloads (STIX, diagrams, reports)
- Shows diagnostics logs and heartbeat age

## Trust Boundaries

### Primary Trust Boundaries

1. **User / System Boundary** — Operators upload files via HTTP; threat modeler must validate input schema and size limits
2. **LLM Provider Boundary** — Threat modeler sends prompts to external LLM service; responses are untrusted until validated
3. **Analyst / System Boundary** — HITL gates accept analyst decisions; decisions must be audited and cannot override validation failures without explicit approval
4. **Storage / System Boundary** — State and audit logs persisted to file system; file integrity and permissions must be enforced

### Internal Boundaries (Optional but Recommended)

1. **Pipeline / HITL Boundary** — HITL decisions should not be bypassed; stage state must be preserved across gates
2. **Audit / State Boundary** — Audit logs are append-only; state versioning must allow rollback only via explicit analyst action

## Data Flows and Sensitivity

### High-Sensitivity Flows (Risk Score 4–5)

- **LLM-001 / LLM-002** — Requests and responses with external LLM provider (trust boundary crossing; credentials and prompts may include system architecture details)
- **PARSE-001** — Intermediate ICD/narrative JSON (contains system architecture before canonicalization; parser must handle untrusted input)

### Medium-Sensitivity Flows (Risk Score 2–3)

- **State objects between agents** — Intermediate threat analysis state (contains evolving threat definitions; must not be tampered mid-pipeline)
- **HITL requests and approvals** — Analyst decisions (must be audited; cannot be replayed or spoofed)

### Low-Sensitivity Flows (Risk Score 0–1)

- **Artifact downloads** — STIX, diagrams, reports (already sanitized; intended for distribution)
- **Diagnostics queries** — Logs and metrics (non-critical status information)

## Data Storage and Retrieval Paths

The threat modeler uses explicit storage and retrieval paths during normal operation:

1. **Prompt Store Path**
	- Orchestrator retrieves stage prompt templates and expected output patterns before each agent run.
	- Prompt editor writes analyst-approved prompt revisions and keeps per-agent prompt history.

1. **State Store Path**
	- Orchestrator persists canonical graph snapshots after each stage transition.
	- Resume operations retrieve latest persisted state plus paused gate metadata for continuity.

1. **Run Metadata Store Path**
	- Orchestrator writes run status, current stage, heartbeat age, and pause gate markers.
	- Run dashboard retrieves this metadata to render timeline, gate state, and diagnostics counters.

1. **Artifact Store Path**
	- STIX exporter, diagram generator, and report writer write generated artifacts to artifact storage.
	- UI artifact viewers retrieve selected artifact content by run ID and artifact type.

## Object Catalog (Explicit JSON Contracts)

The system treats persisted and exchanged JSON structures as first-class object contracts,
not just implicit interface payloads. The following objects are versioned and validated.

1. **FrameworkStateSnapshot**
	- **Owner:** State Manager
	- **Produced by:** Agent Orchestrator after each stage and gate transition
	- **Consumed by:** Agent Orchestrator during resume and historical run reload
	- **Purpose:** Canonical graph plus stage outputs, pause markers, and state version

1. **RunRecord**
	- **Owner:** Run Metadata Store
	- **Produced by:** Agent Orchestrator
	- **Consumed by:** Run Dashboard and timeline views
	- **Purpose:** Run identity, status, timestamps, pause gate, and heartbeat age

1. **GateDecision**
	- **Owner:** Audit Logger
	- **Produced by:** HITL Gate Manager
	- **Consumed by:** Governance/audit review flows
	- **Purpose:** Decision action, actor, rationale, and timestamp

1. **ThreatDecision**
	- **Owner:** Audit Logger
	- **Produced by:** Reviewer actions from UI threat workflows
	- **Consumed by:** Threat review reload and governance evidence
	- **Purpose:** Threat disposition and review notes persistence

1. **PromptRevision**
	- **Owner:** Prompt Store
	- **Produced by:** Prompt editor and stage default initialization
	- **Consumed by:** Stage execution prompt assembly in orchestrator
	- **Purpose:** Prompt versioning, expected outputs, and tuning parameters

1. **ArtifactRecord**
	- **Owner:** Artifact Store
	- **Produced by:** STIX exporter, diagram generator, report writer
	- **Consumed by:** Artifact viewer tabs and download endpoints
	- **Purpose:** Artifact type, checksum, producer stage, and content pointer

1. **RunSummaryDTO / StageStatusDTO / GateDTO**
	- **Owner:** Backend API Projection Mapper
	- **Produced by:** Projection mapper from persisted backend objects
	- **Consumed by:** GUI components through backend API boundary
	- **Purpose:** Stable GUI-safe projections decoupled from internal object schema

These object contracts are explicitly versioned to avoid schema drift between the
separable GUI subsystem and backend logic subsystem.

## External LLM Host and Model Flows

The LLM interface is represented as two explicit boundaries:

1. **LLM Host Boundary**
	- LLM adapter sends authenticated API requests to external provider host gateway.
	- Host gateway returns normalized response envelopes and request IDs to adapter.

1. **LLM Model Boundary**
	- External host gateway routes requests into upstream model runtime.
	- Model runtime returns completion text plus token usage and finish reason.

These boundaries are modeled separately so trust-boundary analysis can distinguish provider host/API risks from model runtime/response risks.

## Optional Retrieval and RAG Section

The following retrieval path is optional and can be enabled for evidence-grounded runs.
If disabled, core pipeline execution remains unchanged.

1. **Corpus Ingestion and Embedding Path**
	- Approved references are ingested and chunked by the RAG ingestor.
	- Embedding adapter generates vectors for each chunk.
	- Vectors and metadata are upserted into the vector store.

1. **Retrieval and Citation Path**
	- Stage-specific query text is sent to retriever for top-k similarity search.
	- Retriever receives evidence snippets with source IDs and scores.
	- Retriever appends citations and evidence context to stage prompt payload before LLM invocation.

1. **Optional Embedding Trust Boundary**
	- When using an external embedding endpoint, embedding requests cross an explicit embedding-provider trust boundary.
	- Local embedding mode avoids this external boundary and keeps embedding operations in-system.

## Operational Constraints

1. **LLM Timeout** — Default 60-second timeout per LLM call; configurable up to 1800 seconds for complex prompts
2. **Heartbeat Monitoring** — 10-second timeout; if orchestrator fails to send heartbeat, UI displays "age" warning
3. **HITL Approval Window** — Paused stages remain paused until analyst explicitly approves or overrides
4. **Artifact Retention** — STIX bundles, diagrams, and reports retained in run history for audit trail

## Integration Points

- **External LLM Providers** — Grok XAI (live), OpenAI-compatible endpoints, Ollama, local fixture mode
- **User Interface** — Streamlit framework with plotly/pandas for visualization
- **Export Formats** — STIX 2.1 JSON, Mermaid markdown, threat model markdown reports
- **Parser Input** — CSV ICD (RFC 4180 compliant), Markdown narratives (CommonMark compliant)

## Threat Model Scope

This threat model applies to the threat modeler system itself, not the systems being modeled by operators. The threat model evaluates:

- **Input validation** risks (malformed ICD CSV, oversized narratives)
- **LLM integration** risks (credential exposure, response manipulation, timeout vulnerabilities)
- **Pipeline integrity** risks (HITL bypass, state tampering, stage skipping)
- **Output manipulation** risks (artifact tampering after generation)
- **Audit trail** risks (log deletion, analyst decision repudiation)
