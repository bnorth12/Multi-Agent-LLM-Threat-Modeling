# LLM Cyber Threat Modeling with Agents

## 1. Purpose

This project defines a Python-first, multi-agent threat modeling framework that converts architecture descriptions and data-flow tables into auditable security artifacts.

Core outputs per run:

- canonical JSON threat-model graph
- STRIDE scoring with rationale
- concrete threats with taxonomy mapping
- mitigation recommendations with residual risk
- STIX 2.1 bundle
- Mermaid diagrams
- final markdown report

## 2. Architecture Summary

The system uses staged orchestration with shared state and schema-validated handoffs between agents.

High-level flow:

1. Input Normalizer and Graph Builder
1. Hierarchical Context Builder
1. Trust Boundary Validator
1. STRIDE Scorer
1. Concrete Threat Generator
1. STIX Packager
1. Mitigation Generator
1. Diagram Generator
1. Human Report Writer

Human-in-the-loop gates are expected at key decision points including trust boundaries, STRIDE calibration, threat plausibility, mitigation adequacy, and final release.

## 3. Layered Architecture

The system is divided into three clear layers:

### Backend Layer (`src/threat_modeler/backend/`)

Contains all pipeline execution logic and state management with **no dependency on Streamlit**.
This layer is safe to import and use from headless scripts, CI pipelines, and future
LangGraph-based orchestration without any UI framework present.

| Module | Purpose |
|--------|---------|
| `backend/run_manager.py` | Pipeline execution engine; owns `_RUN_REGISTRY`, background threads, orchestrator lifecycle, and HITL gate error handling. Persists run metadata (status, timing, gate, error, settings) to `~/.multi_agent_threat_modeler_runs.json`. |
| `backend/prompt_store.py` | Thread-safe agent prompt store with JSON file backing (`~/.multi_agent_threat_modeler_prompts.json`). Manages per-agent prompt text, version history, and temperature settings. |

Public API of the backend (consumed by UI adapters):

```python
from threat_modeler.backend.run_manager import (
    submit_run, resume_run, cancel_run, wait_for_run,
    get_run_status, is_run_active, any_run_active,
)
from threat_modeler.backend.prompt_store import PromptStore
```

### UI Adapter Layer (`src/threat_modeler/ui/execution.py`)

A thin Streamlit adapter. Delegates all execution logic to the backend while retaining
Streamlit session-state bookkeeping and URL-parameter handling. **No pipeline logic lives here.**

### Streamlit Screens (`src/threat_modeler/ui/screens/`)

Per-screen rendering modules that read backend state projections via the adapter.
Screens are read-only consumers of backend state; they do not own runtime data.

### CLI Entry Point

```bash
# Launch the full application
python -m threat_modeler

# With options
python -m threat_modeler --port 9000 --open-browser
```

The `__main__.py` module delegates to `streamlit run src/threat_modeler/ui/app.py`
so no separate wrapper script is needed.

## 3. Data Contracts

Primary artifacts:

- Canonical graph schema (authoritative): see canonical_graph.schema.json
- Canonical graph example: see canonical_json_schema.txt
- LangGraph state schema: see langgraph_state_schema.txt

HITL framework options:

- see ../../Requirements/09_HITL_Framework_Options.md for deployment options and tradeoffs

All stage outputs should pass schema validation before the next stage executes.

## 4. Knowledge and Retrieval

The framework is designed to support retrieval from curated security and policy corpora, including ATTACK, CAPEC, CWE, NIST, and domain-specific guidance.

Retrieval-enabled stages should include evidence references in outputs.

## 5. Implementation Direction

Implementation focus order:

1. schema and state normalization
1. orchestrator and checkpointing
1. agent contracts and validation middleware
1. HITL flow and audit trail
1. output packaging and report generation

## 6. Documentation Status

This file is a cleaned baseline overview. Detailed requirements and release governance are maintained in the Requirements directory.

Sprint 2026-09 architecture additions are documented in:

- `planning/issues/issue_2026_09_Streamlit_Decoupling_Backend_Engine.md`
- `src/threat_modeler/backend/run_manager.py` (module docstring)
- `src/threat_modeler/backend/prompt_store.py` (module docstring)
