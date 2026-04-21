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
