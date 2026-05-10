# Multi-Agent Threat Modeler Tool

The Multi-Agent Threat Modeler (MTM) is a distributed system that applies STRIDE threat analysis, mitigation generation, and artifact packaging to user-provided system architectures. The tool orchestrates a nine-stage agent pipeline, coordinates human-in-the-loop approval gates, and exports threat models in multiple formats (canonical JSON, STIX 2.1, Mermaid diagrams, and human-readable reports).

## Input Management Subsystem

Users upload system architectures via two complementary input channels:

1. **ICD Parser**: Accepts CSV/XLSX files in a flat entity-per-row format. Rows specify subsystems, components, and data flows (interfaces). The parser validates referential integrity (all parent IDs exist) and extracts hardware/software module affiliations, trust boundary crossings, and protocol details.

2. **Narrative Loader**: Accepts markdown or plain text descriptions that provide system context, risk posture, regulatory constraints, and architectural rationale. These narratives are used by downstream agents to refine threat scoring and mitigation recommendations.

## Agent Orchestration Subsystem

The orchestration subsystem manages the nine-stage threat modeling pipeline:

- **Stage 1** (Agent 01): Input Normalizer – validates ICD and narrative inputs, harmonizes data models
- **Stages 2–3** (Agents 02–03): Context Building & Trust Boundary Validation – constructs hierarchical system model, identifies and validates trust boundaries
- **Stage 4** (Agent 04): STRIDE Scorer – applies STRIDE categories to each component and data flow, scores severity
- **Stage 5** (Agent 05): Concrete Threat Generator – generates specific, actionable threats and attack scenarios
- **Stage 6** (Agent 06): STIX Packager – encodes threats into STIX 2.1 intelligence bundles
- **Stage 7** (Agent 07): Mitigation Generator – recommends security controls and mitigations
- **Stage 8** (Agent 08): Diagram Generator – produces Mermaid architecture and threat flow diagrams
- **Stage 9** (Agent 09): Report Writer – compiles human-readable executive threat analysis report

The Pipeline Manager maintains a canonical threat model state (the "canonical graph") that flows through all stages. Each agent reads from and writes to this graph, preserving provenance and enabling branching analysis.

## LLM Runtime Subsystem

The LLM Runtime provides configurable language model services. The tool supports multiple providers:

- **OpenAI Adapter**: Integrates with GPT-4 and GPT-3.5-turbo via OpenAI API (chat_completions endpoint). Includes retry logic (exponential backoff) for transient API failures.
- **xAI Adapter**: Integrates with Grok-4 models via xAI API (also chat_completions-compatible). Supports multi-agent and reasoning model variants.

The LLM Router selects the appropriate provider and model based on user configuration. All API calls include timeout and retry semantics to handle provider transience (429, 5xx) gracefully.

## Human-in-the-Loop Subsystem

The HITL subsystem enforces structured approval gates at critical pipeline stages:

- **Gate 0** (Input Validation): User confirms ICD structure and narrative accuracy
- **Gate 1** (Scope & Boundaries): User validates trust boundary identification
- **Gate 2** (Threat Summary): User reviews high-level threats before detailed analysis
- **Gate 3** (Threat Details): User approves specific threat scenarios
- **Gate 4** (Mitigations): User reviews and customizes mitigation recommendations
- **Gate 5** (Diagram Review): User validates visual representation of architecture and threats
- **Gate 6** (Report Readiness): User confirms report quality before export
- **Gate 7** (Export Validation): User validates artifact consistency across formats

Each gate can pause the pipeline, log audit decisions, and allow users to request re-analysis or corrections. Gate states (pause, resume, accept) are persisted in the audit log for compliance.

## Export Subsystem

The Export subsystem transforms the canonical threat model into four output formats:

1. **Canonical Graph Exporter**: JSON representation conforming to canonical_json_schema.json. Includes all entities, interfaces, threats, mitigations, and provenance metadata.

2. **STIX Exporter**: Generates STIX 2.1 (Structured Threat Information Expression) bundles compatible with threat intelligence platforms and SOCs. Encodes threat objects, attack patterns, and relationships.

3. **Mermaid Diagram Generator**: Produces two complementary Mermaid diagrams:
   - System architecture diagram (components, subsystems, interfaces)
   - Threat flow diagram (STRIDE categories, vulnerable data flows, attacker paths)

4. **Report Writer**: Generates executive-level markdown report with sections for system overview, threat summary, high-priority findings, mitigation roadmap, and compliance recommendations.

## User Interface Subsystem

The UI is built with Streamlit and provides three primary screens:

1. **Configuration Screen (SCR-003/012/013/014)**:
   - Upload system architecture (ICD CSV/XLSX)
   - Upload narrative description (markdown/text)
   - Select LLM provider and model
   - Configure pipeline behavior (gate enforcement, output formats)
   - Set execution parameters (timeout, retry policy)

2. **Execution Monitor (SCR-005/006)**:
   - Real-time pipeline execution status (current stage, agent progress)
   - Gate notifications and approval workflows
   - Audit trail of user decisions and system actions
   - Logs and error messages for troubleshooting

3. **Results Display (SCR-007/008/009/010)**:
   - Download canonical JSON graph
   - Download STIX intelligence bundle
   - Display embedded Mermaid diagrams
   - Download formatted markdown report

## Trust Boundaries

### User Trust Boundary

The boundary between the User Workstation and the MTM deployment. All user-provided input files (ICD CSV, narrative markdown) and downloaded outputs (JSON exports, STIX bundles, reports) cross this boundary. All data must be validated on entry and signed/encrypted on export to prevent tampering or exfiltration.

### External LLM API Boundary

The boundary between the MTM service and external language model providers (OpenAI, xAI). All API calls and responses are encrypted via TLS. API keys must be stored securely (environment variables, secrets manager). Rate limiting and request/response logging must be implemented to prevent API key exfiltration or model prompt injection attacks.

## Data Integrity & Provenance

All data flowing through the pipeline is versioned and timestamped. The canonical graph includes:
- Entity IDs and versions
- Agent execution sequence and timestamps
- User decisions at each HITL gate
- LLM provider and model used for each analysis stage
- Format conversion checksums (for artifact consistency validation)

This enables traceability, audit compliance, and forensic analysis if tool output is called into question.
