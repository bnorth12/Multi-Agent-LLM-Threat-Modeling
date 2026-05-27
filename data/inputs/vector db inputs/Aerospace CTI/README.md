# Aerospace CTI

## Scope

Canonical aerospace cyber threat intelligence corpus for non-conference advisories, backlog tracking, and framework mappings.

## Subfolders

- `advisories/`: curated advisory digests and regulator/security-body synthesis.
- `backlog/`: prioritized source acquisition backlog and intake templates.
- `frameworks/`: framework-specific references and mappings required by ingestion governance.

## Minimum Framework Baseline

- SPARTA must be represented at minimum through `frameworks/sparta_minimum_reference.md`.
- New CTI entries should map to at least one framework element or document why no mapping exists.

## Linkage Requirements

- Every CTI entry should reference capture provenance under `../source_copies/`.
- Threat assertions should include confidence notes and explicit caveats.
