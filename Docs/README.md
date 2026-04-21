# Docs Directory

This directory contains architecture, agent prompt drafts, schema notes, and supporting design references.

Quick index:

- INDEX.md

Contents currently include:

- Agent prompt specification drafts
- Canonical schema references
- State schema references
- Mermaid architecture diagram source
- Vector database and retrieval design notes

Authoritative schema source:

- canonical_graph.schema.json

Canonical example payload:

- canonical_json_schema.txt

Mitigation placement convention:

- mitigation objects are stored under each threat object, not at the data flow root

Notes:

- Agent prompt files are normalized to a common structure for easier parallel implementation.
- Normalization and consolidation should preserve requirement traceability.
