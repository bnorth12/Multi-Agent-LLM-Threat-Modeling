# Agent 02 — Hierarchical Context Builder

## Theory of Operation

**What:** Agent 02 merges newly canonicalized graphs (from Agent 01) with existing baseline graphs in a non-destructive manner, producing a unified threat model that incorporates new system inputs while preserving all approved entities and explicitly annotating conflicts for analyst review.

**When:** Agent 02 executes second in the pipeline, immediately after Agent 01 completes graph normalization. It operates only if an existing baseline graph exists in persistent storage; in greenfield scenarios (first threat model run), Agent 02 receives Agent 01's graph and passes it through with no modifications. On subsequent runs, Agent 02 ensures incremental threat modeling without data loss.

**Why:** Organizations perform threat modeling iteratively: initial system models are refined, components are added, interfaces change, and analyst approvals are recorded. Agent 02 enables non-destructive merging so that approved threat model elements are never accidentally deleted by subsequent submissions. By explicitly annotating conflicts rather than silently resolving them, Agent 02 preserves analytical provenance and forces conscious analyst decisions on contradictory system definitions. This is critical for regulatory compliance (HITL audit trails) and system safety (preventing silent data loss).

**How:** The agent executes four steps: **(1) Fetch** — retrieves the new canonical graph from Agent 01 and optionally loads an existing baseline graph from persistent storage. **(2) Diff** — analyzes differences between the two graphs; identifies entity additions (new entities), modifications (existing entities with changed properties), and conflicts (contradictory definitions). **(3) Merge** — calls LLM to execute merge rules that preserve all existing entities and IDs, incorporates new entities, and attaches conflict annotations where contradictions exist. **(4) Validate & Emit** — verifies merged graph against schema; ensures all unchanged entity IDs remain stable; emits merged graph with conflict metadata to Agent 03.

**Who:** Agent 01 produces the new canonical graph. Existing threat model runs (and analysts' prior approvals) are represented by the baseline graph in storage. Agent 02 depends on the LLM adapter for merge logic. Agent 03 consumes the merged graph. HITL gates may request analyst review of conflict annotations before proceeding to Agent 03.

## High-Level Interfaces

$2### Input Interfaces

- **New Canonical Graph** — Output from Agent 01; contains parsed and canonicalized system entities and relationships
- **Existing Baseline Graph** — Optional graph from persistent storage representing approved and versioned threat model state
- **Merge Context** — Detected differences (new entities, modified properties, conflicting definitions) passed to LLM

$2### Output Interfaces

- **Merged Canonical Graph** — Non-destructively merged graph combining new and existing entities; conflict annotations attached where contradictions exist
- **Conflict Metadata** — Analyst-readable notes indicating which entities were added, modified, or conflicting; used by HITL review gate

$2### Internal Processing Interfaces

- **Graph Differ** — Computes semantic diff between new and existing graphs; produces conflict report
- **LLM Request/Response** — Prompts contain both graphs and conflict report; LLM response contains merged graph JSON

## Component Pieces and Parts

$2### Graph Fetcher
Retrieves new canonical graph from orchestrator state (produced by Agent 01); optionally loads existing baseline graph from file system or state storage; validates both graphs are present and schema-compliant before passing to Graph Differ.
$2### Graph Differ
Analyzes differences between new and existing graphs; identifies entity additions (entities in new but not existing), modifications (existing entities with changed properties), and conflicts (contradictory definitions of same entity); produces structured diff report with conflict summary.
$2### LLM Prompt Handler
Constructs Agent 02 system prompt (requesting non-destructive merge with conflict annotation); builds user prompt containing both graphs and diff report; sends request to LLM; handles timeouts and retries.
$2### Merge Engine
Executes merge rules: preserves all existing entities and their IDs; incorporates new entities; for conflicting properties, attaches merge-conflict annotations for analyst decision-making; produces merged graph ready for validation.
$2### Validation Engine
Validates merged graph against canonical schema; checks that all entity IDs remain stable for unchanged entities; detects new schema violations introduced during merge; rejects non-compliant merges with detailed error.
$2### State Emitter
Serializes merged canonical graph and conflict metadata; packages into orchestrator state object with merge timestamp and analyst-actionable conflict notes; hands off to orchestrator for Agent 03 processing.

## Trust Boundaries

**LLM Provider Boundary** — Agent sends both old and new graph definitions to LLM (may contain system architecture details); receives merged graph from external service; must validate response against schema before accepting.

**Storage Boundary** — Existing baseline graph is read from persistent storage (file system); data integrity cannot be assumed; must re-validate schema after retrieval.

## Error Handling

- **Missing New Graph** — Validation error; Agent 01 must successfully complete before Agent 02 starts
- **LLM Timeout** — Retries up to 3 times; if all fail, emits error and halts
- **Merge Produces Invalid Schema** — Validation engine rejects; detailed error indicates schema violations
- **Unresolvable Conflicts** — Merge-conflict annotations attached; marked for HITL analyst review

## Operational Constraints

- **Timeout** — Default 60 seconds per LLM call; configurable
- **Non-Destructive Rule** — No entities ever deleted; conflicts annotated instead of silently resolved
- **ID Stability** — All unchanged entity IDs must remain identical; validation enforces this invariant
- **HITL Gate** — Merge completion can trigger analyst review of conflict annotations (controlled by pipeline configuration)
