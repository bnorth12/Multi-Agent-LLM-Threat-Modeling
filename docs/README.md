# Docs Directory

This directory contains architecture, agent prompts, schemas, process notes, and supporting references.

Quick index:

- INDEX.md

Subfolder structure:

- architecture
- design
- schemas
- agents
- process
- references

Contents currently include:

- Agent prompt specification files in agents
- Canonical schema references in schemas
- State schema references in schemas
- Architecture artifacts in architecture
- Architecture decomposition package for the application itself, including functional, structural, logical, interface, and requirements mapping views
- Design specifications in design/system and design/software for deployment, runtime orchestration, provider configuration, and future subsystem authorities
- Retrieval references in references

Authoritative schema source:

- schemas/canonical_graph.schema.json

Canonical example payload:

- schemas/canonical_json_schema.txt

Mitigation placement convention:

- mitigation objects are stored under each threat object, not at the data flow root

Notes:

- Agent prompt files are normalized to a common structure for easier parallel implementation.
- Normalization and consolidation should preserve requirement traceability.
- Architecture documents define structural, functional, logical, and interface authority.
- Design documents define implementable subsystem behavior under those architecture authorities.
